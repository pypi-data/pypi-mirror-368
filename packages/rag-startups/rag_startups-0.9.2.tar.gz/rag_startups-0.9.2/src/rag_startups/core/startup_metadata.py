"""Startup metadata handling module for efficient startup data lookups."""

from typing import Dict, List, Optional


class StartupLookup:
    """A class to handle efficient startup metadata lookups and management.

    This class provides fast lookup capabilities for startup data using various
    search criteria like name and description. It maintains an internal index
    for quick access to startup information.

    Attributes:
        startup_data (List[Dict]): List of startup dictionaries containing metadata
        _name_to_data (Dict[str, Dict]): Internal index mapping lowercase names to startup data
    """

    def __init__(self, startup_data: List[Dict]):
        """Initialize the StartupLookup with startup data.

        Args:
            startup_data (List[Dict]): List of dictionaries containing startup metadata.
                Each dictionary should have at least a 'name' key.
        """
        self.startup_data = startup_data
        self._name_to_data = {
            startup["name"].lower(): startup
            for startup in startup_data
            if "name" in startup
        }

    def get_by_name(self, name: str) -> Optional[Dict]:
        """Retrieve startup data by company name.

        Args:
            name (str): The name of the startup to look up

        Returns:
            Optional[Dict]: The startup's metadata dictionary if found, None otherwise

        Example:
            >>> lookup = StartupLookup(startup_data)
            >>> startup = lookup.get_by_name("OpenAI")
            >>> print(startup["category"])
            "AI/ML"
        """
        return self._name_to_data.get(name.lower())

    def get_all_names(self) -> List[str]:
        """Get a list of all startup names in the database.

        Returns:
            List[str]: List of all startup names in lowercase

        Example:
            >>> lookup = StartupLookup(startup_data)
            >>> names = lookup.get_all_names()
            >>> print(len(names))
            42
        """
        return list(self._name_to_data.keys())

    def get_by_description(self, description: str) -> Optional[Dict]:
        """Find startup data by matching a description.

        This method searches through startup descriptions to find the best match
        for the given description text.

        Args:
            description (str): The description text to match against

        Returns:
            Optional[Dict]: The best matching startup's metadata if found, None otherwise

        Example:
            >>> lookup = StartupLookup(startup_data)
            >>> startup = lookup.get_by_description("AI company focusing on language models")
            >>> print(startup["name"])
            "OpenAI"
        """
        if not description:
            return None

        description = description.lower()
        for startup in self.startup_data:
            if startup.get("long_desc", "").lower() == description:
                return startup
        return None
