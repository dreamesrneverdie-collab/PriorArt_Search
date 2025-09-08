import streamlit as st
from src.patent_search_agent.graph import create_graph
import uuid

st.set_page_config(
    page_title="Patent Search System",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Patent Search System")

def init_session_state():
    if 'thread_id' not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    if 'app' not in st.session_state:
        st.session_state.app = create_graph()
    if 'current_state' not in st.session_state:
        st.session_state.current_state = None
    if 'keywords_generated' not in st.session_state:
        st.session_state.keywords_generated = False

init_session_state()

# Input section
with st.container():
    st.header("Patent Description")
    patent_description = st.text_area(
        "Enter the patent description",
        height=200,
        placeholder="Enter a description of the patent you want to search for..."
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        max_results = st.number_input("Max Results", min_value=1, value=10)
    
    if st.button("Start Search", type="primary"):
        if patent_description:
            # Initialize the search
            initial_state = {
                "patent_description": patent_description,
                "max_results": max_results,
                "messages": [],
            }
            
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            
            with st.spinner("Generating keywords..."):
                st.session_state.current_state = st.session_state.app.invoke(
                    initial_state, 
                    config=config
                )
                st.session_state.keywords_generated = True
                st.rerun()

# Display keywords and validation section
if st.session_state.keywords_generated and st.session_state.current_state:
    st.header("Keywords Validation")
    
    seed_keywords = st.session_state.current_state.get('seed_keywords', {})
    
    if seed_keywords:
        st.subheader("Generated Keywords")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("Problem/Purpose:")
            st.write(", ".join(seed_keywords.get('problem_purpose', [])))
            
        with col2:
            st.write("Object/System:")
            st.write(", ".join(seed_keywords.get('object_system', [])))
            
        with col3:
            st.write("Environment/Field:")
            st.write(", ".join(seed_keywords.get('environment_field', [])))
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Accept Keywords ✅", type="primary"):
                with st.spinner("Processing accepted keywords..."):
                    resume_command = {
                        "type": "accept"
                    }
                    config = {"configurable": {"thread_id": st.session_state.thread_id}}
                    st.session_state.current_state = st.session_state.app.invoke(
                        resume_command,
                        config=config
                    )
                    st.rerun()
        
        with col2:
            if st.button("Reject Keywords ❌"):
                with st.spinner("Regenerating keywords..."):
                    resume_command = {
                        "type": "reject"
                    }
                    config = {"configurable": {"thread_id": st.session_state.thread_id}}
                    st.session_state.current_state = st.session_state.app.invoke(
                        resume_command,
                        config=config
                    )
                    st.rerun()

# Display results section
if st.session_state.current_state and 'search_results' in st.session_state.current_state:
    st.header("Search Results")
    results = st.session_state.current_state.get('search_results', [])
    
    for idx, result in enumerate(results, 1):
        with st.expander(f"Result {idx}: {result.get('title', 'No Title')}"):
            st.write(f"**Patent ID:** {result.get('patent_id', 'N/A')}")
            st.write(f"**Relevance Score:** {result.get('relevance_score', 'N/A')}")
            st.write("**Abstract:**")
            st.write(result.get('abstract', 'No abstract available'))
            if 'url' in result:
                st.markdown(f"[View Patent Details]({result['url']})")

# Display messages/logs
if st.session_state.current_state and st.session_state.current_state.get('messages'):
    with st.expander("Process Logs"):
        for msg in st.session_state.current_state.get('messages', []):
            st.write(msg)
