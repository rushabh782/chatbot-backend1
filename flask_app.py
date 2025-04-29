from flask import Flask, request, jsonify
from api_handler import get_recommendations

app = Flask(__name__)

@app.route('/api/recommendations', methods=['POST'])
def recommendations():
    data = request.get_json()
    query = data.get('query')
    
    if not query:
        return jsonify({'success': False, 'error': 'Query is required'}), 400
    
    result = get_recommendations(query)
    
    if not result.get('success', True):
        return jsonify(result), 500

    return jsonify(result)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Flask API is running'})
