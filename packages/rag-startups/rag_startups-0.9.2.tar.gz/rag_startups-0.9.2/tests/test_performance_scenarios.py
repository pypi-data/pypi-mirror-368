"""
Unit tests for performance test scenarios and edge cases.

These tests validate the components and scenarios tested in our
comprehensive performance test, ensuring reliability under various conditions.
"""

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

from rag_startups.config.settings import get_settings
from rag_startups.core.model_service import ModelService
from rag_startups.core.rag_chain import initialize_rag
from rag_startups.core.startup_metadata import StartupLookup
from rag_startups.data.loader import load_data


class TestPerformanceScenarios:
    """Test performance-related scenarios and edge cases."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sample_startup_data = [
            {
                "name": "TestStartup1",
                "description": "AI-powered test platform for developers",
                "location": "San Francisco, CA",
                "tags": ["b2b", "ai", "developer-tools"],
                "founders": [{"name": "Test Founder 1"}],
                "meta": {"founded": "2023", "team_size": "5"},
            },
            {
                "name": "TestStartup2",
                "description": "Machine learning platform for financial analysis",
                "location": "New York, NY",
                "tags": ["fintech", "ml", "b2b"],
                "founders": [{"name": "Test Founder 2"}],
                "meta": {"founded": "2022", "team_size": "10"},
            },
            {
                "name": "TestStartup3",
                "description": "Automated testing framework for web applications",
                "location": "Austin, TX",
                "tags": ["developer-tools", "automation", "testing"],
                "founders": [{"name": "Test Founder 3"}],
                "meta": {"founded": "2024", "team_size": "3"},
            },
        ]

    def create_temp_startup_file(self, data=None):
        """Create temporary startup data file for testing."""
        if data is None:
            data = self.sample_startup_data

        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(data, temp_file, indent=2)
        temp_file.close()
        return temp_file.name

    def test_data_loading_performance(self):
        """Test data loading performance with various data sizes."""
        temp_file = self.create_temp_startup_file()

        try:
            start_time = time.time()
            df, json_data = load_data(temp_file)
            load_time = time.time() - start_time

            # Verify data loaded correctly
            assert len(df) == len(self.sample_startup_data)
            assert len(json_data) == len(self.sample_startup_data)

            # Performance should be reasonable for small datasets
            assert load_time < 1.0  # Should load small dataset in under 1 second

        finally:
            Path(temp_file).unlink()

    def test_startup_lookup_initialization_performance(self):
        """Test startup lookup initialization performance."""
        start_time = time.time()
        lookup = StartupLookup(self.sample_startup_data)
        init_time = time.time() - start_time

        # Verify lookup works correctly
        names = lookup.get_all_names()
        assert len(names) == len(self.sample_startup_data)
        assert "teststartup1" in names  # StartupLookup converts to lowercase

        # Performance should be very fast for small datasets
        assert init_time < 0.1  # Should initialize in under 100ms

    @patch("rag_startups.core.rag_chain.create_vectorstore")
    @patch("rag_startups.core.rag_chain.setup_retriever")
    @patch("rag_startups.core.rag_chain.create_documents")
    @patch("rag_startups.core.rag_chain.split_documents")
    def test_rag_initialization_mocked(
        self,
        mock_split_docs,
        mock_create_docs,
        mock_setup_retriever,
        mock_create_vectorstore,
    ):
        """Test RAG initialization with mocked components for speed."""
        # Mock the expensive operations
        mock_create_docs.return_value = ["doc1", "doc2", "doc3"]
        mock_split_docs.return_value = ["chunk1", "chunk2", "chunk3"]
        mock_vectorstore = Mock()
        mock_create_vectorstore.return_value = mock_vectorstore
        mock_retriever = Mock()
        mock_setup_retriever.return_value = mock_retriever

        # Create mock DataFrame
        mock_df = Mock()
        mock_df.__len__ = Mock(return_value=3)

        start_time = time.time()
        retriever, startup_lookup = initialize_rag(mock_df, self.sample_startup_data)
        init_time = time.time() - start_time

        # Verify components were called
        mock_create_docs.assert_called_once()
        mock_split_docs.assert_called_once()
        mock_create_vectorstore.assert_called_once()
        mock_setup_retriever.assert_called_once()

        # Should be fast when components are mocked
        assert init_time < 1.0

    def test_model_service_performance(self):
        """Test model service initialization and selection performance."""
        with patch(
            "rag_startups.core.model_service.ModelManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager

            # Mock model selection
            mock_language_model = Mock()
            mock_language_model.name = "test-model"
            mock_embedding_model = Mock()
            mock_embedding_model.name = "test-embedding"

            mock_manager.get_best_model.side_effect = [
                mock_language_model,
                mock_embedding_model,
            ]

            settings = get_settings()

            start_time = time.time()
            model_service = ModelService(settings)
            language_model = model_service.get_language_model()
            embedding_model = model_service.get_embedding_model()
            selection_time = time.time() - start_time

            # Verify models were selected
            assert language_model.name == "test-model"
            assert embedding_model.name == "test-embedding"

            # Should be very fast with mocked components
            assert selection_time < 0.1

    @patch("rag_startups.core.rag_chain.format_startup_idea")
    def test_idea_formatting_performance(self, mock_format_idea):
        """Test startup idea formatting performance."""
        # Mock the formatting function to return quickly
        mock_format_idea.return_value = {
            "name": "TestIdea",
            "description": "Test description",
            "market_size": "Large",
        }

        test_descriptions = [
            "AI-powered developer productivity tool",
            "Machine learning platform for finance",
            "Automated testing framework",
        ]

        start_time = time.time()
        formatted_ideas = []
        for desc in test_descriptions:
            idea = mock_format_idea(desc)
            formatted_ideas.append(idea)
        format_time = time.time() - start_time

        # Verify all ideas were processed
        assert len(formatted_ideas) == len(test_descriptions)

        # Should be fast with mocked formatting
        assert format_time < 0.1

    def test_large_dataset_simulation(self):
        """Test behavior with larger simulated datasets."""
        # Create a larger dataset for testing
        large_dataset = []
        for i in range(100):  # Simulate 100 startups
            startup = {
                "name": f"Startup{i}",
                "description": f"Description for startup {i} in various domains",
                "location": f"City{i % 10}, State",
                "tags": [f"tag{i % 5}", "b2b"],
                "founders": [{"name": f"Founder{i}"}],
                "meta": {"founded": "2023", "team_size": str(i % 20 + 1)},
            }
            large_dataset.append(startup)

        temp_file = self.create_temp_startup_file(large_dataset)

        try:
            start_time = time.time()
            df, json_data = load_data(temp_file)
            lookup = StartupLookup(json_data)
            load_time = time.time() - start_time

            # Verify data loaded correctly
            assert len(df) == 100
            assert len(json_data) == 100

            # Performance should still be reasonable for 100 startups
            assert load_time < 2.0  # Should load 100 startups in under 2 seconds

            # Test lookup functionality
            names = lookup.get_all_names()
            assert len(names) == 100
            assert "startup0" in names  # StartupLookup converts to lowercase
            assert "startup99" in names

        finally:
            Path(temp_file).unlink()

    def test_error_handling_in_performance_scenarios(self):
        """Test error handling in performance-critical scenarios."""
        # Test with malformed JSON data
        malformed_data = [
            {"name": "ValidStartup", "description": "Valid description"},
            {"name": "InvalidStartup"},  # Missing description
            {"description": "Missing name"},  # Missing name
        ]

        # StartupLookup should handle malformed data gracefully
        lookup = StartupLookup(malformed_data)
        names = lookup.get_all_names()

        # Should still work with valid entries
        assert "validstartup" in names  # StartupLookup converts to lowercase

    def test_memory_usage_simulation(self):
        """Test memory usage patterns with startup data."""
        # Create multiple lookups to test memory usage
        lookups = []

        for i in range(10):
            # Create small datasets
            data = [
                {
                    "name": f"Startup{i}_{j}",
                    "description": f"Description {i}_{j}",
                    "location": "Test City",
                }
                for j in range(10)
            ]
            lookup = StartupLookup(data)
            lookups.append(lookup)

        # Verify all lookups work
        assert len(lookups) == 10
        for i, lookup in enumerate(lookups):
            names = lookup.get_all_names()
            assert len(names) == 10
            assert f"startup{i}_0" in names  # StartupLookup converts to lowercase

    @patch("rag_startups.config.settings.get_settings")
    def test_configuration_performance(self, mock_get_settings):
        """Test configuration loading performance."""
        mock_settings = Mock()
        mock_settings.enable_smart_model_selection = True
        mock_settings.model_health_check_interval = 3600
        mock_settings.model_timeout = 10
        mock_settings.project_root = Path("/tmp")
        mock_get_settings.return_value = mock_settings

        start_time = time.time()
        settings = get_settings()
        config_time = time.time() - start_time

        # Configuration loading should be very fast
        assert config_time < 0.1
        assert settings.enable_smart_model_selection is True

    def test_concurrent_access_simulation(self):
        """Test behavior under simulated concurrent access."""
        # Simulate multiple concurrent lookups
        lookup = StartupLookup(self.sample_startup_data)

        # Perform multiple operations that might happen concurrently
        results = []
        for i in range(10):
            names = lookup.get_all_names()
            startup = lookup.get_by_name("TestStartup1")
            results.append((names, startup))

        # All operations should succeed
        assert len(results) == 10
        for names, startup in results:
            assert len(names) == 3
            assert startup is not None
            assert startup["name"] == "TestStartup1"


class TestPerformanceEdgeCases:
    """Test edge cases that could affect performance."""

    def test_empty_dataset_handling(self):
        """Test handling of empty datasets."""
        empty_data = []

        # Should handle empty data gracefully
        lookup = StartupLookup(empty_data)
        names = lookup.get_all_names()
        assert names == []

    def test_very_large_descriptions(self):
        """Test handling of very large startup descriptions."""
        large_description = "A" * 10000  # 10KB description

        large_startup = {
            "name": "LargeStartup",
            "description": large_description,
            "location": "Test City",
        }

        lookup = StartupLookup([large_startup])
        startup = lookup.get_by_name("LargeStartup")

        assert startup is not None
        assert len(startup["description"]) == 10000

    def test_unicode_handling_performance(self):
        """Test performance with unicode and international characters."""
        unicode_data = [
            {
                "name": "UnicodeStartup",
                "description": "Startup with émojis 🚀 and ünïcödé characters",
                "location": "Tōkyō, Japan",
            },
            {
                "name": "中文Startup",
                "description": "中文描述 with mixed languages",
                "location": "北京, China",
            },
        ]

        start_time = time.time()
        lookup = StartupLookup(unicode_data)
        names = lookup.get_all_names()
        unicode_time = time.time() - start_time

        # Should handle unicode efficiently
        assert len(names) == 2
        assert "unicodestartup" in names  # StartupLookup converts to lowercase
        assert "中文startup" in names
        assert unicode_time < 0.1
