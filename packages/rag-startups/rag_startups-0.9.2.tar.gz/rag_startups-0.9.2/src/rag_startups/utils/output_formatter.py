import logging
from typing import Dict, Set


class OutputFormatter:
    def __init__(self):
        self.timings: Dict[str, float] = {}
        self.nested_ops: Set[str] = {
            "initialize_embeddings",
            "create_and_split_document",
        }

    def add_timing(self, operation: str, duration: float):
        """Add timing information for an operation."""
        self.timings[operation] = duration
        # Also log it for backward compatibility
        logging.info(f"{operation} took {duration:.2f} seconds")

    def print_summary(self):
        """Print a summary of all timing information."""
        if not self.timings:
            return

        print("\n🕒 Performance Summary:")
        print("=" * 50)

        # Define timing categories and their operations
        categories = {
            "Data Loading": ["load_data", "create_documents", "split_documents"],
            "Embedding Process": ["embed", "setup_retriever"],
            "Generation": [
                "rag_chain_local",
                "calculate_result",
                "format_startup_idea",
            ],
        }

        total_time = 0
        for category, operations in categories.items():
            category_time = 0
            category_printed = False

            for op in operations:
                if op in self.timings:
                    if not category_printed:
                        print(f"\n{category}:")
                        category_printed = True

                    duration = self.timings[op]
                    if (
                        op not in self.nested_ops
                    ):  # Only add to total if not a nested operation
                        category_time += duration
                        total_time += duration
                    print(f"  • {op}: {duration:.2f}s")

            # Add nested operations at the end of their category
            if (
                category == "Data Loading"
                and "create_and_split_document" in self.timings
            ):
                print(
                    f"  • create_and_split_document: {self.timings['create_and_split_document']:.2f}s (combined)"
                )
            elif (
                category == "Embedding Process"
                and "initialize_embeddings" in self.timings
            ):
                print(
                    f"  • initialize_embeddings: {self.timings['initialize_embeddings']:.2f}s (combined)"
                )

            if category_printed:
                print(f"  Total {category} Time: {category_time:.2f}s")

        print("-" * 50)
        print(f"Total Processing Time: {total_time:.2f}s")
        print("=" * 50)

    @staticmethod
    def print_startup_ideas(ideas: str):
        """Print formatted startup ideas."""
        print("\n🚀 Generated Startup Ideas")
        print("=" * 50)

        # Remove the generic intro text
        ideas = ideas.replace(
            "Here are the most relevant startup ideas from YC companies:\n", ""
        )

        # Split and format each idea
        ideas_list = ideas.split("==================================================")
        for idea in ideas_list:
            if idea.strip():
                print(idea.strip())
                print("=" * 50)


# Global formatter instance
formatter = OutputFormatter()
