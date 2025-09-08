"""Flask web application for Patent Search Agent UI."""
import logging
import os
import uuid
import traceback
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from src.patent_search_agent.graph import create_graph
from langgraph.types import Command
from werkzeug.serving import WSGIRequestHandler
WSGIRequestHandler.protocol_version = "HTTP/1.1"  # Enable keep-alive connections

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-123')

# Configure CORS headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Global variable to store the graph instance
graph_app = None
active_sessions = {}

def get_graph():
    """Get or create the graph instance."""
    global graph_app
    if graph_app is None:
        try:
            logger.info("Creating new graph instance...")
            import signal
            from contextlib import contextmanager
            
            @contextmanager
            def timeout(seconds):
                def handler(signum, frame):
                    raise TimeoutError(f"Operation timed out after {seconds} seconds")
                # Set the timeout handler
                old_handler = signal.signal(signal.SIGALRM, handler)
                # Set alarm
                signal.alarm(seconds)
                try:
                    yield
                finally:
                    # Restore the old handler
                    signal.signal(signal.SIGALRM, old_handler)
                    # Disable alarm
                    signal.alarm(0)
            
            try:
                with timeout(30):  # 30 seconds timeout
                    graph_app = create_graph()
                    logger.info("Graph instance created successfully")
            except TimeoutError as te:
                logger.error("Graph creation timed out")
                raise Exception("Graph initialization timed out after 30 seconds")
        except Exception as e:
            logger.error(f"Error creating graph: {e}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to create graph: {str(e)}")
    return graph_app

# Add request logging middleware
@app.before_request
def log_request_info():
    logger.info(f"=== INCOMING REQUEST ===")
    logger.info(f"URL: {request.url}")
    logger.info(f"Method: {request.method}")
    logger.info(f"Path: {request.path}")
    logger.info(f"Headers: {dict(request.headers)}")
    if request.method == 'POST':
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"JSON data: {request.get_json(silent=True)}")
    logger.info("========================")

# Test endpoint
@app.route('/test')
def test():
    """Test endpoint to verify Flask is working."""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'rule': rule.rule,
            'methods': list(rule.methods),
            'endpoint': rule.endpoint
        })
    return jsonify({
        'message': 'Flask app is working!',
        'routes': routes,
        'request_method': request.method
    })

@app.route('/')
def index():
    """Main page with patent search form."""
    logger.info("Index route accessed")
    return render_template('index.html')

@app.route('/start_search', methods=['POST'])
def start_search():
    """Start a new patent search workflow."""
    try:
        logger.info("Received start_search request")
        
        if not request.is_json:
            logger.error("Request is not JSON")
            return jsonify({'error': 'Request must be JSON'}), 400
            
        data = request.get_json()
        logger.info(f"Received data: {data}")
        
        patent_description = data.get('patent_description', '').strip()
        logger.info(f"Patent description length: {len(patent_description)}")
        
        if not patent_description:
            logger.error("Empty patent description")
            return jsonify({'error': 'Patent description is required'}), 400
        
        # Create new session
        thread_id = str(uuid.uuid4())
        logger.info(f"Created thread ID: {thread_id}")
        
        # Initialize workflow
        initial_state = {
            "patent_description": patent_description,
            "max_results": 10,
            "messages": [],
        }
        
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # Get graph instance
            logger.info("Getting graph instance")
            app_instance = get_graph()
            
            # Run until first interrupt
            logger.info("Invoking graph with initial state")
            result = app_instance.invoke(initial_state, config=config)
            logger.info(f"Graph result keys: {result.keys() if result else 'None'}")
            
        except Exception as graph_error:
            logger.error(f"Error in graph processing: {str(graph_error)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': f'Graph processing error: {str(graph_error)}'}), 500
        
        # Store in active sessions
        active_sessions[thread_id] = {
            'current_state': result,
            'workflow_complete': False
        }
        
        if result.get('seed_keywords'):
            logger.info("Successfully extracted keywords")
            seed_keywords = result.get('seed_keywords')
            if hasattr(seed_keywords, 'dict'):
                seed_keywords = seed_keywords.dict()
            return jsonify({
                'thread_id': thread_id,
                'status': 'waiting_validation',
                'seed_keywords': seed_keywords,
            })
        else:
            logger.error("No keywords found in result")
            return jsonify({'error': 'Failed to extract keywords'}), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in start_search: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/validate_keywords', methods=['POST'])
def validate_keywords():
    """Handle user validation of keywords."""
    try:
        data = request.get_json()
        thread_id = data.get('thread_id')
        action = data.get('action')
        keywords = data.get('keywords')
        
        if not thread_id or thread_id not in active_sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        if action not in ['accept', 'reject']:
            return jsonify({'error': 'Invalid action'}), 400
        
        config = {"configurable": {"thread_id": thread_id}}
        app_instance = get_graph()
        
        # Create command based on action
        if action == 'accept':
            command = Command(resume=[{"type": "accept"}])
        else:  # reject
            command = Command(resume=[{"type": "reject"}])
        
        # Continue workflow
        result = app_instance.invoke(command, config=config)
        active_sessions[thread_id]['current_state'] = result
        
        # Return appropriate response
        if result.get('final_queries') or result.get('search_results'):
            active_sessions[thread_id]['workflow_complete'] = True
            return jsonify({
                'status': 'complete',
                'result': {
                    'seed_keywords': result.get('seed_keywords'),
                    'enhanced_keywords': result.get('enhanced_keywords'),
                    'ipc_codes': result.get('ipc_codes'),
                    'final_queries': result.get('final_queries'),
                    'search_results': result.get('search_results')
                }
            })
        else:
            return jsonify({
                'status': 'waiting_validation',
                'seed_keywords': result.get('seed_keywords').dict()
            })
            
    except Exception as e:
        logger.error(f"Error in validate_keywords: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_session_status/<thread_id>')
def get_session_status(thread_id):
    """Get the current status of a search session."""
    logger.info(f"Get session status called for thread: {thread_id}")
    try:
        if thread_id not in active_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = active_sessions[thread_id]
        current_state = session_data.get('current_state', {})
        
        return jsonify({
            'thread_id': thread_id,
            'workflow_complete': session_data.get('workflow_complete', False),
            'patent_description': session_data.get('patent_description'),
            'current_state': {
                'seed_keywords': current_state.get('seed_keywords'),
                'enhanced_keywords': current_state.get('enhanced_keywords'),
                'ipc_codes': current_state.get('ipc_codes'),
                'final_queries': current_state.get('final_queries'),
                'search_results': current_state.get('search_results'),
                'evaluation_scores': current_state.get('evaluation_scores')
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Endpoint not found', 'url': request.url}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)