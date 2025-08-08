"""
MCP Tools Implementation Validator

This module provides comprehensive validation for MCP tool implementations,
checking compliance with FastMCP patterns, parameter validation, error handling,
and dependency analysis.
"""
import ast
import inspect
import importlib
from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import re


@dataclass
class ValidationResult:
    """Result of tool validation analysis."""
    tool_name: str
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    analysis: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation result to dictionary."""
        return asdict(self)


class FastMCPComplianceChecker:
    """Checks FastMCP framework compliance for MCP tools."""
    
    def __init__(self):
        self.fastmcp_patterns = {
            "context_parameter": "Tools should accept optional Context parameter",
            "async_function": "Tools must be async functions",
            "return_structure": "Tools should return Dict[str, Any] with success indicator",
            "error_handling": "Tools should have proper try/catch error handling",
            "parameter_validation": "Tools should validate input parameters",
            "type_annotations": "Tools should have proper type annotations"
        }
    
    async def check_tool_registration_pattern(self, tool_func: Callable) -> Dict[str, Any]:
        """Check if tool follows FastMCP registration patterns."""
        issues = []
        recommendations = []
        
        # Check function signature
        sig = inspect.signature(tool_func)
        
        # Check for context parameter
        if 'context' not in sig.parameters:
            issues.append("Missing 'context' parameter for MCP Context access")
            recommendations.append("Add 'context: Optional[Context] = None' parameter")
        
        # Check if async
        if not inspect.iscoroutinefunction(tool_func):
            issues.append("Tool function must be async")
            recommendations.append("Convert function to async def")
        
        # Check return type annotation
        return_annotation = sig.return_annotation
        if return_annotation == inspect.Signature.empty:
            issues.append("Missing return type annotation")
            recommendations.append("Add -> Dict[str, Any] return type annotation")
        
        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "recommendations": recommendations,
            "pattern_score": max(0, 100 - (len(issues) * 20))
        }
    
    async def check_error_handling_pattern(self, tool_func: Callable) -> Dict[str, Any]:
        """Check if tool implements proper error handling patterns."""
        issues = []
        recommendations = []
        
        # Get function source code
        try:
            source = inspect.getsource(tool_func)
            tree = ast.parse(source)
            
            has_try_except = False
            has_success_indicator = False
            
            # Walk the AST to find error handling patterns
            for node in ast.walk(tree):
                if isinstance(node, ast.Try):
                    has_try_except = True
                
                # Look for return statements with success indicators
                if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict):
                    for key in node.value.keys:
                        if isinstance(key, ast.Constant) and key.value == "success":
                            has_success_indicator = True
            
            if not has_try_except:
                issues.append("No try/except error handling found")
                recommendations.append("Wrap main logic in try/except block")
            
            if not has_success_indicator:
                issues.append("No success indicator in return value")
                recommendations.append("Include 'success': True/False in return dict")
                
        except Exception as e:
            issues.append(f"Could not analyze source code: {str(e)}")
        
        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "recommendations": recommendations,
            "error_handling_score": max(0, 100 - (len(issues) * 30))
        }
    
    async def check_parameter_validation(self, tool_func: Callable) -> Dict[str, Any]:
        """Check parameter validation patterns."""
        issues = []
        recommendations = []
        
        sig = inspect.signature(tool_func)
        
        # Check for type annotations on parameters
        untyped_params = []
        for param_name, param in sig.parameters.items():
            if param_name != 'context' and param.annotation == inspect.Parameter.empty:
                untyped_params.append(param_name)
        
        if untyped_params:
            issues.append(f"Parameters missing type annotations: {untyped_params}")
            recommendations.append("Add type annotations to all parameters")
        
        # Check for validation in source code
        try:
            source = inspect.getsource(tool_func)
            has_validation = "raise ValueError" in source or "ValueError(" in source
            
            if not has_validation:
                issues.append("No parameter validation found")
                recommendations.append("Add parameter validation with ValueError")
        except Exception:
            pass
        
        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "recommendations": recommendations,
            "validation_score": max(0, 100 - (len(issues) * 25))
        }


class ToolDependencyAnalyzer:
    """Analyzes dependencies between MCP tools and service layers."""
    
    def __init__(self):
        self.service_imports = {
            "TaskService": "src.services.task_service",
            "AgentService": "src.services.agent_service", 
            "AssignmentService": "src.services.assignment_service",
            "PlanService": "src.services.plan_service",
            "PlanValidator": "src.utils.plan_validator"
        }
    
    async def analyze_service_dependencies(self, tool_func: Callable) -> Dict[str, Any]:
        """Analyze service layer dependencies for a tool."""
        dependencies = {
            "services": [],
            "external_imports": [],
            "complexity_score": 0
        }
        
        try:
            source = inspect.getsource(tool_func)
            
            # Find import statements and service usage
            for service_name, module_path in self.service_imports.items():
                if service_name in source:
                    dependencies["services"].append({
                        "name": service_name,
                        "module": module_path,
                        "usage_count": source.count(service_name)
                    })
            
            # Look for external library imports
            lines = source.split('\n')
            for line in lines:
                if line.strip().startswith('from ') or line.strip().startswith('import '):
                    if 'src.' not in line:  # External import
                        dependencies["external_imports"].append(line.strip())
            
            # Calculate complexity score
            dependencies["complexity_score"] = (
                len(dependencies["services"]) * 10 +
                len(dependencies["external_imports"]) * 5
            )
            
        except Exception as e:
            dependencies["error"] = f"Could not analyze dependencies: {str(e)}"
        
        return dependencies
    
    def build_dependency_graph(self, tool_list: List[Tuple[str, List[str]]]) -> Dict[str, Any]:
        """Build dependency graph for all tools."""
        graph = {
            "nodes": [],
            "edges": [],
            "clusters": {}
        }
        
        # Add tool nodes
        for tool_name, dependencies in tool_list:
            graph["nodes"].append({
                "id": tool_name,
                "type": "tool",
                "dependency_count": len(dependencies)
            })
            
            # Add service nodes and edges
            for dep in dependencies:
                service_node = {
                    "id": dep,
                    "type": "service"
                }
                if service_node not in graph["nodes"]:
                    graph["nodes"].append(service_node)
                
                # Add edge
                graph["edges"].append({
                    "from": tool_name,
                    "to": dep,
                    "type": "dependency"
                })
        
        # Group by service clusters
        service_tools = {}
        for tool_name, dependencies in tool_list:
            for dep in dependencies:
                if dep not in service_tools:
                    service_tools[dep] = []
                service_tools[dep].append(tool_name)
        
        graph["clusters"] = service_tools
        
        return graph


class ToolValidator:
    """Main validator for MCP tool implementations."""
    
    def __init__(self):
        self.compliance_checker = FastMCPComplianceChecker()
        self.dependency_analyzer = ToolDependencyAnalyzer()
        
        # Known MCP tools for validation
        self.mcp_tools = [
            "mcp__coord-hub-lite__health_check",
            "mcp__coord-hub-lite__create_task", 
            "mcp__coord-hub-lite__update_task_status",
            "mcp__coord-hub-lite__assign_task_tool",
            "mcp__coord-hub-lite__get_task_tree_tool",
            "mcp__coord-hub-lite__register_agent_tool",
            "mcp__coord-hub-lite__find_available_agent_tool",
            "mcp__coord-hub-lite__upload_plan",
            "mcp__coord-hub-lite__validate_plan"
        ]
    
    async def validate_tool_function(self, tool_func: Callable, tool_name: str = None) -> ValidationResult:
        """Validate a single tool function implementation."""
        if tool_name is None:
            tool_name = getattr(tool_func, '__name__', 'unknown_tool')
        
        errors = []
        warnings = []
        analysis = {}
        
        # Basic function checks
        if not inspect.iscoroutinefunction(tool_func):
            errors.append("Tool function must be async")
        
        # Parameter analysis
        sig = inspect.signature(tool_func)
        analysis["parameters"] = self._analyze_parameter_types(tool_func)
        analysis["is_async"] = inspect.iscoroutinefunction(tool_func)
        analysis["return_type_annotation"] = sig.return_annotation
        
        # Check for context parameter
        if 'context' not in sig.parameters:
            errors.append("Tool function missing context parameter for MCP Context access")
        
        # FastMCP compliance checks
        compliance_result = await self.compliance_checker.check_tool_registration_pattern(tool_func)
        if not compliance_result["compliant"]:
            errors.extend(compliance_result["issues"])
        
        analysis["compliance"] = compliance_result
        
        # Error handling check
        error_handling = await self.compliance_checker.check_error_handling_pattern(tool_func)
        analysis["error_handling"] = error_handling
        
        if not error_handling["compliant"]:
            warnings.extend(error_handling["issues"])
        
        # Parameter validation check
        param_validation = await self.compliance_checker.check_parameter_validation(tool_func)
        analysis["parameter_validation"] = param_validation
        
        if not param_validation["compliant"]:
            warnings.extend(param_validation["issues"])
        
        # Dependency analysis
        dependencies = await self.dependency_analyzer.analyze_service_dependencies(tool_func)
        analysis["dependencies"] = dependencies
        
        return ValidationResult(
            tool_name=tool_name,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            analysis=analysis
        )
    
    async def validate_tool_metadata(self, metadata: Dict[str, Any]) -> ValidationResult:
        """Validate tool metadata for MCP registration."""
        errors = []
        warnings = []
        analysis = {}
        
        required_fields = ["name", "description", "parameters"]
        
        # Check required fields
        for field in required_fields:
            if field not in metadata:
                errors.append(f"Missing required field: {field}")
        
        # Validate name
        if "name" in metadata:
            name = metadata["name"]
            if not isinstance(name, str) or not name.strip():
                errors.append("Tool name must be non-empty string")
            analysis["name"] = name
        
        # Validate description
        if "description" in metadata:
            desc = metadata["description"]
            if not isinstance(desc, str) or len(desc.strip()) < 10:
                warnings.append("Tool description should be descriptive (10+ characters)")
            analysis["description"] = desc
        
        # Validate parameters schema
        if "parameters" in metadata:
            params = metadata["parameters"]
            if not isinstance(params, dict):
                errors.append("Parameters must be a dictionary")
            else:
                analysis["parameters"] = params
                
                # Check JSON schema structure
                if "type" not in params:
                    errors.append("Parameters must have 'type' field")
                
                if params.get("type") == "object" and "properties" not in params:
                    warnings.append("Object type should have 'properties' field")
        
        return ValidationResult(
            tool_name=metadata.get("name", "unknown"),
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            analysis=analysis
        )
    
    def _analyze_parameter_types(self, tool_func: Callable) -> Dict[str, Any]:
        """Analyze parameter types and defaults for a tool function."""
        sig = inspect.signature(tool_func)
        params_analysis = {}
        
        for param_name, param in sig.parameters.items():
            # Convert type annotation to string representation
            if param.annotation != inspect.Parameter.empty:
                if hasattr(param.annotation, '__name__'):
                    type_str = param.annotation.__name__
                else:
                    type_str = str(param.annotation)
            else:
                type_str = "Any"
            
            param_info = {
                "type": type_str,
                "required": param.default == inspect.Parameter.empty,
                "default": param.default if param.default != inspect.Parameter.empty else None
            }
            params_analysis[param_name] = param_info
        
        return params_analysis
    
    def _check_return_value_structure(self, return_value: Any) -> bool:
        """Check if return value follows expected structure."""
        if not isinstance(return_value, dict):
            return False
        
        # Should have success indicator or similar status field
        status_indicators = ["success", "status", "valid", "error"]
        has_status = any(key in return_value for key in status_indicators)
        
        return has_status
    
    async def validate_all_tools(self) -> Dict[str, ValidationResult]:
        """Validate all known MCP tools in the system."""
        results = {}
        
        # Tool module mappings
        tool_modules = {
            "create_task": "src.tools.task_tools",
            "update_task_status": "src.tools.task_tools",
            "register_agent_tool": "src.tools.agent_tools",
            "find_available_agent_tool": "src.tools.agent_tools",
            "assign_task_tool": "src.tools.assignment_tools",
            "get_task_tree_tool": "src.tools.assignment_tools",
            "upload_plan": "src.tools.plan_tools",
            "validate_plan": "src.tools.plan_tools"
        }
        
        for tool_name, module_path in tool_modules.items():
            try:
                # Import the module and get the tool function
                module = importlib.import_module(module_path)
                if hasattr(module, tool_name):
                    tool_func = getattr(module, tool_name)
                    result = await self.validate_tool_function(tool_func, tool_name)
                    results[tool_name] = result
                else:
                    results[tool_name] = ValidationResult(
                        tool_name=tool_name,
                        is_valid=False,
                        errors=[f"Tool function {tool_name} not found in {module_path}"],
                        warnings=[],
                        analysis={}
                    )
            except ImportError as e:
                results[tool_name] = ValidationResult(
                    tool_name=tool_name,
                    is_valid=False,
                    errors=[f"Could not import {module_path}: {str(e)}"],
                    warnings=[],
                    analysis={}
                )
            except Exception as e:
                results[tool_name] = ValidationResult(
                    tool_name=tool_name,
                    is_valid=False,
                    errors=[f"Validation error: {str(e)}"],
                    warnings=[],
                    analysis={}
                )
        
        return results
    
    def generate_compliance_report(self, validation_results: Dict[str, ValidationResult]) -> Dict[str, Any]:
        """Generate a comprehensive compliance report."""
        report = {
            "summary": {
                "total_tools": len(validation_results),
                "valid_tools": sum(1 for r in validation_results.values() if r.is_valid),
                "tools_with_warnings": sum(1 for r in validation_results.values() if r.warnings),
                "compliance_score": 0
            },
            "tool_details": {},
            "common_issues": {},
            "recommendations": []
        }
        
        # Calculate compliance score
        if validation_results:
            valid_ratio = report["summary"]["valid_tools"] / report["summary"]["total_tools"]
            report["summary"]["compliance_score"] = round(valid_ratio * 100, 1)
        
        # Analyze common issues
        all_errors = []
        all_warnings = []
        
        for tool_name, result in validation_results.items():
            report["tool_details"][tool_name] = {
                "valid": result.is_valid,
                "error_count": len(result.errors),
                "warning_count": len(result.warnings),
                "errors": result.errors,
                "warnings": result.warnings
            }
            
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
        
        # Find most common issues
        from collections import Counter
        error_counts = Counter(all_errors)
        warning_counts = Counter(all_warnings)
        
        report["common_issues"] = {
            "most_common_errors": error_counts.most_common(5),
            "most_common_warnings": warning_counts.most_common(5)
        }
        
        # Generate recommendations
        if error_counts:
            top_error = error_counts.most_common(1)[0][0]
            report["recommendations"].append(f"Priority fix: {top_error}")
        
        if warning_counts:
            top_warning = warning_counts.most_common(1)[0][0] 
            report["recommendations"].append(f"Improvement opportunity: {top_warning}")
        
        return report