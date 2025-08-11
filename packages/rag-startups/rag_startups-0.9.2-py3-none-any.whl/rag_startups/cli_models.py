"""
CLI commands for model management and health checking.
"""

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .config.settings import get_settings
from .core.model_manager import ModelType
from .core.model_service import ModelService

app = typer.Typer(name="models", help="Model management commands")
console = Console()


@app.command()
def status(
    model_name: Optional[str] = typer.Argument(None, help="Specific model to check"),
    refresh: bool = typer.Option(
        False, "--refresh", "-r", help="Force refresh model health"
    ),
):
    """Check model health status."""
    settings = get_settings()
    model_service = ModelService(settings)

    if refresh:
        console.print("🔄 Refreshing model health status...", style="yellow")
        health_info = model_service.refresh_model_health()
    else:
        health_info = model_service.check_model_health(model_name)

    if model_name:
        # Single model status
        status_color = "green" if health_info["healthy"] else "red"
        status_icon = "✅" if health_info["healthy"] else "❌"

        panel = Panel(
            f"{status_icon} Model: [bold]{health_info['model']}[/bold]\n"
            f"Status: [{status_color}]{health_info['status']}[/{status_color}]\n"
            f"Healthy: [{status_color}]{health_info['healthy']}[/{status_color}]",
            title="Model Status",
            border_style=status_color,
        )
        console.print(panel)
    else:
        # Overall system status
        overall_color = "green" if health_info["overall_healthy"] else "red"
        overall_icon = "✅" if health_info["overall_healthy"] else "❌"

        # Language model status
        lang_info = health_info["language_model"]
        lang_color = "green" if lang_info["healthy"] else "red"
        lang_icon = "✅" if lang_info["healthy"] else "❌"

        # Embedding model status
        embed_info = health_info["embedding_model"]
        embed_color = "green" if embed_info["healthy"] else "red"
        embed_icon = "✅" if embed_info["healthy"] else "❌"

        panel = Panel(
            f"{overall_icon} [bold]Overall System Health: "
            f"[{overall_color}]{'HEALTHY' if health_info['overall_healthy'] else 'UNHEALTHY'}[/{overall_color}][/bold]\n\n"
            f"{lang_icon} [bold]Language Model[/bold]\n"
            f"   Name: {lang_info['name']}\n"
            f"   Status: [{lang_color}]{lang_info['status']}[/{lang_color}]\n\n"
            f"{embed_icon} [bold]Embedding Model[/bold]\n"
            f"   Name: {embed_info['name']}\n"
            f"   Status: [{embed_color}]{embed_info['status']}[/{embed_color}]",
            title="RAG System Model Status",
            border_style=overall_color,
        )
        console.print(panel)


@app.command()
def list(
    model_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Filter by model type (language|embedding)"
    )
):
    """List all available models."""
    settings = get_settings()
    model_service = ModelService(settings)

    # Convert string to ModelType if provided
    type_filter = None
    if model_type:
        if model_type.lower() == "language":
            type_filter = ModelType.LANGUAGE_GENERATION
        elif model_type.lower() == "embedding":
            type_filter = ModelType.EMBEDDING
        else:
            console.print(
                f"❌ Invalid model type: {model_type}. Use 'language' or 'embedding'",
                style="red",
            )
            raise typer.Exit(1)

    models = model_service.list_available_models(type_filter)

    if not models:
        console.print("No models found.", style="yellow")
        return

    # Create table
    table = Table(title="Available Models")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("Provider", style="blue")
    table.add_column("Priority", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Healthy", justify="center")

    for model in models:
        status_color = "green" if model["is_healthy"] else "red"
        status_icon = "✅" if model["is_healthy"] else "❌"

        table.add_row(
            model["name"],
            model["model_type"].value.replace("-", " ").title(),
            model["provider"],
            str(model["fallback_priority"]),
            f"[{status_color}]{model['current_status']}[/{status_color}]",
            status_icon,
        )

    console.print(table)


@app.command()
def test(
    force: bool = typer.Option(
        False, "--force", "-f", help="Force test even if models appear unhealthy"
    )
):
    """Test model functionality with sample data."""
    settings = get_settings()
    model_service = ModelService(settings)

    console.print("🧪 Testing model functionality...", style="yellow")

    # Check health first
    health_info = model_service.check_model_health()

    if not health_info["overall_healthy"] and not force:
        console.print(
            "❌ Models are not healthy. Use --force to test anyway.", style="red"
        )
        console.print("Run 'rag-startups models status' for details.", style="blue")
        raise typer.Exit(1)

    # Test embedding model
    console.print("\n📊 Testing embedding model...", style="blue")
    try:
        embedding_model = model_service.get_embedding_model()
        sentence_transformer = model_service.create_sentence_transformer(
            embedding_model
        )

        test_text = "This is a test sentence for embedding."
        embeddings = sentence_transformer.encode([test_text])

        console.print(
            f"✅ Embedding model working: {embedding_model.name}", style="green"
        )
        console.print(f"   Generated embedding shape: {embeddings.shape}", style="dim")

    except Exception as e:
        console.print(f"❌ Embedding model test failed: {e}", style="red")

    # Test language model
    console.print("\n🤖 Testing language model...", style="blue")
    try:
        language_model = model_service.get_language_model()

        if language_model.provider == "huggingface":
            hf_client = model_service.create_huggingface_client(language_model)

            test_prompt = "Generate a brief startup idea:"
            # Get model parameters but use simplified test parameters
            model_service.get_model_parameters(language_model)

            # Limit parameters for test
            test_params = {"max_new_tokens": 50, "temperature": 0.7, "do_sample": True}

            console.print(f"   Testing with prompt: '{test_prompt}'", style="dim")
            response = hf_client.text_generation(test_prompt, **test_params)

            console.print(
                f"✅ Language model working: {language_model.name}", style="green"
            )
            console.print(f"   Sample response: {response[:100]}...", style="dim")

        else:
            console.print(
                f"⚠️  Language model test skipped for provider: {language_model.provider}",
                style="yellow",
            )

    except Exception as e:
        console.print(f"❌ Language model test failed: {e}", style="red")
        if "404" in str(e):
            console.print(
                "   This model may no longer be available on HuggingFace",
                style="yellow",
            )
            console.print(
                "   The system will automatically try fallback models", style="blue"
            )

    console.print("\n🎯 Test complete!", style="green")


@app.command()
def add(
    name: str = typer.Argument(..., help="Model name"),
    model_type: str = typer.Option(
        ..., "--type", "-t", help="Model type (language|embedding)"
    ),
    provider: str = typer.Option(
        "huggingface", "--provider", "-p", help="Model provider"
    ),
    priority: int = typer.Option(
        50, "--priority", help="Fallback priority (lower = higher priority)"
    ),
):
    """Add a custom model configuration."""
    settings = get_settings()
    model_service = ModelService(settings)

    # Convert string to ModelType
    if model_type.lower() == "language":
        type_enum = ModelType.LANGUAGE_GENERATION
    elif model_type.lower() == "embedding":
        type_enum = ModelType.EMBEDDING
    else:
        console.print(
            f"❌ Invalid model type: {model_type}. Use 'language' or 'embedding'",
            style="red",
        )
        raise typer.Exit(1)

    success = model_service.add_custom_model(
        name=name, model_type=type_enum, provider=provider, priority=priority
    )

    if success:
        console.print(f"✅ Added model: {name}", style="green")

        # Test the new model
        console.print("🔄 Testing new model...", style="yellow")
        health_info = model_service.check_model_health(name)

        if health_info["healthy"]:
            console.print("✅ Model is healthy and ready to use", style="green")
        else:
            console.print(
                f"⚠️  Model added but appears unhealthy: {health_info['status']}",
                style="yellow",
            )
    else:
        console.print(f"❌ Failed to add model: {name}", style="red")


if __name__ == "__main__":
    app()
