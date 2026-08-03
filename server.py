from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATA = {}

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    return jsonify({'success': True, 'players': list(DATA.values())})

@app.route('/api/leaderboard/update', methods=['POST'])
def update_leaderboard():
    data = request.json
    DATA[data['user_id']] = data
    return jsonify({'success': True})

@app.route('/api/trades', methods=['GET'])
def get_trades():
    return jsonify({'success': True, 'trades': []})

@app.route('/api/trades/create', methods=['POST'])
def create_trade():
    return jsonify({'success': True})

@app.route('/api/trades/buy', methods=['POST'])
def buy_trade():
    return jsonify({'success': True})

@app.route('/api/trades/cancel', methods=['POST'])
def cancel_trade():
    return jsonify({'success': True})

@app.route('/api/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    return jsonify({'success': True, 'profile': DATA.get(user_id, {})})

@app.route('/api/profile/save', methods=['POST'])
def save_profile():
    data = request.json
    DATA[data['user_id']] = data
    return jsonify({'success': True})

@app.route('/api')
def home():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
