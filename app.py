"""
Flask Web Interface for GitHubProfileBot
Provides a simple web UI for interacting with Claude-powered bot
"""

from flask import Flask, render_template, request, jsonify, Response
import os
import json

# Try to use Claude bot first, fall back to rule-based bot
try:
    from claude_bot import ClaudePortfolioBot
    bot = ClaudePortfolioBot(portfolio_data_path="portfolio_data.json")
    bot_type = "claude"
except (ImportError, ValueError):
    from github_profile_bot import GitHubProfileBot
    bot = GitHubProfileBot(portfolio_data_path="portfolio_data.json")
    bot_type = "rule-based"

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

@app.route('/')
def index():
    """Serve the main chatbot page."""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint for bot queries."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Empty query'}), 400
        
        if bot_type == "claude":
            # Stream response for Claude
            response = bot.chat(query, stream=False)
        else:
            # Use rule-based bot response
            response = bot.answer_query(query)
        
        return jsonify({
            'query': query,
            'response': response,
            'success': True,
            'bot_type': bot_type
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """Streaming API endpoint for Claude."""
    if bot_type != "claude":
        return jsonify({'error': 'Streaming only available with Claude bot'}), 400
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Empty query'}), 400
        
        def generate():
            for chunk in bot.chat(query, stream=True):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/info/developer')
def get_developer_info():
    """Get developer information."""
    if bot_type == "claude":
        info = bot.portfolio_data.get('developer', {})
        return jsonify(info)
    else:
        return jsonify(bot.about_developer())

@app.route('/api/info/skills')
def get_skills():
    """Get skills information."""
    return jsonify(bot.get_skills_summary())

@app.route('/api/projects')
def get_projects():
    """Get all projects."""
    return jsonify([
        {
            'id': p['id'],
            'name': p.get('name'),
            'subtitle': p.get('subtitle'),
            'type': p.get('type')
        }
        for p in bot.portfolio_data.get('projects', [])
    ])

@app.route('/api/projects/<int:project_id>')
def get_project(project_id):
    """Get specific project details."""
    project = bot.projects.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    return jsonify(project)

@app.route('/api/roadmap/<focus>')
def get_roadmap(focus):
    """Get learning roadmap for a specific area."""
    roadmap = bot.learning_roadmap(focus)
    return jsonify({'roadmap': roadmap})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
