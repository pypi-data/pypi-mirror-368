"""Command-line interface for startup idea generation."""

import os
import sys
from pathlib import Path
from typing import Optional

import typer
from huggingface_hub import hf_hub_download, model_info
from huggingface_hub.errors import HfHubHTTPError
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .cli_models import app as models_app
from .core.model_service import ModelService
from .core.startup_metadata import StartupLookup
from .data.loader import load_data
from .embed_master import calculate_result, initialize_embeddings
from .idea_generator.generator import StartupIdeaGenerator
from .idea_generator.processors import parse_ideas
from .utils.caching import clear_cache
from .utils.output_formatter import formatter

app = typer.Typer(
    name="rag_startups",
    help="Generate and analyze startup ideas using AI and market data.",
    add_completion=False,
)
console = Console()

# Add model management subcommand
app.add_typer(models_app, name="models")


def validate_token() -> str:
    """Validate HuggingFace token is available."""
    token = os.getenv("HUGGINGFACE_TOKEN")
    if not token:
        console.print(
            "[red]Error:[/red] HUGGINGFACE_TOKEN environment variable not set.\n"
            "Please set it with your HuggingFace API token."
        )
        raise typer.Exit(1)
    # Ensure the token is visible to settings/model manager in this process
    os.environ["HUGGINGFACE_TOKEN"] = token
    # Also set aliases used by huggingface_hub/transformers
    os.environ.setdefault("HUGGINGFACE_HUB_TOKEN", token)
    os.environ.setdefault("HF_TOKEN", token)
    return token


def display_idea(idea_text: str, market_insights: Optional[dict] = None):
    """Display generated idea with optional market insights."""
    # Display the idea
    console.print(Panel(idea_text, title="Generated Startup Idea", expand=False))

    # Display market insights if available
    if market_insights:
        table = Table(
            title="Market Analysis", show_header=True, header_style="bold magenta"
        )
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        for name, insights in market_insights.items():
            table.add_row("Startup Name", name)
            table.add_row("Market Size", f"${insights.market_size:,.2f}B")
            table.add_row("Growth Rate", f"{insights.growth_rate:.1f}%")
            table.add_row("Competition", insights.competition_level)
            table.add_row("Opportunity Score", f"{insights.opportunity_score:.2f}")
            table.add_row("Confidence Score", f"{insights.confidence_score:.2f}")

            if insights.key_trends:
                table.add_row(
                    "Key Trends",
                    "\n".join(f"• {trend}" for trend in insights.key_trends),
                )

            if insights.risk_factors:
                table.add_row(
                    "Risk Factors",
                    "\n".join(f"• {risk}" for risk in insights.risk_factors),
                )

        console.print(table)


@app.command()
def generate_all(
    topic: str = typer.Argument(..., help="Topic or domain for the startup idea"),
    startup_file: str = typer.Option(
        "yc_startups.json",
        "--file",
        "-f",
        help="Path to startup data file (must be provided by user)",
    ),
    num_ideas: int = typer.Option(
        1, "--num-ideas", "-n", help="Number of startup ideas to generate (1-5)"
    ),
    market_analysis: bool = typer.Option(
        True, "--market/--no-market", help="Include market analysis"
    ),
    temperature: float = typer.Option(
        0.7,
        "--temperature",
        "-t",
        help="Model temperature (0.0-1.0). Higher values make output more creative.",
    ),
    print_examples: bool = typer.Option(
        False, "--print-examples", "-p", help="Print startup examples found in file"
    ),
):
    """Generate startup ideas with optional market analysis.

    Each generated startup name includes a unique identifier (e.g., TechStartup-x7y9z).
    Note: Generated names are suggestions only. Users must verify legal availability
    before use. See README.md for more information about name verification.
    """

    # Validate number of ideas
    if not 1 <= num_ideas <= 5:
        console.print("[red]Error:[/red] num_ideas must be between 1 and 5")
        raise typer.Exit(1)
    # Validate startup data file exists
    if not os.path.exists(startup_file):
        console.print(
            f"[red]Error:[/red] Startup data file '{startup_file}' not found.\n"
            "Please provide a valid startup data file using --file option."
        )
        raise typer.Exit(1)

    """Generate startup ideas with optional market analysis."""

    # Validate token
    token = validate_token()

    # Initialize smart model management
    from .config.settings import get_settings

    settings = get_settings()
    model_service = ModelService(settings)

    # Get the best available language model
    language_model = model_service.get_language_model()
    console.print(f"[blue]Using model:[/blue] {language_model.name}", style="dim")
    # Minimal preflight: verify token can access model metadata (detect gated/unauthorized)
    try:
        _ = model_info(language_model.name, token=token)
    except HfHubHTTPError as e:
        status = getattr(e.response, "status_code", None)
        if status in (401, 403):
            console.print(
                "[red]Authorization error:[/red] Your token cannot access the selected model.\n"
                f"Model: {language_model.name}\n"
                "Visit the model page on Hugging Face to request access, or use a token with access."
            )
            raise typer.Exit(1)
    # Get the best available embedding model
    embedding_model = model_service.get_embedding_model()
    console.print(f"[blue]Using embeddings:[/blue] {embedding_model.name}", style="dim")

    question = (
        f"Find innovative startup ideas in {topic}"
        if " " in topic  # If it's a compound phrase like "education technology"
        else f"Find innovative startup ideas in the {topic} domain"
    )

    prompt_messages = [
        (
            "system",
            """
            You are an assistant for question-answering tasks.
            Use the following pieces of retrieved context to answer the question.
            If you don't know the answer, just say that you don't know.
            Use three sentences maximum and keep the answer concise.
            Question: {question}
            Context: {context}
            Answer:""",
        )
    ]

    # Initialize lookup with the JSON data
    df, json_data = load_data(startup_file)  # no max_lines
    lookup = StartupLookup(json_data)

    with console.status("[bold green]Generating startup ideas..."):
        # Find startups in the file relevant to the topic
        example_startups = find_relevant_startups(
            num_ideas,
            question,
            prompt_messages,
            print_examples,
            lookup,
            df,
            json_data,
            embedding_model_name=embedding_model.name,
            language_model_name=language_model.name,
        )
        example_startups_parsed = parse_ideas(example_startups)

        # Use smart model management instead of hardcoded model
        generator = StartupIdeaGenerator(model_name=language_model.name, token=token)
        response, insights = generator.generate(
            num_ideas=num_ideas,
            example_startups=example_startups_parsed,
            temperature=temperature,
            include_market_analysis=market_analysis,
        )

    if response:
        display_idea(response, insights if market_analysis else None)
    else:
        console.print("[red]Failed to generate startup ideas.[/red]")
        raise typer.Exit(1)


def find_relevant_startups(
    num_ideas,
    question,
    prompt_messages,
    print_examples,
    lookup,
    df,
    json_data,
    *,
    embedding_model_name: str,
    language_model_name: str,
):
    """the code to find startups examples here"""

    # Initialize embeddings and retriever once using the selected embedding model
    retriever = initialize_embeddings(df, model_name=embedding_model_name)

    # Pass retriever to calculate_result
    result = calculate_result(
        question=question,
        retriever=retriever,
        json_data=json_data,
        prompt_messages=prompt_messages,
        lookup=lookup,
        num_ideas=num_ideas,
        language_model_name=language_model_name,
    )

    # Print the results in a nicely formatted way

    if print_examples:
        formatter.print_startup_ideas(result)
        formatter.print_summary()

    return result


@app.command()
def analyze(
    idea_name: str = typer.Argument(..., help="Name of the startup to analyze"),
    idea_description: str = typer.Argument(
        ..., help="Brief description of the startup idea"
    ),
    target_market: str = typer.Argument(..., help="Target market for the startup"),
):
    """Analyze market potential for an existing startup idea."""
    token = validate_token()

    with console.status("[bold green]Analyzing market potential..."):
        generator = StartupIdeaGenerator(token=token)
        idea = {
            "name": idea_name,
            "description": idea_description,
            "target_market": target_market,
        }
        _, insights = generator.generate(
            num_ideas=1,
            example_startups=[idea],
            include_market_analysis=True,
        )

    if insights:
        display_idea(
            f"Analysis for: {idea_name}\n\n{idea_description}\nTarget Market: {target_market}",
            insights,
        )
    else:
        console.print("[red]Failed to analyze startup idea.[/red]")
        raise typer.Exit(1)


@app.command()
def clear():
    """Clear cached data and analysis results."""
    try:
        clear_cache()
        console.print("[green]Successfully cleared cache.[/green]")
    except Exception as e:
        console.print(f"[red]Failed to clear cache: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def quickstart(
    no_input: bool = typer.Option(False, help="Run without interactive prompts")
):
    """Interactive wizard to set up the project quickly.

    Steps:
    1. Verify Python version (>= 3.11)
    2. Create/update a `.env` file with HUGGINGFACE_TOKEN.
    3. Download a small language model for immediate use.
    4. Run an example query to verify everything works.
    """

    # 1. Python version check
    if sys.version_info < (3, 11):
        console.print("[red]Python 3.11+ is required to run rag_startups.[/red]")
        raise typer.Exit(1)

    # 2. Obtain token (env var or prompt)
    token = os.getenv("HUGGINGFACE_TOKEN")
    if not token:
        if no_input:
            console.print(
                "[red]HUGGINGFACE_TOKEN is not set. Provide it as an environment variable or run without --no-input for an interactive prompt.[/red]"
            )
            raise typer.Exit(1)
        token = typer.prompt("Enter your HuggingFace API token", hide_input=True)
        os.environ["HUGGINGFACE_TOKEN"] = token

    # Create or update .env file
    env_path = Path(".env")
    if env_path.exists():
        content = env_path.read_text()
        if "HUGGINGFACE_TOKEN" not in content:
            with env_path.open("a", encoding="utf-8") as env_file:
                env_file.write(f"HUGGINGFACE_TOKEN={token}\n")
    else:
        env_path.write_text(f"HUGGINGFACE_TOKEN={token}\n", encoding="utf-8")
    console.print("[green]`.env` file configured.[/green]")

    # 3. Download a small model so the user can start immediately
    console.print(
        "[blue]Downloading example model (sentence-transformers/all-MiniLM-L6-v2)...[/blue]"
    )
    try:
        hf_hub_download(
            repo_id="sentence-transformers/all-MiniLM-L6-v2",
            filename="config.json",
            token=token,
        )
        console.print("[green]Model download complete.[/green]")
    except Exception as exc:  # pragma: no cover — network may fail during CI
        console.print(f"[yellow]Model download skipped: {exc}[/yellow]")

    # 4. Run an example query to verify setup
    try:
        generator = StartupIdeaGenerator(
            model_name="sentence-transformers/all-MiniLM-L6-v2", token=token
        )
        response, _ = generator.generate(
            num_ideas=1,
            example_startups=[],
            include_market_analysis=False,
        )
        console.print(Panel(response, title="Quickstart Example", expand=False))
    except Exception as exc:  # pragma: no cover
        console.print(f"[yellow]Skipping example generation: {exc}[/yellow]")

    console.print("[bold green]Quickstart completed successfully![/bold green]")


if __name__ == "__main__":
    app()
