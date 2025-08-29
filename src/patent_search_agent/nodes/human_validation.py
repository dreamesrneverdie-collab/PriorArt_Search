"""Human Validation Node - Allows human-in-the-loop validation of keywords."""

from typing import Dict, Any
from langchain_core.messages import HumanMessage
from langgraph.types import interrupt

from ..state import PatentSearchState


def human_validation_node(state: PatentSearchState) -> Dict[str, Any]:
    """
    Human-in-the-loop validation of generated keywords using LangGraph interrupt.
    
    This node implements the "Review and Edit State" pattern from LangGraph.
    Uses interrupt() to pause the workflow and wait for human input.
    
    Args:
        state: Current state containing seed_keywords
        
    Returns:
        Updated state with validated_keywords
    """
    try:
        seed_keywords = state.get("seed_keywords")
        
        if not seed_keywords:
            return {
                **state,
                "errors": state.get("errors", []) + ["No seed keywords found for validation"],
                "validated_keywords": {}
            }
        
        # Format keywords for human review
        formatted_keywords = _format_keywords_for_display(seed_keywords)
        
        # Use interrupt to pause workflow and get human input
        # This will pause the graph execution until resumed with Command(resume=human_input)
        human_input = interrupt(
            {
                "task": "Review and edit the generated keywords for patent search",
                "instruction": """
Please review the keywords below and provide your feedback:

Actions you can take:
1. 'approve' - Accept all keywords as-is
2. 'edit' - Provide modified keywords in the same structure
3. 'reject' - Reject all keywords (will use fallback)

If editing, please provide the modified keywords in this format:
{
    "action": "edit",
    "keywords": {
        "problem_purpose": ["keyword1", "keyword2", ...],
        "object_system": ["keyword1", "keyword2", ...],
        "environment_field": ["keyword1", "keyword2", ...]
    }
}
                """,
                "current_keywords": {
                    "problem_purpose": seed_keywords.problem_purpose,
                    "object_system": seed_keywords.object_system,
                    "environment_field": seed_keywords.environment_field
                },
                "formatted_display": formatted_keywords
            }
        )
        
        # Process human input
        validated_keywords = _process_human_input(human_input, seed_keywords)
        
        return {
            **state,
            "validated_keywords": validated_keywords,
            "messages": state.get("messages", []) + [
                HumanMessage(content=f"Keywords validated by human: {human_input}")
            ]
        }
        
    except Exception as e:
        error_msg = f"Error in human validation: {str(e)}"
        # Fallback: use original keywords if validation fails
        fallback_keywords = state.get("seed_keywords", {})
        
        return {
            **state,
            "validated_keywords": fallback_keywords,
            "errors": state.get("errors", []) + [error_msg],
        }


def _format_keywords_for_display(seed_keywords) -> str:
    """Format keywords for human-readable display."""
    if not seed_keywords:
        return "No keywords generated."
    
    formatted = []
    categories = ["problem_purpose", "object_system", "environment_field"]
    
    for category in categories:
        keywords = getattr(seed_keywords, category, [])
        if keywords:
            formatted.append(f"\n{category.replace('_', ' ').title()}:")
            for i, keyword in enumerate(keywords, 1):
                formatted.append(f"  {i}. {keyword}")
    
    return "\n".join(formatted)


def _process_human_input(human_input: Any, seed_keywords) -> Dict[str, Any]:
    """Process human input and return validated keywords."""
    
    # Handle different input formats
    if isinstance(human_input, str):
        action = human_input.lower().strip()
        
        if action == "approve":
            # Return original keywords as dict
            return {
                "problem_purpose": seed_keywords.problem_purpose,
                "object_system": seed_keywords.object_system,
                "environment_field": seed_keywords.environment_field
            }
        elif action == "reject":
            # Return empty keywords
            return {
                "problem_purpose": [],
                "object_system": [],
                "environment_field": []
            }
        else:
            # Default to approve if unclear
            return {
                "problem_purpose": seed_keywords.problem_purpose,
                "object_system": seed_keywords.object_system,
                "environment_field": seed_keywords.environment_field
            }
    
    elif isinstance(human_input, dict):
        action = human_input.get("action", "approve").lower()
        
        if action == "edit" and "keywords" in human_input:
            # Use edited keywords
            edited = human_input["keywords"]
            return {
                "problem_purpose": edited.get("problem_purpose", seed_keywords.problem_purpose),
                "object_system": edited.get("object_system", seed_keywords.object_system),
                "environment_field": edited.get("environment_field", seed_keywords.environment_field)
            }
        elif action == "reject":
            return {
                "problem_purpose": [],
                "object_system": [],
                "environment_field": []
            }
        else:
            # Default to approve
            return {
                "problem_purpose": seed_keywords.problem_purpose,
                "object_system": seed_keywords.object_system,
                "environment_field": seed_keywords.environment_field
            }
    
    # Fallback: return original keywords
    return {
        "problem_purpose": seed_keywords.problem_purpose,
        "object_system": seed_keywords.object_system,
        "environment_field": seed_keywords.environment_field
    }

