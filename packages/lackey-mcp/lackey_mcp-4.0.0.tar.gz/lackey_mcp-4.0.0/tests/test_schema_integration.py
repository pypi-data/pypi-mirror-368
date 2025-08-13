"""Integration tests for schema-focused MCP tools.

Tests verify that all three tools (lackey_schema, lackey_suggest, lackey_validate)
maintain clean separation from data operations and provide pure schema introspection.
"""

from unittest.mock import Mock, patch

import pytest

from src.lackey.mcp.gateways.lackey_schema import LackeySchemaGateway
from src.lackey.mcp.lackey_suggest import lackey_suggest
from src.lackey.mcp.lackey_validate import lackey_validate


class TestSchemaIntegration:
    """Test integration of all schema-focused MCP tools."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.gateway = LackeySchemaGateway()

    @pytest.mark.asyncio
    async def test_lackey_schema_tool_pure_introspection(self) -> None:
        """Test lackey_schema tool provides pure schema introspection."""
        # Test gateway schema retrieval
        result = await self.gateway.get_gateway_schema("lackey_get", "tier2")

        assert result["gateway"] == "lackey_get"
        assert result["disclosure_level"] == "tier2"
        assert "tools" in result
        assert result["tool_count"] > 0

        # Verify no data contamination - only schema structure
        for tool_name, schema in result["tools"].items():
            assert "required" in schema or "optional" in schema
            assert "types" in schema
            # Should not contain actual data values
            assert "data" not in schema
            assert "results" not in schema
            assert "values" not in schema

    @pytest.mark.asyncio
    async def test_lackey_schema_tool_specific_introspection(self) -> None:
        """Test lackey_schema tool for specific tool introspection."""
        result = await self.gateway.get_tool_schema(
            "get_ready_tasks", "lackey_get", "tier3"
        )

        assert result["tool_name"] == "get_ready_tasks"
        assert result["gateway"] == "lackey_get"
        assert result["disclosure_level"] == "tier3"
        assert "schema" in result

        # Verify schema structure without data contamination
        schema = result["schema"]
        assert isinstance(schema, dict)
        # Should contain schema metadata, not actual data
        for key, value in schema.items():
            assert key in [
                "required",
                "optional",
                "types",
                "descriptions",
                "examples",
                "constraints",
            ]

    @pytest.mark.asyncio
    async def test_lackey_schema_tool_list_available(self) -> None:
        """Test lackey_schema tool lists available tools without data exposure."""
        result = await self.gateway.list_available_tools()

        assert "tools_by_gateway" in result
        assert "total_tool_count" in result
        assert "gateway_count" in result

        # Verify only tool names, no data
        for gateway, tools in result["tools_by_gateway"].items():
            assert isinstance(tools, list)
            for tool in tools:
                assert isinstance(tool, str)
                # Tool names should not contain data values
                assert not any(char.isdigit() for char in tool if tool.count(char) > 3)

    def test_lackey_suggest_tool_schema_based_suggestions(self) -> None:
        """Test lackey_suggest tool provides schema-based parameter suggestions."""
        result = lackey_suggest.suggest_parameters("get_ready_tasks")

        assert "tool_name" in result
        assert "parameter_suggestions" in result
        assert result["tool_name"] == "get_ready_tasks"

        # Verify suggestions are schema-based, not data-based
        suggestions = result["parameter_suggestions"]
        for suggestion in suggestions:
            assert "name" in suggestion
            assert "type" in suggestion
            assert "required" in suggestion
            # Should not contain actual data values
            assert "actual_value" not in suggestion
            assert "current_data" not in suggestion

    def test_lackey_suggest_tool_next_parameter(self) -> None:
        """Test lackey_suggest tool suggests next parameter based on schema."""
        current_params = {"project_id": "test-id"}
        result = lackey_suggest.suggest_next_parameter("get_task", current_params)

        assert "next_parameter" in result
        assert "suggestion" in result

        # Verify suggestions are structural, not data-driven
        suggestion = result["suggestion"]
        assert "name" in suggestion
        assert "description" in suggestion
        # Should be schema-based reasoning
        assert "examples" in suggestion

    def test_lackey_suggest_tool_parameter_structure(self) -> None:
        """Test lackey_suggest tool analyzes parameter structure without data."""
        result = lackey_suggest.analyze_parameter_structure("update_task_status")

        assert "tool_name" in result
        assert "parameter_count" in result
        assert result["tool_name"] == "update_task_status"

        # Verify analysis is purely structural
        assert "parameter_types" in result
        assert "validation_rules" in result
        assert "complexity_score" in result

        # Should not contain data references
        assert "data_value" not in result
        assert "current_value" not in result

    def test_lackey_validate_tool_schema_validation(self) -> None:
        """Test lackey_validate tool validates against schema without execution."""
        test_params = {
            "project_id": "d1e10785-84bd-42f7-9e2e-536496c4509a",
            "task_id": "test-task-id",
            "new_status": "in_progress",
        }
        result = lackey_validate.validate_parameters("update_task_status", test_params)

        assert "valid" in result
        assert "tool_name" in result
        assert "validation_score" in result
        assert result["tool_name"] == "update_task_status"

        # Verify validation is schema-based, not execution-based
        assert "execution_result" not in result
        assert "actual_data" not in result
        assert "database_check" not in result

    def test_lackey_validate_tool_structure_validation(self) -> None:
        """Test lackey_validate tool validates parameter structure."""
        test_params = {"invalid_param": "value"}
        result = lackey_validate.validate_structure("get_ready_tasks", test_params)

        assert "structure_valid" in result
        assert "structure_issues" in result

        # Should identify structural issues without data access
        if not result["structure_valid"]:
            assert len(result["structure_issues"]) > 0
            for issue in result["structure_issues"]:
                assert "parameter" in issue
                assert "severity" in issue
                assert "message" in issue
                # Messages should be schema-focused
                assert any(
                    word in issue["message"].lower()
                    for word in [
                        "schema",
                        "expected",
                        "parameter",
                        "structure",
                        "required",
                    ]
                )

    def test_lackey_validate_tool_validation_guidance(self) -> None:
        """Test lackey_validate tool provides validation guidance without execution."""
        test_params = {"project_id": "invalid-format"}
        result = lackey_validate.get_validation_guidance("get_ready_tasks", test_params)

        assert "guidance" in result
        assert "examples" in result
        assert "validation_summary" in result

        # Verify guidance is schema-based
        guidance = result["guidance"]
        for guide in guidance:
            assert isinstance(guide, str)
            # Should not reference actual data or execution
            assert "execution" not in guide.lower()
            assert "database" not in guide.lower()

    def test_clean_separation_from_data_operations(self) -> None:
        """Test that all tools maintain clean separation from data operations."""
        # Mock any potential data access to ensure it's not called
        with patch("src.lackey.core.LackeyCore") as mock_core:
            mock_core.return_value = Mock()

            # Test schema introspection doesn't access core data
            LackeySchemaGateway()

            # These operations should work without core instance
            result1 = lackey_suggest.suggest_parameters("get_ready_tasks")
            result2 = lackey_validate.validate_parameters("get_ready_tasks", {})

            # Verify core was not accessed for data operations
            mock_core.assert_not_called()

            assert "parameter_suggestions" in result1
            assert "valid" in result2

    @pytest.mark.asyncio
    async def test_disclosure_level_filtering(self) -> None:
        """Test that disclosure levels properly filter schema information."""
        # Test Tier 1 - minimal disclosure
        tier1_result = await self.gateway.get_tool_schema(
            "get_ready_tasks", disclosure_level="tier1"
        )
        tier1_schema = tier1_result["schema"]

        # Test Tier 2 - standard disclosure
        tier2_result = await self.gateway.get_tool_schema(
            "get_ready_tasks", disclosure_level="tier2"
        )
        tier2_schema = tier2_result["schema"]

        # Test Tier 3 - complete disclosure
        tier3_result = await self.gateway.get_tool_schema(
            "get_ready_tasks", disclosure_level="tier3"
        )
        tier3_schema = tier3_result["schema"]

        # Verify progressive disclosure
        assert len(tier1_schema.keys()) <= len(tier2_schema.keys())
        assert len(tier2_schema.keys()) <= len(tier3_schema.keys())

        # Tier 1 should have minimal info
        assert "required" in tier1_schema
        assert "types" in tier1_schema

        # Tier 2 should have more detail
        assert "required" in tier2_schema
        assert "optional" in tier2_schema
        assert "types" in tier2_schema

        # All should maintain data separation
        for schema in [tier1_schema, tier2_schema, tier3_schema]:
            assert "data" not in schema
            assert "values" not in schema
            assert "results" not in schema

    def test_error_handling_without_data_exposure(self) -> None:
        """Test that error handling doesn't expose data."""
        # Test invalid tool name
        result = lackey_suggest.suggest_parameters("nonexistent_tool")
        assert "error" in result

        # Error should not contain data values
        error_msg = result["error"].lower()
        assert "data" not in error_msg
        assert "value" not in error_msg

        # Should be a clean error message
        assert "not found" in error_msg or "unknown" in error_msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
