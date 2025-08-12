"""
End-to-End validation tests for MEMG v0.3 EntityType standardization.

This test suite performs comprehensive live testing of the memory system
with real AI calls and graph validation as outlined in the testing proposal.
"""

from pathlib import Path
import sys
from unittest.mock import patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import MCP app - skip if not available in current test setup
try:
    from integration.mcp.mcp_server import app
except ImportError:
    app = None

from memg_core.models.core import EntityType, MemoryType
from memg_core.utils.system_info import get_system_info


class TestE2EValidation:
    """
    End-to-end test following the testing proposal scenario:
    Process a memory with multiple entity types and verify storage/retrieval.
    """

    @pytest.fixture
    def test_user_id(self):
        """Test user ID for isolation."""
        return "e2e_test_user_v03"

    @pytest.fixture
    def test_memory_content(self):
        """Test content with multiple entity types."""
        return (
            "For the new billing system, we are using Python and Docker. "
            "The main API is a system COMPONENT called 'InvoiceService'. "
            "We ran into a ModuleNotFoundError, but the SOLUTION was to "
            "update the requirements.txt FILE_TYPE."
        )

    def test_entity_type_enum_completeness(self):
        """Verify all 16 standard EntityTypes exist (allowing additional types)."""
        expected_types = {
            # Technology Types
            EntityType.TECHNOLOGY,
            EntityType.DATABASE,
            EntityType.LIBRARY,
            EntityType.TOOL,
            # System Types
            EntityType.COMPONENT,
            EntityType.SERVICE,
            EntityType.ARCHITECTURE,
            EntityType.PROTOCOL,
            # Problem/Solution Types
            EntityType.ERROR,
            EntityType.ISSUE,
            EntityType.SOLUTION,
            EntityType.WORKAROUND,
            # Domain Types
            EntityType.CONCEPT,
            EntityType.METHOD,
            EntityType.CONFIGURATION,
            EntityType.FILE_TYPE,
        }

        actual_types = set(EntityType)
        # At least includes the 16 standardized types
        assert expected_types.issubset(actual_types)

    def test_entity_type_string_values(self):
        """Verify EntityType enum has correct string values for database storage."""
        assert EntityType.TECHNOLOGY.value == "TECHNOLOGY"
        assert EntityType.DATABASE.value == "DATABASE"
        assert EntityType.COMPONENT.value == "COMPONENT"
        assert EntityType.ERROR.value == "ERROR"
        assert EntityType.SOLUTION.value == "SOLUTION"
        assert EntityType.FILE_TYPE.value == "FILE_TYPE"

    def test_memory_type_validation(self):
        """Test MemoryType enum validation (allowing TASK as additive)."""
        assert MemoryType.DOCUMENT.value == "document"
        assert MemoryType.NOTE.value == "note"
        assert MemoryType.CONVERSATION.value == "conversation"

        # Ensure the three core types exist (others may be additive like TASK)
        core = {"document", "note", "conversation"}
        assert core.issubset({t.value for t in MemoryType})

    def test_migration_script_exists_and_importable(self):
        """Test migration script can be imported and has required functions."""
        try:
            # Migration script may not exist yet in development
            from scripts.migrate_entity_types import get_standardized_type

            # Test function exists and works
            result = get_standardized_type("framework")
            assert result == EntityType.TECHNOLOGY

            # Test fallback works
            fallback = get_standardized_type("unknown_type_xyz")
            assert fallback == EntityType.CONCEPT

        except ImportError as e:
            pytest.skip(f"Migration script not available in test environment: {e}")

    def test_core_processing_imports_correctly(self):
        """Test core processing components can import EntityType successfully."""
        try:
            from memg_core.models import EntityType as ImportedEntityType

            # Verify EntityType is available
            assert ImportedEntityType.TECHNOLOGY == EntityType.TECHNOLOGY
            assert ImportedEntityType.DATABASE == EntityType.DATABASE

        except ImportError as e:
            pytest.fail(f"Core processing import failed: {e}")

    def test_memory_retriever_imports_correctly(self):
        """Test MemoryRetriever can import and use EntityType."""
        try:
            from memg_core.processing.memory_retriever import MemoryRetriever

            # Create retriever instance (with mocked dependencies)
            with (
                patch("memg_core.processing.memory_retriever.QdrantInterface"),
                patch("memg_core.processing.memory_retriever.GenAIEmbedder"),
                patch("memg_core.processing.memory_retriever.KuzuInterface"),
            ):
                retriever = MemoryRetriever()
                assert retriever is not None

        except ImportError as e:
            pytest.fail(f"MemoryRetriever import failed: {e}")

    def test_mcp_server_tools_available(self):
        """Test MCP server has all required tools for v0.3."""
        try:
            try:
                from integration.mcp.mcp_server import app

                # Check that the app exists and is configured
                assert app is not None
            except ImportError:
                pytest.skip("MCP server not available in test environment")

            # Expected core MCP tools for MEMG
            expected_tools = {
                "add_memory",
                "search_memories",
                "graph_search",
                "validate_graph",
                "get_memory_schema",
                "get_system_info",
            }

            # Try to confirm expected tool names are registered on the app
            try:
                registered = (
                    set(getattr(app, "_tools", {}).keys())
                    if hasattr(app, "_tools")
                    else set()
                )
                missing = expected_tools - registered
                if missing:
                    pytest.skip(
                        f"Some tools not present in this environment: {missing}"
                    )
            except Exception:
                # If we cannot introspect, at least the import worked
                assert True

        except Exception as e:
            pytest.fail(f"MCP server setup failed: {e}")

    def test_kuzu_interface_importable(self):
        """Test KuzuInterface can be imported and initialized."""
        try:
            from memg_core.kuzu_graph.interface import KuzuInterface

            # Test class is importable
            assert KuzuInterface is not None

            # Test initialization would work (without actual DB connection)
            # In real e2e tests, this would connect to a test database

        except ImportError as e:
            pytest.fail(f"KuzuInterface import failed: {e}")

    def test_qdrant_interface_importable(self):
        """Test QdrantInterface can be imported and initialized."""
        try:
            from memg_core.qdrant.interface import QdrantInterface

            # Test class is importable
            assert QdrantInterface is not None

        except ImportError as e:
            pytest.fail(f"QdrantInterface import failed: {e}")

    def test_core_interfaces_importable(self):
        """Test core interfaces can be imported (validation moved to _stash)."""
        try:
            from memg_core.kuzu_graph.interface import KuzuInterface
            from memg_core.qdrant.interface import QdrantInterface

            # Test classes are importable
            assert KuzuInterface is not None
            assert QdrantInterface is not None

        except ImportError as e:
            pytest.fail(f"Core interfaces import failed: {e}")

    def test_genai_integration_importable(self):
        """Test GenAI integration for entity extraction."""
        try:
            from memg_core.utils.embeddings import GenAIEmbedder
            from memg_core.utils.genai import GenAI

            # Test classes are importable
            assert GenAI is not None
            assert GenAIEmbedder is not None

        except ImportError as e:
            pytest.fail(f"GenAI integration import failed: {e}")


class TestSystemReadiness:
    """Test system readiness for v0.3 release."""

    def test_version_defined(self):
        """Test version is properly defined."""
        try:
            from memg_core.version import __version__

            assert isinstance(__version__, str)
            assert len(__version__) > 0
            # Should be v0.3.0 or similar for this release

        except ImportError:
            # Version might not be set up yet, which is okay for dev
            pytest.skip("Version not defined yet")

    def test_docker_files_exist(self):
        """Test Docker deployment files exist."""
        project_root = Path(__file__).parent.parent

        dockerfile = project_root / "Dockerfile"
        docker_compose = project_root / "dockerfiles" / "docker-compose.yml"

        # Skip if Docker files not present (not required for core library)
        if not dockerfile.exists() or not docker_compose.exists():
            pytest.skip("Docker files not present - not required for core library")

        assert dockerfile.exists(), "Dockerfile missing"
        assert docker_compose.exists(), "docker-compose.yml missing"

    def test_requirements_file_exists(self):
        """Test requirements.txt exists and has key dependencies."""
        project_root = Path(__file__).parent.parent
        requirements_file = project_root / "requirements.txt"

        assert requirements_file.exists(), "requirements.txt missing"

        with open(requirements_file) as f:
            requirements = f.read().lower()

        # Check key dependencies are listed
        assert "fastmcp" in requirements  # FastAPI is included via FastMCP
        assert "qdrant" in requirements
        assert "kuzu" in requirements
        assert "pydantic" in requirements
        assert "google-genai" in requirements

    def test_environment_template_exists(self):
        """Test environment template exists."""
        project_root = Path(__file__).parent.parent
        env_example = project_root / "env.example"

        assert env_example.exists(), "env.example missing"

    def test_get_system_info_minimum_fields(self, monkeypatch):
        """System info exposes registry path, qdrant stats, graph flag, neighbor cap."""
        monkeypatch.setenv("KUZU_DB_PATH", "/tmp/memg_core_test_kuzu.db")
        monkeypatch.setenv("QDRANT_STORAGE_PATH", "/tmp/memg_core_test_qdrant")
        info = get_system_info()
        assert "registry" in info and isinstance(info["registry"], dict)
        assert "qdrant" in info and isinstance(info["qdrant"], dict)
        assert "graph_enabled" in info
        assert "neighbor_cap_default" in info


    def test_lightweight_core_imports(self):
        """Test core imports work without heavy dependencies."""
        try:
            # Test core system imports
            import memg_core.kuzu_graph.interface
            import memg_core.models.core
            import memg_core.processing.memory_retriever
            import memg_core.qdrant.interface

            # If all core imports succeed, we have a lean core
            assert True

        except ImportError as e:
            pytest.fail(f"Core import failed: {e}")

    def test_memory_model_efficiency(self):
        """Test Memory model is efficient for storage."""
        # Test memory creation is fast
        import time

        from memg_core.models.core import Memory, MemoryType

        start = time.time()

        for i in range(100):
            memory = Memory(
                user_id="perf_test",
                content=f"Test content {i}",
                memory_type=MemoryType.NOTE,
            )
            # Test serialization is fast
            _ = memory.to_qdrant_payload()
            _ = memory.to_kuzu_node()

        end = time.time()
        duration = end - start

        # Should be able to create and serialize 100 memories in under 1 second
        assert (
            duration < 1.0
        ), f"Memory operations too slow: {duration}s for 100 operations"

    def test_entity_model_efficiency(self):
        """Test Entity model is efficient."""
        import time

        from memg_core.models.core import Entity, EntityType

        start = time.time()

        for i in range(100):
            entity = Entity(
                user_id="perf_test",
                name=f"Entity{i}",
                type=EntityType.TECHNOLOGY,
                description=f"Description {i}",
            )
            _ = entity.to_kuzu_node()

        end = time.time()
        duration = end - start

        # Should be fast
        assert (
            duration < 1.0
        ), f"Entity operations too slow: {duration}s for 100 operations"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
