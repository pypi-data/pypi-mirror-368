"""
Dependency patterns tests.
These tests prepare for dependency injection refactoring.
"""

from unittest.mock import Mock, mock_open, patch

import pandas as pd
import pytest

import src.rag_startups.core.rag_chain as rag_chain_module
from src.rag_startups.core.rag_chain import initialize_rag
from src.rag_startups.core.startup_metadata import StartupLookup
from src.rag_startups.data.loader import initialize_startup_lookup, load_data


class TestDependencyPatterns:
    """Tests to prepare for dependency injection refactoring."""

    @pytest.fixture
    def sample_json_data(self):
        """Sample JSON data for testing."""
        return [
            {
                "name": "TestStartup1",
                "description": "First test startup",
                "industry": "Tech",
                "founded": "2020",
            },
            {
                "name": "TestStartup2",
                "description": "Second test startup",
                "industry": "AI",
                "founded": "2021",
            },
        ]

    @pytest.fixture
    def sample_df(self):
        """Sample DataFrame for testing."""
        return pd.DataFrame(
            {
                "name": ["TestStartup1", "TestStartup2"],
                "description": ["First test startup", "Second test startup"],
                "industry": ["Tech", "AI"],
            }
        )

    def test_startup_lookup_creation_patterns(self, sample_json_data):
        """Test different ways StartupLookup can be created."""
        # Direct instantiation
        lookup1 = StartupLookup(sample_json_data)
        assert lookup1 is not None
        assert lookup1.get_by_name("TestStartup1") is not None

        # Via initialize_startup_lookup function
        lookup2 = initialize_startup_lookup(sample_json_data)
        assert lookup2 is not None
        assert lookup2.get_by_name("TestStartup1") is not None

        # Both should be functionally equivalent
        result1 = lookup1.get_by_name("TestStartup1")
        result2 = lookup2.get_by_name("TestStartup1")
        assert result1["name"] == result2["name"]

    def test_global_state_isolation(self, sample_df, sample_json_data):
        """Test current global state behavior for isolation planning."""
        # Store initial global state - access through module to avoid stale import
        initial_global = rag_chain_module.startup_lookup

        # Initialize RAG (this modifies global state)
        retriever1, lookup1 = initialize_rag(sample_df, sample_json_data)
        global_after_init1 = rag_chain_module.startup_lookup

        # Initialize again with different data
        smaller_data = sample_json_data[:1]
        smaller_df = sample_df.iloc[:1]
        retriever2, lookup2 = initialize_rag(smaller_df, smaller_data)
        global_after_init2 = rag_chain_module.startup_lookup

        # Document current behavior
        assert global_after_init1 is not initial_global
        assert global_after_init2 is not global_after_init1
        assert (
            global_after_init2 == lookup2
        )  # Global should match latest initialization

    def test_dependency_injection_simulation(self, sample_json_data):
        """Simulate how dependency injection would work."""
        # Create multiple independent lookups
        lookup_full = StartupLookup(sample_json_data)
        lookup_partial = StartupLookup(sample_json_data[:1])

        # Test that they can coexist without interfering
        assert lookup_full.get_by_name("TestStartup1") is not None
        assert lookup_full.get_by_name("TestStartup2") is not None

        assert lookup_partial.get_by_name("TestStartup1") is not None
        assert lookup_partial.get_by_name("TestStartup2") is None

        # This demonstrates that dependency injection would work
        # Each component could have its own lookup instance

    def test_data_loader_dependency_patterns(self):
        """Test data loading patterns for dependency injection."""
        # Test that load_data can work with different files
        # (Mock the file system for testing)

        mock_data = [{"name": "MockStartup", "description": "Mock description"}]
        mock_df = pd.DataFrame(mock_data)

        # Mock file operations and pandas read_json
        mock_file_content = mock_df.to_json(orient="records")

        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            with patch("src.rag_startups.data.loader.pd.read_json") as mock_read_json:
                mock_read_json.return_value = mock_df

                # Test that load_data returns both df and json_data
                df, json_data = load_data("mock_file.json")

                assert df is not None
                assert json_data is not None
                assert isinstance(df, pd.DataFrame)
                assert isinstance(json_data, list)

    def test_component_isolation(self, sample_json_data):
        """Test that components can work independently."""
        # Test StartupLookup isolation
        lookup1 = StartupLookup(sample_json_data)
        lookup2 = StartupLookup(sample_json_data)

        # They should be independent instances
        assert lookup1 is not lookup2
        assert id(lookup1) != id(lookup2)

        # But functionally equivalent
        assert (
            lookup1.get_by_name("TestStartup1")["name"]
            == lookup2.get_by_name("TestStartup1")["name"]
        )

    def test_mock_injection_patterns(self, sample_df, sample_json_data):
        """Test patterns for mocking dependencies."""
        # Test that we can mock the startup_lookup dependency
        mock_lookup = Mock(spec=StartupLookup)
        mock_lookup.get_by_description.return_value = {
            "name": "MockedStartup",
            "description": "Mocked description",
        }

        # Test that the mock behaves as expected
        result = mock_lookup.get_by_description("test")
        assert result["name"] == "MockedStartup"

        # This pattern would work for dependency injection
        assert mock_lookup.get_by_description.called

    def test_configuration_dependency_patterns(self):
        """Test configuration dependency patterns."""
        # Test that configuration can be injected
        mock_config = {
            "model_name": "test/model",
            "max_requests_per_hour": 50,
            "temperature": 0.8,
        }

        # This simulates how configuration injection would work
        assert mock_config["model_name"] == "test/model"
        assert mock_config["max_requests_per_hour"] == 50
        assert mock_config["temperature"] == 0.8

        # Components could receive this config object instead of
        # reading from environment variables directly

    def test_service_layer_preparation(self, sample_json_data):
        """Test preparation for service layer pattern."""

        # Simulate a service that encapsulates business logic
        class MockIdeaService:
            def __init__(self, startup_lookup: StartupLookup):
                self.startup_lookup = startup_lookup

            def find_startup(self, name: str):
                return self.startup_lookup.get_by_name(name)

        # Test that service pattern would work
        lookup = StartupLookup(sample_json_data)
        service = MockIdeaService(lookup)

        result = service.find_startup("TestStartup1")
        assert result is not None
        assert result["name"] == "TestStartup1"

        # This demonstrates clean separation of concerns

    def test_factory_pattern_preparation(self, sample_json_data):
        """Test preparation for factory pattern."""

        # Simulate a factory that creates configured objects
        class MockStartupLookupFactory:
            @staticmethod
            def create_lookup(data_source: list) -> StartupLookup:
                return StartupLookup(data_source)

            @staticmethod
            def create_lookup_from_file(filename: str) -> StartupLookup:
                # In real implementation, this would load from file
                return StartupLookup(sample_json_data)

        # Test factory pattern
        factory = MockStartupLookupFactory()
        lookup1 = factory.create_lookup(sample_json_data)
        lookup2 = factory.create_lookup_from_file("test.json")

        assert lookup1 is not None
        assert lookup2 is not None
        assert lookup1.get_by_name("TestStartup1") is not None
        assert lookup2.get_by_name("TestStartup1") is not None

    @patch("src.rag_startups.core.rag_chain.startup_lookup")
    def test_global_state_mocking(self, mock_global_lookup, sample_json_data):
        """Test that global state can be mocked for testing."""
        # Configure the mock
        mock_global_lookup.get_by_description.return_value = {
            "name": "GlobalMockedStartup",
            "description": "Globally mocked description",
        }

        # Test that the mock is used
        from src.rag_startups.core.rag_chain import startup_lookup as imported_lookup

        # The imported lookup should be the mock
        result = imported_lookup.get_by_description("test")
        assert result["name"] == "GlobalMockedStartup"

        # This demonstrates that global state can be controlled in tests
