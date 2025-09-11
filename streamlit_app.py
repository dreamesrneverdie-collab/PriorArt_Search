import streamlit as st
from src.patent_search_agent.graph import create_graph
import uuid
from langgraph.types import interrupt, Command

st.set_page_config(
    page_title="Patent Search System",
    page_icon="\U0001f50d",
    layout="wide"
)

st.title("\U0001f50d Patent Search System")

def init_session_state():
    if 'thread_id' not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    if 'cancel_event' not in st.session_state:
        st.session_state.cancel_event = False
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
    
    seed_keywords = st.session_state.current_state.get('seed_keywords', {}).dict()
    
    if seed_keywords:
        st.subheader("Generated Keywords")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # st.write("Problem/Purpose:")
            # st.write(", ".join(seed_keywords.get('problem_purpose', [])))
            problem_purpose = st.text_input("Problem/Purpose:", ", ".join(seed_keywords.get('problem_purpose', [])))
            
        with col2:
            # st.write("Object/System:")
            # st.write(", ".join(seed_keywords.get('object_system', [])))
            object_system = st.text_input("Object/System:", ", ".join(seed_keywords.get('object_system', [])))
            
        with col3:
            # st.write("Environment/Field:")
            # st.write(", ".join(seed_keywords.get('environment_field', [])))
            environment_field = st.text_input("Environment/Field:", ", ".join(seed_keywords.get('environment_field', [])))
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Accept Keywords ✅", type="primary"):
                with st.spinner("Processing accepted keywords..."):
                    st.session_state.cancel_event = False
                    resume_command = Command(resume=[{
                        "type": "edit",
                        "args": {
                                "keywords": {
                                    "problem_purpose": problem_purpose.split(", "),
                                    "object_system": object_system.split(", "),
                                    "environment_field": environment_field.split(", ")
                                }
                        }
                    }])
                    config = {"configurable": {"thread_id": st.session_state.thread_id}}
                    st.session_state.current_state = st.session_state.app.invoke(
                        resume_command,
                        config=config
                    )
                    st.rerun()
        
        with col2:
            if st.button("Reject Keywords ❎"):
                with st.spinner("Regenerating keywords..."):
                    st.session_state.cancel_event = False
                    resume_command = Command(resume=[{
                            "type": "reject",
                        }])
                    config = {"configurable": {"thread_id": st.session_state.thread_id}}
                    st.session_state.current_state = st.session_state.app.invoke(
                        resume_command,
                        config=config
                    )
                    st.rerun()
        with col3:
            if st.button("Cancel Workflow ❌"):
                with st.spinner("Canceling Workflow..."):
                    st.session_state.cancel_event = True
                    st.rerun()        st.write("Object/System:")
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
