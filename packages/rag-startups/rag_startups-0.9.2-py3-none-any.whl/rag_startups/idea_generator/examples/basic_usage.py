"""
Example usage of the StartupIdeaGenerator.
"""

from dotenv import load_dotenv

from rag_startups.idea_generator.generator import StartupIdeaGenerator


def main():
    # Load environment variables (including HUGGINGFACE_TOKEN)
    load_dotenv()

    # Create generator instance
    generator = StartupIdeaGenerator(
        max_requests_per_hour=10  # Conservative limit for testing
    )

    # Example startup for context
    example_startups = [
        {
            "name": "TechFlow",
            "problem": "Small businesses struggle with workflow automation",
            "solution": "AI-powered workflow automation platform",
            "target_market": "Small to medium businesses",
            "unique_value": [
                "Easy to use interface",
                "Affordable pricing",
                "Custom automation rules",
            ],
        }
    ]

    try:
        # Generate ideas
        print("Generating startup ideas...")
        ideas = generator.generate(
            num_ideas=2, example_startups=example_startups, temperature=0.7
        )

        if ideas:
            print("\nGenerated Ideas:")
            print(ideas)
        else:
            print("No ideas generated")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
