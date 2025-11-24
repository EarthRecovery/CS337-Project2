from flask import Flask, render_template, request, jsonify, session
from project.parser import Parser
from project.qa import QA
import os
import re

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Store QA instances per session
qa_instances = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/load_recipe', methods=['POST'])
def load_recipe():
    """Load a recipe from URL"""
    data = request.json
    url = data.get('url', '')

    # Basic URL validation which can accept any valid HTTP/HTTPS URL
    pattern = r'^https?://.*$'
    if not re.match(pattern, url):
        return jsonify({'error': 'Invalid URL. Please provide a valid URL starting with http:// or https://'}), 400

    try:
        # Create new QA instance
        qa = QA()
        qa.model = Parser(url).parse()
        qa.max_step = len(qa.model["Steps"])

        # Store in session
        session_id = session.get('session_id', os.urandom(16).hex())
        session['session_id'] = session_id
        qa_instances[session_id] = qa

        return jsonify({
            'success': True,
            'dish_name': qa.model['dish_name'],
            'dish_intro': qa.model['dish_intro'],
            'prep_time': qa.model['prep_time'],
            'cook_time': qa.model['cook_time'],
            'total_time': qa.model['total_time'],
            'serving': qa.model['serving']
        })
    except Exception as e:
        return jsonify({'error': f'Error parsing recipe: {str(e)}'}), 500

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Process a question from the user"""
    data = request.json
    question = data.get('question', '')

    session_id = session.get('session_id')
    if not session_id or session_id not in qa_instances:
        return jsonify({'error': 'No recipe loaded. Please load a recipe first.'}), 400

    qa = qa_instances[session_id]

    # Parse and process question
    q_data = qa.question_parser(question)

    # Capture output from agent
    import io
    import sys
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    status = qa.agent(q_data)

    sys.stdout = old_stdout
    response_text = captured_output.getvalue()

    # Update history
    qa._add_to_history(q_data)

    return jsonify({
        'response': response_text.strip(),
        'current_step': qa.current_step,
        'question_type': q_data['type'].name,
        'exit': status == -1
    })

@app.route('/api/get_state', methods=['GET'])
def get_state():
    """Get current state of the QA system"""
    session_id = session.get('session_id')
    if not session_id or session_id not in qa_instances:
        return jsonify({'error': 'No recipe loaded.'}), 400

    qa = qa_instances[session_id]

    return jsonify({
        'current_step': qa.current_step,
        'max_step': qa.max_step,
        'dish_name': qa.model['dish_name']
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)