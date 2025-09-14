from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter()

@router.get("/types")
def get_component_types():
    """Get all available component types and their configurations"""
    component_types = {
        "user-query": {
            "name": "User Query",
            "description": "Entry point for user input",
            "category": "input",
            "config_schema": {
                "placeholder": {
                    "type": "string",
                    "label": "Placeholder Text",
                    "default": "Enter your question..."
                },
                "validation": {
                    "type": "boolean", 
                    "label": "Enable Input Validation",
                    "default": False
                }
            }
        },
        "knowledge-base": {
            "name": "Knowledge Base",
            "description": "Document processing and vector search",
            "category": "processing",
            "config_schema": {
                "documents": {
                    "type": "array",
                    "label": "Linked Documents",
                    "default": []
                },
                "search_limit": {
                    "type": "number",
                    "label": "Search Result Limit",
                    "default": 5,
                    "min": 1,
                    "max": 20
                },
                "similarity_threshold": {
                    "type": "number",
                    "label": "Similarity Threshold",
                    "default": 0.7,
                    "min": 0.1,
                    "max": 1.0,
                    "step": 0.1
                }
            }
        },
        "llm-engine": {
            "name": "LLM Engine",
            "description": "AI language model processing",
            "category": "processing",
            "config_schema": {
                "model": {
                    "type": "select",
                    "label": "Model",
                    "options": [
                        {"value": "gpt-3.5-turbo", "label": "GPT-3.5 Turbo"},
                        {"value": "gpt-4", "label": "GPT-4"},
                        {"value": "gpt-4-turbo", "label": "GPT-4 Turbo"},
                        {"value": "gemini-1.5-flash", "label": "Gemini Pro"}
                    ],
                    "default": "gemini-1.5-flash"
                },
                "custom_prompt": {
                    "type": "textarea",
                    "label": "Custom Prompt",
                    "placeholder": "Enter custom instructions for the AI...",
                    "default": ""
                },
                "temperature": {
                    "type": "number",
                    "label": "Temperature",
                    "default": 0.7,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1
                },
                "max_tokens": {
                    "type": "number",
                    "label": "Max Tokens",
                    "default": 1000,
                    "min": 100,
                    "max": 4000
                },
                "enable_web_search": {
                    "type": "boolean",
                    "label": "Enable Web Search",
                    "default": False
                },
                "web_search_queries": {
                    "type": "number",
                    "label": "Web Search Result Limit",
                    "default": 3,
                    "min": 1,
                    "max": 10
                }
            }
        },
        "output": {
            "name": "Output",
            "description": "Display final response to user",
            "category": "output",
            "config_schema": {
                "format": {
                    "type": "select",
                    "label": "Output Format",
                    "options": [
                        {"value": "text", "label": "Plain Text"},
                        {"value": "markdown", "label": "Markdown"},
                        {"value": "html", "label": "HTML"}
                    ],
                    "default": "markdown"
                },
                "show_sources": {
                    "type": "boolean",
                    "label": "Show Sources",
                    "default": True
                },
                "show_execution_time": {
                    "type": "boolean",
                    "label": "Show Execution Time",
                    "default": False
                }
            }
        }
    }
    
    return component_types

@router.get("/categories")
def get_component_categories():
    """Get component categories for UI organization"""
    categories = [
        {"id": "input", "name": "Input", "description": "Components for receiving user input"},
        {"id": "processing", "name": "Processing", "description": "Components for data processing and AI operations"},
        {"id": "output", "name": "Output", "description": "Components for displaying results"}
    ]
    return categories

@router.post("/validate-config")
def validate_component_config(component_type: str, config: Dict[str, Any]):
    """Validate component configuration"""
    # Get component types
    component_types = get_component_types()
    
    if component_type not in component_types:
        return {"valid": False, "errors": ["Invalid component type"]}
    
    schema = component_types[component_type]["config_schema"]
    errors = []
    
    # Basic validation
    for field, field_schema in schema.items():
        if field in config:
            value = config[field]
            field_type = field_schema["type"]
            
            # Type validation
            if field_type == "number":
                if not isinstance(value, (int, float)):
                    errors.append(f"{field} must be a number")
                else:
                    # Range validation
                    if "min" in field_schema and value < field_schema["min"]:
                        errors.append(f"{field} must be >= {field_schema['min']}")
                    if "max" in field_schema and value > field_schema["max"]:
                        errors.append(f"{field} must be <= {field_schema['max']}")
            
            elif field_type == "boolean":
                if not isinstance(value, bool):
                    errors.append(f"{field} must be a boolean")
            
            elif field_type == "string":
                if not isinstance(value, str):
                    errors.append(f"{field} must be a string")
            
            elif field_type == "array":
                if not isinstance(value, list):
                    errors.append(f"{field} must be an array")
    
    return {"valid": len(errors) == 0, "errors": errors}