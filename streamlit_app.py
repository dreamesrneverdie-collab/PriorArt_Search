import streamlit as st
import json
from src.patent_search_agent.graph import run_patent_search
from langgraph.types import Command

st.set_page_config(
    page_title="Patent Search System",
    page_icon="🔍",
    layout="wide"
)

def main():
    st.title("🔍 Patent Search System")
    
    # Input for patent description
    st.subheader("Enter Patent Description")
    patent_description = st.text_area(
        "Describe the patent you want to search for",
        height=200,
        help="Enter a detailed description of the patent concept you want to search for."
    )
    
    # Model selection
    model_name = st.selectbox(
        "Select Model",
        ["qwen3:4b-instruct-2507-fp16"],
        help="Select the model to use for the search"
    )
    
    # Number of results
    max_results = st.slider(
        "Maximum Results",
        min_value=5,
        max_value=50,
        value=10,
        help="Select the maximum number of results to return"
    )
    
    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'thread_config' not in st.session_state:
        st.session_state.thread_config = None
    
    # Start search button
    if st.button("Start Search") and patent_description:
        with st.spinner("Starting patent search..."):
            try:
                # Initial search
                result = run_patent_search(
                    patent_description=patent_description,
                    max_results=max_results,
                    model_name=model_name
                )
                st.session_state.result = result
                st.session_state.step = 2
                
                # Display initial keywords
                if 'seed_keywords' in result:
                    display_keywords(result['seed_keywords'])
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
    # Display keyword validation interface if we have results
    if st.session_state.step == 2 and st.session_state.result:
        st.subheader("Keyword Validation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Accept Keywords"):
                with st.spinner("Processing..."):
                    example2 = Command(resume=[{"type": "accept"}])
                    result = run_patent_search(
                        patent_description=patent_description,
                        max_results=max_results,
                        model_name=model_name
                    )
                    st.session_state.result = result
                    st.session_state.step = 3
        
        with col2:
            if st.button("❌ Reject Keywords"):
                with st.spinner("Processing..."):
                    example3 = Command(resume=[{"type": "reject"}])
                    result = run_patent_search(
                        patent_description=patent_description,
                        max_results=max_results,
                        model_name=model_name
                    )
                    st.session_state.result = result
                    display_keywords(result.get('seed_keywords'))
    
    # Display final results
    if st.session_state.step == 3 and st.session_state.result:
        display_final_results(st.session_state.result)

def display_keywords(keywords):
    if not keywords:
        return
    
    st.subheader("Generated Keywords")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("Problem/Purpose:")
        for kw in keywords.get('problem_purpose', []):
            st.write(f"- {kw}")
            
    with col2:
        st.write("Object/System:")
        for kw in keywords.get('object_system', []):
            st.write(f"- {kw}")
            
    with col3:
        st.write("Environment/Field:")
        for kw in keywords.get('environment_field', []):
            st.write(f"- {kw}")

def display_final_results(result):
    st.subheader("Search Results")
    
    # Display messages
    if 'messages' in result:
        for msg in result['messages']:
            st.write(msg)
    
    # Display any other relevant information from the result
    if 'patents' in result:
        for patent in result['patents']:
            with st.expander(f"Patent: {patent.get('title', 'Untitled')}"):
                st.write(f"ID: {patent.get('id', 'N/A')}")
                st.write(f"Abstract: {patent.get('abstract', 'N/A')}")
                if patent.get('link'):
                    st.markdown(f"[View Patent]({patent['link']})")

if __name__ == "__main__":
    main()
