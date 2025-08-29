"""Keyword Generation Node - Generates seed keywords using structured output."""

from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.language_models import BaseChatModel

from ..state import PatentSearchState
from ..schemas import SeedKeywords, ConceptMatrix
from ..utils.prompts import KEYWORD_GENERATION_PROMPT


def keyword_generation_node(state: PatentSearchState, llm: BaseChatModel) -> Dict[str, Any]:
    """
    Generate seed keywords from concept matrix using structured output.
    
    This node uses the "bind as tool" approach to ensure structured keyword output.
    
    Args:
        state: Current state containing concept_matrix_structured
        llm: Language model for keyword generation
        
    Returns:
        Updated state with seed_keywords_structured
    """
    try:
        # Get concept matrix from state
        concept_matrix = state.get("concept_matrix")
        if not concept_matrix:
            raise ValueError("No concept matrix found in state")
        
        model = llm.with_structured_output(SeedKeywords)
        
        # Format concept matrix for prompt
        concept_text = _format_concept_matrix(concept_matrix)
        
        # Create messages for LLM
        messages = [
            SystemMessage(content=KEYWORD_GENERATION_PROMPT + """

You MUST respond by calling the SeedKeywords tool with the generated keywords.
Generate 3-10 high-quality search keywords for each category based on the concept matrix.
Focus on technical terminology that would appear in patent documents.

Guidelines:
- Use patent-specific language and formal terminology
- Include both specific and broader category terms
- Consider Boolean search optimization
- Balance specificity with searchability
"""),
            HumanMessage(content=f"""
Concept Matrix:
{concept_text}

Generate seed keywords for patent search based on these extracted concepts.
Each category should have 3-10 relevant search terms.
""")
        ]
        
        # Get LLM response with forced tool calling
        response = model.invoke(messages)

        seed_keywords = response

        return {
            **state,
            "seed_keywords": seed_keywords,
            "messages": state.get("messages", []) + [
                HumanMessage(content="Generating search keywords from concepts"),
                response,
            ]
        }
        
    except Exception as e:
        error_msg = f"Error in keyword generation: {str(e)}"
        # Fallback keyword generation
        concept_matrix = state.get("concept_matrix")
        fallback_keywords = _fallback_keyword_generation(concept_matrix)
    
        return {
            **state,
            "seed_keywords": fallback_keywords,
            "errors": state.get("errors", []) + [error_msg],
        }


def _format_concept_matrix(concept_matrix: ConceptMatrix) -> str:
    """Format concept matrix for display in prompt."""
    return f"""
Problem/Purpose: {', '.join(concept_matrix.problem_purpose)}
Object/System: {', '.join(concept_matrix.object_system)}
Environment/Field: {', '.join(concept_matrix.environment_field)}
"""


def _fallback_keyword_generation(concept_matrix: ConceptMatrix) -> SeedKeywords:
    """
    Fallback keyword generation when structured output fails.
    
    Args:
        concept_matrix: Extracted concept matrix
        
    Returns:
        Basic SeedKeywords based on concepts
    """
    problem_keywords = []
    object_keywords = []
    field_keywords = []
    
    # Generate keywords from problem/purpose concepts
    for concept in concept_matrix.problem_purpose:
        problem_keywords.append([f"fallback_keyword_{concept}"]*3)
    
    # Generate keywords from object/system concepts
    for concept in concept_matrix.object_system:
        object_keywords.append([f"fallback_keyword_{concept}"]*3)

    # Generate keywords from environment/field concepts
    for concept in concept_matrix.environment_field:
        field_keywords.append([f"fallback_keyword_{concept}"]*3)
    
    return SeedKeywords(
        problem_purpose=problem_keywords[:10],
        object_system=object_keywords[:10],
        environment_field=field_keywords[:10]
    )

