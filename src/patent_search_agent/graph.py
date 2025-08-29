"""Main graph with structured output nodes for Patent Search Agent."""

import logging
import os
from typing import Literal

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import ChatOllama

from .state import PatentSearchState
from .nodes.concept_extraction import concept_extraction_node
from .nodes.keyword_generation import keyword_generation_node
from .nodes.query_generation import query_generation_node
from .nodes.human_validation import human_validation_node
from .nodes.enhancement import enhancement_node
from .nodes.ipc_classification import ipc_classification_node
from .nodes.patent_search import patent_search_node
from .nodes.evaluation import evaluation_node

# Load environment variables
load_dotenv()


def create_llm(model_name: str = "qwen3:8b"):
    """Create LLM instance based on model name."""
    try:
        return ChatOllama(
            model=model_name,
            temperature=0.7,
            num_predict=4096,
            num_ctx=20480,
            reasoning=True,
        )
    except Exception as e:
        logging.error(f"Error creating LLM: {e}")


def should_continue_validation(state: PatentSearchState) -> Literal["keyword_generation", "enhancement"]:
    """Determine if validation is complete or needs human input."""
    if state.get("validated_keywords", False)["problem_purpose"].is_empty() and state.get("validated_keywords", False)["object_system"].is_empty() and state.get("validated_keywords", False)["environment_field"].is_empty():
        return "keyword_generation"
    return "enhancement"


def should_continue_workflow(state: PatentSearchState) -> Literal["evaluation", "__end__"]:
    """Determine if workflow should continue or end."""
    # Check both old and new search results formats
    search_results = state.get("search_results", [])
    search_results = state.get("search_results")
    
    has_results = False
    if search_results:
        has_results = len(search_results) > 0
    elif search_results:
        has_results = search_results.total_found > 0
    
    if has_results:
        return "evaluation"
    return "__end__"


def create_graph(
    model_name: str = "qwen3:8b",
    checkpointer=None
) -> StateGraph:
    """
    Create the patent search workflow graph with structured outputs.
    
    This graph uses the "bind as tool" approach for structured outputs,
    ensuring consistent data formats throughout the workflow.
    """
    
    # Create LLM instance
    llm = create_llm(model_name)
    
    # Create checkpointer if not provided
    if checkpointer is None:
        checkpointer = MemorySaver()
    
    # Create the graph
    workflow = StateGraph(PatentSearchState)
    
    # Add structured nodes
    workflow.add_node("concept_extraction", lambda state: concept_extraction_node(state, llm))
    workflow.add_node("keyword_generation", lambda state: keyword_generation_node(state, llm))
    workflow.add_node("human_validation", human_validation_node)
    workflow.add_node("enhancement", lambda state: enhancement_node(state, llm))
    workflow.add_node("ipc_classification", lambda state: ipc_classification_node(state, llm))
    workflow.add_node("query_generation", lambda state: query_generation_node(state, llm))
    workflow.add_node("patent_search", patent_search_node)
    workflow.add_node("evaluation", evaluation_node)
    
    # Define the workflow edges
    workflow.add_edge(START, "concept_extraction")
    workflow.add_edge("concept_extraction", "keyword_generation")
    workflow.add_edge("keyword_generation", "human_validation")
    
    # Conditional edge for human validation
    workflow.add_conditional_edges(
        "human_validation",
        should_continue_validation,
        {
            "human_validation": "human_validation",  # Loop back for more validation
            "enhancement": "enhancement"
        }
    )
    
    workflow.add_edge("enhancement", "ipc_classification")
    workflow.add_edge("ipc_classification", "query_generation")
    # workflow.add_edge("query_generation", "patent_search")
    
    # Conditional edge for final results
    # workflow.add_conditional_edges(
    #     "patent_search",
    #     should_continue_workflow,
    #     {
    #         "evaluation": "evaluation",
    #         "__end__": END
    #     }
    # )
    
    # workflow.add_edge("evaluation", END)
    workflow.add_edge("query_generation", END)
    
    # Compile the graph
    app = workflow.compile(checkpointer=checkpointer)
    
    return app


def run_patent_search(
    patent_description: str,
    max_results: int = 10,
    model_name: str = "qwen3:8b"
) -> dict:
    """
    Run the patent search workflow with structured outputs.
    
    Args:
        patent_description: Description of the patent to search for
        max_results: Maximum number of results to return
        model_name: LLM model to use
        
    Returns:
        Final state with structured results
    """
    
    app = create_graph(model_name=model_name)
    
    initial_state = {
        "patent_description": patent_description,
        "max_results": max_results,
        "messages": [],
        "validation_complete": False
    }
    
    # Create a thread for this run
    thread = {"configurable": {"thread_id": "patent_search"}}
    
    # Run the workflow
    result = app.invoke(initial_state, config=thread)
    
    return result


def extract_results(final_state: dict) -> dict:
    """
    Extract key structured results from the final state.
    
    Args:
        final_state: Final state from workflow execution
        
    Returns:
        Dictionary with key structured outputs
    """
    return {
        "concept_matrix": final_state.get("concept_matrix"),
        "seed_keywords": final_state.get("seed_keywords"),
        "enhanced_keywords": final_state.get("enhanced_keywords"),
        "ipc_classification": final_state.get("ipc_classification"),
        "search_queries": final_state.get("search_queries"),
        "search_results": final_state.get("search_results"),
        "similarity_evaluations": final_state.get("similarity_evaluations"),
        "final_results": final_state.get("final_results"),
        "errors": final_state.get("errors", [])
    }


if __name__ == "__main__":
    # Example usage with structured outputs
    sample_description = """
    A smart wearable device for continuous health monitoring that integrates multiple biosensors 
    including heart rate, blood oxygen saturation, skin temperature, and motion sensors. The device 
    uses machine learning algorithms to analyze the collected data and predict potential health issues.
    """
    
    print("🔍 Running Patent Search with Structured Outputs...")
    result = run_patent_search(sample_description)
    
    # Extract structured results
    structured_results = extract_results(result)
    
    print("\n📊 Structured Results:")
    for key, value in structured_results.items():
        if value:
            print(f"✅ {key}: Available")
        else:
            print(f"❌ {key}: Not available")
    
    # Show concept matrix if available
    concept_matrix = structured_results.get("concept_matrix")
    if concept_matrix:
        print(f"\n🎯 Concept Matrix:")
        print(f"Problem/Purpose: {concept_matrix.problem_purpose}")
        print(f"Object/System: {concept_matrix.object_system}")
        print(f"Environment/Field: {concept_matrix.environment_field}")
    
    print("\n✅ Structured patent search completed!")
