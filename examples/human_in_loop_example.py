"""Example demonstrating Human-in-the-Loop with LangGraph interrupt pattern."""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from langgraph.types import Command
from src.patent_search_agent.graph import create_graph
from src.patent_search_agent.schemas import SeedKeywords


def run_with_human_approval():
    """Example: Run workflow with human approval."""
    
    # Create graph with memory for interrupt functionality
    app = create_graph()
    
    # Sample patent description
    patent_description = """
    A smart wearable device that monitors vital signs including heart rate, 
    blood pressure, and body temperature. The device uses machine learning 
    to predict health anomalies and alert users in real-time.
    """
    
    initial_state = {
        "patent_description": patent_description,
        "max_results": 10,
        "messages": [],
        "validation_complete": False
    }
    
    # Create thread configuration for this workflow
    thread_config = {"configurable": {"thread_id": "patent_search_001"}}
    
    print("🚀 Starting patent search workflow...")
    
    try:
        # Run until interrupt (human validation node)
        result = app.invoke(initial_state, config=thread_config)
        print("⏸️  Workflow paused at human validation node")
        print("📋 Please review the keywords and provide your decision")
        
        # In a real application, you would:
        # 1. Display the keywords to the user via UI
        # 2. Get user input through a form/interface  
        # 3. Resume with user's decision
        
        # For demo, let's approve the keywords
        print("✅ Simulating user approval...")
        
        # Resume with approval
        final_result = app.invoke(
            Command(resume="approve"), 
            config=thread_config
        )
        
        print("🎉 Workflow completed successfully!")
        return final_result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def run_with_human_edits():
    """Example: Run workflow with human keyword edits."""
    
    app = create_graph()
    
    patent_description = """
    An autonomous drone system for agricultural monitoring using computer vision 
    and AI to detect crop diseases, pest infestations, and optimize irrigation.
    """
    
    initial_state = {
        "patent_description": patent_description,
        "max_results": 15,
        "messages": [],
        "validation_complete": False
    }
    
    thread_config = {"configurable": {"thread_id": "patent_search_002"}}
    
    print("🚀 Starting patent search workflow with edits...")
    
    try:
        # Run until interrupt
        result = app.invoke(initial_state, config=thread_config)
        print("⏸️  Workflow paused at human validation node")
        
        # Simulate user editing keywords
        print("✏️  Simulating user keyword edits...")
        
        edited_keywords = {
            "action": "edit",
            "keywords": {
                "problem_purpose": [
                    "crop_disease_detection",
                    "pest_monitoring", 
                    "precision_agriculture",
                    "automated_irrigation"
                ],
                "object_system": [
                    "autonomous_drone",
                    "computer_vision_system",
                    "ai_detection_algorithm",
                    "multispectral_camera"
                ],
                "environment_field": [
                    "agricultural_technology",
                    "precision_farming",
                    "drone_agriculture",
                    "smart_farming"
                ]
            }
        }
        
        # Resume with edited keywords
        final_result = app.invoke(
            Command(resume=edited_keywords),
            config=thread_config
        )
        
        print("🎉 Workflow completed with user edits!")
        return final_result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def run_with_human_rejection():
    """Example: Run workflow with human keyword rejection."""
    
    app = create_graph()
    
    patent_description = """
    A blockchain-based supply chain tracking system that ensures 
    product authenticity and transparency from manufacturer to consumer.
    """
    
    initial_state = {
        "patent_description": patent_description,
        "max_results": 10,
        "messages": [],
        "validation_complete": False
    }
    
    thread_config = {"configurable": {"thread_id": "patent_search_003"}}
    
    print("🚀 Starting patent search workflow with rejection...")
    
    try:
        # Run until interrupt
        result = app.invoke(initial_state, config=thread_config)
        print("⏸️  Workflow paused at human validation node")
        
        # Simulate user rejecting keywords
        print("❌ Simulating user keyword rejection...")
        
        # Resume with rejection
        final_result = app.invoke(
            Command(resume="reject"),
            config=thread_config
        )
        
        print("🎉 Workflow completed with keyword rejection!")
        return final_result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def show_interrupt_data_example():
    """Example showing what data is presented to user during interrupt."""
    
    # Sample data that would be shown to user
    interrupt_data = {
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
            "problem_purpose": ["health_monitoring", "vital_signs_detection"],
            "object_system": ["wearable_device", "sensor_array"],
            "environment_field": ["medical_technology", "healthcare"]
        },
        "formatted_display": """
Problem Purpose:
  1. health_monitoring
  2. vital_signs_detection

Object System:
  1. wearable_device
  2. sensor_array

Environment Field:
  1. medical_technology
  2. healthcare
        """
    }
    
    print("📋 Example of data presented to user during interrupt:")
    print("=" * 60)
    for key, value in interrupt_data.items():
        print(f"{key}: {value}")
        print("-" * 40)


if __name__ == "__main__":
    print("🔍 LangGraph Human-in-the-Loop Examples")
    print("=" * 50)
    
    print("\n1. 📋 Example interrupt data:")
    show_interrupt_data_example()
    
    print("\n2. ✅ Running with approval:")
    run_with_human_approval()
    
    print("\n3. ✏️  Running with edits:")
    run_with_human_edits()
    
    print("\n4. ❌ Running with rejection:")
    run_with_human_rejection()
    
    print("\n✅ All examples completed!")
