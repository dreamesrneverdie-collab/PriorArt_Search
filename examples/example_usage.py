"""
Example usage of the Patent Search Agent.

This script demonstrates how to use the multi-agent system to search for similar patents.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from patent_search_agent.graph import create_graph, run_patent_search
from patent_search_agent.nodes.human_validation import simulate_user_approval


def main():
    """Run example patent search workflow."""
    
    print("🔍 Patent Search Multi-Agent System - Example")
    print("=" * 50)
    
    # Example patent description
    patent_description = """
    A smart wearable device for continuous health monitoring that integrates multiple biosensors 
    including heart rate, blood oxygen saturation, skin temperature, and motion sensors. The device 
    uses machine learning algorithms to analyze the collected data and predict potential health issues. 
    It features wireless connectivity to sync data with a mobile application that provides 
    personalized health recommendations and alerts healthcare providers in emergency situations.
    
    The device includes a flexible display, long-lasting battery with wireless charging capability, 
    and is designed to be water-resistant for daily wear. The system employs edge computing to 
    process sensitive health data locally while using cloud services for advanced analytics and 
    data backup.
    """
    
    print("📄 Patent Description:")
    print(patent_description)
    print("\n" + "=" * 50)
    
    try:
        # Create the workflow graph
        print("🔧 Creating workflow graph...")
        app = create_graph()
        
        # Initial state
        initial_state = {
            "patent_description": patent_description,
            "max_results": 8,
            "messages": [],
            "validation_complete": False
        }
        
        print("🚀 Starting patent search workflow...")
        
        # For this example, we'll simulate the workflow steps
        # In a real implementation, you would run the full workflow
        
        # Step 1: Concept Extraction (simulated)
        print("\n1️⃣ Concept Extraction...")
        concept_matrix = {
            "problem_purpose": [
                "health monitoring", "biosensor data analysis", 
                "predictive health analytics", "emergency detection"
            ],
            "object_system": [
                "wearable device", "biosensors", "machine learning", 
                "mobile application", "wireless connectivity", "edge computing"
            ],
            "environment_field": [
                "healthcare technology", "iot medical devices", 
                "digital health", "wearable computing", "telemedicine"
            ]
        }
        print(f"   Extracted concepts: {concept_matrix}")
        
        # Step 2: Keyword Generation (simulated)
        print("\n2️⃣ Keyword Generation...")
        seed_keywords = {
            "problem_purpose": [
                "continuous health monitoring", "biosensor analysis", 
                "health prediction", "medical alert system"
            ],
            "object_system": [
                "smart wearable", "multi-sensor device", "health tracker",
                "ml health device", "connected health device"
            ],
            "environment_field": [
                "digital healthcare", "iot health", "mobile health",
                "telemedicine platform", "health informatics"
            ]
        }
        print(f"   Generated keywords: {seed_keywords}")
        
        # Step 3: Human Validation (simulated approval)
        print("\n3️⃣ Human Validation...")
        print("   Keywords approved by user (simulated)")
        validated_keywords = seed_keywords
        
        # Step 4: Enhancement (simulated)
        print("\n4️⃣ Keyword Enhancement...")
        enhanced_keywords = {
            "problem_purpose": [
                "continuous health monitoring", "biosensor analysis", 
                "health prediction", "medical alert system",
                "vital signs monitoring", "physiological monitoring"
            ],
            "object_system": [
                "smart wearable", "multi-sensor device", "health tracker",
                "ml health device", "connected health device",
                "wearable computer", "biomedical sensor array"
            ],
            "environment_field": [
                "digital healthcare", "iot health", "mobile health",
                "telemedicine platform", "health informatics",
                "ubiquitous computing", "pervasive healthcare"
            ]
        }
        print(f"   Enhanced keywords: {len(enhanced_keywords)} categories")
        
        # Step 5: IPC Classification (simulated)
        print("\n5️⃣ IPC Classification...")
        ipc_codes = ["A61B", "G06F", "H04W", "G16H"]
        print(f"   IPC codes: {ipc_codes}")
        
        # Step 6: Query Generation (simulated)
        print("\n6️⃣ Query Generation...")
        search_queries = [
            '"wearable health monitor" AND "biosensor"',
            'IPC:"A61B" AND "continuous monitoring"',
            '"smart wearable" AND "health prediction"',
            '"iot health device" AND "machine learning"'
        ]
        print(f"   Generated {len(search_queries)} search queries")
        
        # Step 7: Patent Search (simulated results)
        print("\n7️⃣ Patent Search...")
        mock_results = [
            {
                "title": "Wearable Health Monitoring System with Multi-Sensor Array",
                "patent_number": "US10123456",
                "abstract": "A wearable device for continuous health monitoring...",
                "similarity_score": 0.85,
                "url": "https://patents.google.com/patent/US10123456"
            },
            {
                "title": "Smart Watch with Integrated Biosensors for Health Tracking",
                "patent_number": "US10234567", 
                "abstract": "An intelligent wearable device with multiple sensors...",
                "similarity_score": 0.78,
                "url": "https://patents.google.com/patent/US10234567"
            }
        ]
        print(f"   Found {len(mock_results)} similar patents")
        
        # Step 8: Evaluation (simulated)
        print("\n8️⃣ Patent Evaluation...")
        final_results = mock_results
        print(f"   Evaluated and ranked {len(final_results)} patents")
        
        # Display results
        print("\n" + "=" * 50)
        print("📊 FINAL RESULTS")
        print("=" * 50)
        
        for i, result in enumerate(final_results, 1):
            print(f"\n{i}. {result['title']}")
            print(f"   Patent Number: {result['patent_number']}")
            print(f"   Similarity Score: {result['similarity_score']:.2f}")
            print(f"   Abstract: {result['abstract'][:100]}...")
            print(f"   URL: {result['url']}")
        
        print(f"\n✅ Patent search completed successfully!")
        print(f"Found {len(final_results)} relevant patents for prior art analysis.")
        
    except Exception as e:
        print(f"❌ Error during workflow execution: {str(e)}")
        print("Note: This example uses simulated data. Real execution requires API keys.")


def demonstrate_individual_nodes():
    """Demonstrate individual node functionality."""
    
    print("\n" + "=" * 50)
    print("🧪 Individual Node Demonstrations")
    print("=" * 50)
    
    # This would demonstrate each node individually
    # For brevity, showing structure only
    
    nodes_info = {
        "Concept Extraction": "Analyzes patent text to extract key technical concepts",
        "Keyword Generation": "Generates search keywords from extracted concepts", 
        "Human Validation": "Allows human review and editing of keywords",
        "Enhancement": "Expands keywords using web search for synonyms",
        "IPC Classification": "Determines patent classification codes",
        "Query Generation": "Creates Boolean search queries for patent databases",
        "Patent Search": "Searches Google Patents using generated queries",
        "Evaluation": "Crawls and evaluates similarity of found patents"
    }
    
    for node, description in nodes_info.items():
        print(f"• {node}: {description}")


if __name__ == "__main__":
    main()
    demonstrate_individual_nodes()
    
    print("\n" + "=" * 50)
    print("🚀 Next Steps:")
    print("1. Configure API keys in .env file")
    print("2. Install dependencies: poetry install")
    print("3. Run with LangGraph Studio for interactive experience")
    print("4. Customize nodes based on your specific requirements")
    print("=" * 50)
