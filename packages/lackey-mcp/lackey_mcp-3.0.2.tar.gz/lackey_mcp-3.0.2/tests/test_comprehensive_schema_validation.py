"""Comprehensive test suite for all schema disclosure tiers and validation scenarios.

Tests verify complete coverage of:
- All three schema disclosure tiers (Tier 1, 2, 3)
- Schema validation scenarios across all tools
- Error response format validation
- No data contamination in test scenarios
"""

from typing import Any
from unittest.mock import Mock, patch

import pytest

from src.lackey.mcp.gateways.lackey_schema import LackeySchemaGateway
from src.lackey.mcp.lackey_suggest import lackey_suggest
from src.lackey.mcp.lackey_validate import lackey_validate


class TestComprehensiveSchemaValidation:
    """Comprehensive test suite for schema disclosure and validation."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.gateway = LackeySchemaGateway()
        self.test_tools = [
            "get_ready_tasks",
            "get_task",
            "update_task_status",
            "add_task_note",
        ]
        self.test_gateways = ["lackey_get", "lackey_do", "lackey_analyze"]

    # ========== TIER 1 SCHEMA DISCLOSURE TESTS ==========

    @pytest.mark.asyncio
    async def test_tier1_schema_disclosure_minimal_info(self) -> None:
        """Test Tier 1 provides minimal schema information only."""
        for gateway in self.test_gateways:
            result = await self.gateway.get_gateway_schema(gateway, "tier1")

            assert result["disclosure_level"] == "tier1"
            assert "tools" in result

            for tool_name, schema in result["tools"].items():
                # Tier 1 should only have required params and basic types
                assert "required" in schema
                assert "types" in schema
                # Should not have detailed info
                assert "descriptions" not in schema
                assert "examples" not in schema
                assert "constraints" not in schema

                # Types should be simplified
                for param, param_type in schema["types"].items():
                    assert param_type in [
                        "text",
                        "number",
                        "true/false",
                        "list",
                        "object",
                        "value",
                        "id",
                    ]

    @pytest.mark.asyncio
    async def test_tier1_tool_specific_schema(self) -> None:
        """Test Tier 1 tool-specific schema disclosure."""
        for tool in self.test_tools:
            try:
                result = await self.gateway.get_tool_schema(
                    tool, disclosure_level="tier1"
                )
                schema = result["schema"]

                assert result["disclosure_level"] == "tier1"
                assert "required" in schema
                assert "types" in schema
                # Minimal disclosure - no optional params shown
                assert "optional" not in schema or len(schema.get("optional", {})) == 0

            except ValueError:
                # Tool not found is acceptable
                continue

    # ========== TIER 2 SCHEMA DISCLOSURE TESTS ==========

    @pytest.mark.asyncio
    async def test_tier2_schema_disclosure_standard_info(self) -> None:
        """Test Tier 2 provides standard schema information."""
        for gateway in self.test_gateways:
            result = await self.gateway.get_gateway_schema(gateway, "tier2")

            assert result["disclosure_level"] == "tier2"
            assert "tools" in result

            for tool_name, schema in result["tools"].items():
                # Tier 2 should have required, optional, and types
                assert "required" in schema
                assert "types" in schema
                assert "optional" in schema

                # May have descriptions but not full examples
                if "descriptions" in schema:
                    assert isinstance(schema["descriptions"], dict)

    @pytest.mark.asyncio
    async def test_tier2_parameter_validation_scenarios(self) -> None:
        """Test Tier 2 parameter validation scenarios."""
        test_cases = [
            ("get_ready_tasks", {"project_id": "valid-uuid"}),
            ("get_task", {"project_id": "valid-uuid", "task_id": "valid-uuid"}),
            (
                "update_task_status",
                {
                    "project_id": "valid-uuid",
                    "task_id": "valid-uuid",
                    "new_status": "in_progress",
                },
            ),
        ]

        for tool_name, params in test_cases:
            result = lackey_validate.validate_parameters(tool_name, params)

            assert "valid" in result
            assert "tool_name" in result
            assert result["tool_name"] == tool_name
            assert "validation_score" in result

            # Should not contain actual data
            assert "actual_data" not in result
            assert "database_values" not in result

    # ========== TIER 3 SCHEMA DISCLOSURE TESTS ==========

    @pytest.mark.asyncio
    async def test_tier3_schema_disclosure_complete_info(self) -> None:
        """Test Tier 3 provides complete schema information."""
        for gateway in self.test_gateways:
            result = await self.gateway.get_gateway_schema(gateway, "tier3")

            assert result["disclosure_level"] == "tier3"
            assert "tools" in result

            for tool_name, schema in result["tools"].items():
                # Tier 3 should have all available information
                assert "required" in schema
                assert "types" in schema
                assert "optional" in schema

                # Should have comprehensive details
                expected_fields = ["descriptions", "examples", "constraints"]
                present_fields = [field for field in expected_fields if field in schema]
                assert len(present_fields) >= 1  # At least one detailed field

    @pytest.mark.asyncio
    async def test_tier3_comprehensive_validation_scenarios(self) -> None:
        """Test Tier 3 comprehensive validation scenarios."""
        complex_scenarios: list[tuple[str, dict[str, Any]]] = [
            # Valid complete parameters
            (
                "update_task_status",
                {
                    "project_id": "d1e10785-84bd-42f7-9e2e-536496c4509a",
                    "task_id": "eadddfea-98d2-44b2-93d6-081b17362892",
                    "new_status": "done",
                },
            ),
            # Missing required parameters
            ("get_task", {"project_id": "d1e10785-84bd-42f7-9e2e-536496c4509a"}),
            # Invalid parameter types
            ("get_ready_tasks", {"project_id": 12345}),
        ]

        for tool_name, params in complex_scenarios:
            result = lackey_validate.validate_parameters(tool_name, params)

            assert "valid" in result
            assert "issues" in result
            assert "validation_score" in result

            # Comprehensive validation should provide detailed feedback
            if not result["valid"]:
                assert len(result["issues"]) > 0
                for issue in result["issues"]:
                    assert "parameter" in issue
                    assert "severity" in issue
                    assert "message" in issue

    # ========== ERROR RESPONSE FORMAT VALIDATION ==========

    def test_tier1_error_response_format(self) -> None:
        """Test Tier 1 error response format validation."""
        # Test with invalid tool
        result = lackey_suggest.suggest_parameters("nonexistent_tool")

        assert "error" in result
        error_msg = result["error"]

        # Tier 1 errors should be minimal
        assert len(error_msg) < 100  # Brief error message
        assert "not found" in error_msg.lower()

        # Should not expose internal details
        assert "traceback" not in error_msg.lower()
        assert "exception" not in error_msg.lower()

    def test_tier2_error_response_format(self) -> None:
        """Test Tier 2 error response format validation."""
        # Test validation with invalid parameters
        result = lackey_validate.validate_parameters(
            "get_ready_tasks", {"invalid_param": "value"}
        )

        assert "valid" in result
        assert not result["valid"]
        assert "issues" in result

        # Tier 2 should provide structured error information
        for issue in result["issues"]:
            assert isinstance(issue, dict)
            assert "parameter" in issue
            assert "severity" in issue
            assert "message" in issue

            # Should not contain sensitive data
            assert "password" not in issue["message"].lower()
            assert "secret" not in issue["message"].lower()

    def test_tier3_error_response_format(self) -> None:
        """Test Tier 3 error response format validation."""
        # Test comprehensive validation guidance
        result = lackey_validate.get_validation_guidance(
            "get_ready_tasks", {"project_id": "invalid-format"}
        )

        assert "guidance" in result
        assert "examples" in result
        assert "validation_summary" in result

        # Tier 3 should provide comprehensive guidance
        assert len(result["guidance"]) > 0
        assert len(result["examples"]) > 0

        # Should include actionable suggestions
        for example in result["examples"]:
            assert "parameter" in example
            assert "fix" in example or "example" in example

    # ========== DATA CONTAMINATION PREVENTION TESTS ==========

    def test_no_data_contamination_in_schema_operations(self) -> None:
        """Test that schema operations don't access or expose actual data."""
        # Mock data access to ensure it's not called
        with patch("src.lackey.core.LackeyCore") as mock_core:
            mock_core.return_value = Mock()

            # Test all schema operations
            schema_ops = [
                lambda: lackey_suggest.suggest_parameters("get_ready_tasks"),
                lambda: lackey_validate.validate_parameters("get_ready_tasks", {}),
                lambda: lackey_suggest.analyze_parameter_structure("get_task"),
            ]

            for op in schema_ops:
                result = op()

                # Verify no data contamination
                result_str = str(result).lower()
                forbidden_terms = [
                    "actual_data",
                    "database",
                    "real_value",
                    "current_data",
                    "stored_value",
                ]
                for term in forbidden_terms:
                    assert term not in result_str

            # Verify core was not accessed
            mock_core.assert_not_called()

    def test_parameter_suggestions_no_data_leakage(self) -> None:
        """Test parameter suggestions don't leak actual data values."""
        # Get available tools first
        available_tools = [
            tool for tool in self.test_tools if self._is_tool_available(tool)
        ]

        for tool in available_tools:
            result = lackey_suggest.suggest_parameters(tool)

            # Check all suggestion content
            suggestions = result.get("parameter_suggestions", [])
            for suggestion in suggestions:
                examples = suggestion.get("examples", [])
                for example in examples:
                    # Examples should be generic, not real data
                    assert not self._is_real_data_value(str(example))

    def test_validation_scenarios_no_data_exposure(self) -> None:
        """Test validation scenarios don't expose actual system data."""
        test_params = [
            {"project_id": "test-project-id"},
            {"task_id": "test-task-id"},
            {"invalid_param": "test-value"},
        ]

        # Get available tools first
        available_tools = [
            tool for tool in self.test_tools if self._is_tool_available(tool)
        ]

        for params in test_params:
            for tool in available_tools:
                result = lackey_validate.validate_structure(tool, params)

                # Check that validation doesn't expose real data
                result_str = str(result).lower()
                assert "real_project" not in result_str
                assert "actual_task" not in result_str
                assert "database_id" not in result_str

    # ========== PROGRESSIVE DISCLOSURE VALIDATION ==========

    @pytest.mark.asyncio
    async def test_progressive_disclosure_information_levels(self) -> None:
        """Test that progressive disclosure provides appropriate information levels."""
        tool_name = "get_ready_tasks"

        # Get all three tiers
        tier1 = await self.gateway.get_tool_schema(tool_name, disclosure_level="tier1")
        tier2 = await self.gateway.get_tool_schema(tool_name, disclosure_level="tier2")
        tier3 = await self.gateway.get_tool_schema(tool_name, disclosure_level="tier3")

        # Verify progressive information increase
        tier1_keys = set(tier1["schema"].keys())
        tier2_keys = set(tier2["schema"].keys())
        tier3_keys = set(tier3["schema"].keys())

        # Each tier should have at least as much info as the previous
        assert tier1_keys.issubset(tier2_keys) or len(tier1_keys) <= len(tier2_keys)
        assert tier2_keys.issubset(tier3_keys) or len(tier2_keys) <= len(tier3_keys)

        # Verify content appropriateness
        assert "required" in tier1["schema"]
        assert "optional" in tier2["schema"]
        # Tier 3 should have the most comprehensive information
        tier3_schema = tier3["schema"]
        comprehensive_fields = ["descriptions", "examples", "constraints"]
        tier3_comprehensive = sum(
            1 for field in comprehensive_fields if field in tier3_schema
        )
        tier2_comprehensive = sum(
            1 for field in comprehensive_fields if field in tier2["schema"]
        )
        assert tier3_comprehensive >= tier2_comprehensive

    # ========== INTEGRATION AND EDGE CASE TESTS ==========

    def test_error_handling_edge_cases(self) -> None:
        """Test error handling for edge cases without data exposure."""
        edge_cases: list[tuple[str, dict[str, Any]]] = [
            ("", {}),  # Empty tool name
            ("nonexistent_tool", {}),  # Invalid tool
            ("get_ready_tasks", {"malformed": "data"}),  # Invalid parameters
        ]

        for tool_name, params in edge_cases:
            # Test suggestion tool
            suggest_result = lackey_suggest.suggest_parameters(tool_name)
            assert (
                "error" in suggest_result or "parameter_suggestions" in suggest_result
            )

            # Test validation tool
            validate_result = lackey_validate.validate_parameters(tool_name, params)
            assert "error" in validate_result or "valid" in validate_result

            # Verify no data leakage in error messages
            for result in [suggest_result, validate_result]:
                result_str = str(result).lower()
                assert "internal_error" not in result_str
                assert "system_path" not in result_str

    @pytest.mark.asyncio
    async def test_schema_consistency_across_tiers(self) -> None:
        """Test schema consistency across all disclosure tiers."""
        for gateway in self.test_gateways:
            tier1_result = await self.gateway.get_gateway_schema(gateway, "tier1")
            tier2_result = await self.gateway.get_gateway_schema(gateway, "tier2")
            tier3_result = await self.gateway.get_gateway_schema(gateway, "tier3")

            # Same tools should be available across all tiers
            tier1_tools = set(tier1_result["tools"].keys())
            tier2_tools = set(tier2_result["tools"].keys())
            tier3_tools = set(tier3_result["tools"].keys())

            assert tier1_tools == tier2_tools == tier3_tools

            # Required parameters should be consistent
            for tool_name in tier1_tools:
                tier1_required = set(
                    tier1_result["tools"][tool_name].get("required", [])
                )
                tier2_required = set(
                    tier2_result["tools"][tool_name].get("required", [])
                )
                tier3_required = set(
                    tier3_result["tools"][tool_name].get("required", [])
                )

                assert tier1_required == tier2_required == tier3_required

    # ========== HELPER METHODS ==========

    def _is_tool_available(self, tool_name: str) -> bool:
        """Check if a tool is available without raising exceptions."""
        try:
            lackey_suggest.suggest_parameters(tool_name)
            return True
        except Exception:
            return False

    def _is_real_data_value(self, value: str) -> bool:
        """Check if a value appears to be real system data rather than example data."""
        # Real data indicators (UUIDs with specific patterns, actual project names)
        real_data_patterns = [
            "d1e10785-84bd-42f7-9e2e-536496c4509a",  # Actual project ID from tests
            "eadddfea-98d2-44b2-93d6-081b17362892",  # Actual task ID from tests
            "lackey_production",
            "real_project",
            "actual_task",
        ]

        return any(pattern in value.lower() for pattern in real_data_patterns)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
