from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Хранилище в памяти
leaderboard = {}
trades = {}
profiles = {}

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    players = list(leaderboard.values())
    players.sort(key=lambda x: x.get('wood', 0), reverse=True)
    return jsonify({'success': True, 'players': players[:100]})

@app.route('/api/leaderboard/update', methods=['POST'])
def update_leaderboard():
    data = request.json
    user_id = data.get('user_id')
    if user_id:
        leaderboard[user_id] = {
            'user_id': user_id,
            'name': data.get('name', 'Игрок'),
            'wood': data.get('wood', 0),
            'crystals': data.get('crystals', 0),
            'treeLevel': data.get('treeLevel', 1),
            'totalTrees': data.get('totalTrees', 0)
        }
    return jsonify({'success': True, 'count': len(leaderboard)})

@app.route('/api/trades', methods=['GET'])
def get_trades():
    user_id = request.args.get('user_id', '')
    result = []
    for t in trades.values():
        if not t.get('targetId') or t['targetId'] == user_id:
            result.append(t)
    return jsonify({'success': True, 'trades': result})

@app.route('/api/trades/create', methods=['POST'])
def create_trade():
    data = request.json
    trade_id = str(len(trades) + 1)
    trades[trade_id] = {
        'id': trade_id,
        'sellerId': data.get('sellerId'),
        'sellerName': data.get('sellerName'),
        'targetId': data.get('targetId'),
        'skinId': data.get('skinId'),
        'skinName': data.get('skinName'),
        'skinEmoji': data.get('skinEmoji'),
        'price': data.get('price', 0)
    }
    return jsonify({'success': True, 'trade': trades[trade_id]})

@app.route('/api/trades/buy', methods=['POST'])
def buy_trade():
    data = request.json
    trade_id = data.get('trade_id')
    if trade_id in trades:
        trade = trades.pop(trade_id)
        return jsonify({'success': True, 'sellerId': trade['sellerId'], 'price': trade['price'], 'skinId': trade['skinId']})
    return jsonify({'success': False, 'error': 'Торг не найден'}), 404

@app.route('/api/trades/cancel', methods=['POST'])
def cancel_trade():
    data = request.json
    trade_id = data.get('trade_id')
    if trade_id in trades:
        del trades[trade_id]
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Торг не найден'}), 404

@app.route('/api/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    return jsonify({'success': True, 'profile': profiles.get(user_id, {})})

@app.route('/api/profile/save', methods=['POST'])
def save_profile():
    data = request.json
    user_id = data.get('user_id')
    if user_id:
        profiles[user_id] = data
    return jsonify({'success': True})

@app.route('/api/ping', methods=['GET'])
def ping():
    """Эндпоинт для проверки что сервер жив"""
    return jsonify({'status': 'ok', 'players': len(leaderboard), 'trades': len(trades)})

@app.route('/')
def home():
    return jsonify({'status': 'ok', 'message': 'Дровосек-кликер API v2.0'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
