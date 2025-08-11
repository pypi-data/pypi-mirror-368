"""
Prompt templates for startup idea generation.
"""

from typing import List


def generate_base_prompt(num_ideas: int, example_startups: List[dict] = None) -> str:
    """
    Generate the base prompt for startup idea generation.

    Args:
        num_ideas: Number of startup ideas to generate
        example_startups: Optional list of example startups from our database

    Returns:
        Formatted prompt string
    """
    # Default examples if none provided
    if not example_startups:
        example_startups = [
            {
                "name": "Fragment",
                "problem": (
                    "Fragment's premise is that every company using AI will need "
                    "humans in the loop and software for the handoff between AI and humans."
                ),
                "solution": (
                    "We start by helping operations teams in fintech companies "
                    "with task management for their manual processes (onboarding, compliance…)."
                ),
                "target_market": "the handoff between ai and humans.",
                "unique_value": [
                    (
                        "We start by helping operations teams in fintech companies "
                        "with task management for their manual processes (onboarding, compliance…)"
                    )
                ],
            },
            # Add more default examples here
        ]

    # Format examples into prompt
    examples = ""
    for i, startup in enumerate(example_startups, 1):
        examples += f"""
Startup Idea #{i}:
Name: {startup['name']}
Problem/Opportunity: {startup['problem']}
Solution: {startup['solution']}
Target Market: {startup['target_market']}
Unique Value:
"""
        if isinstance(startup["unique_value"], list):
            for point in startup["unique_value"]:
                examples += f"• {point}\n"
        else:
            examples += f"• {startup['unique_value']}\n"

    return f"""Generate {num_ideas} new startup ideas, without existing companies working on them yet, based on the following existing startup descriptions:
{examples}
IMPORTANT FORMATTING INSTRUCTIONS:
1. Do NOT use any separators (no ---, no ___, no ***) between ideas
2. Do NOT use any markdown formatting
3. Do NOT repeat back the examples or these instructions
4. Start DIRECTLY with "Startup Idea #1:" and your first idea
5. Just list ideas one after another with a single line break between them
6. Use this EXACT format for each idea:

Startup Idea #[number]:
Name: [company name]
Problem/Opportunity: [clear problem statement]
Solution: [detailed solution description]
Target Market: [specific target market]
Unique Value:
• [bullet point 1]
• [bullet point 2]
• [bullet point 3]

Requirements for each idea:
1. Fill gaps in the market
2. Build upon insights from the existing startups
3. Are unique and not currently being pursued
4. Have clear problem/solution statements
5. Must include ALL sections
6. Use bullet points (•) for Unique Value items

BEGIN YOUR RESPONSE NOW:"""
