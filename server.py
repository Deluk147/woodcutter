from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Простое файловое хранилище (замените на базу данных в продакшене)
DATA_DIR = 'data'

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ============ API для рейтинга ============

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Получить таблицу лидеров"""
    lb = load_json('leaderboard.json')
    # Преобразуем в список и сортируем
    players = list(lb.values())
    players.sort(key=lambda x: x.get('wood', 0), reverse=True)
    return jsonify({'success': True, 'players': players[:100]})

@app.route('/api/leaderboard/update', methods=['POST'])
def update_leaderboard():
    """Обновить данные игрока в рейтинге"""
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'error': 'user_id required'}), 400
    
    lb = load_json('leaderboard.json')
    lb[user_id] = {
        'user_id': user_id,
        'name': data.get('name', 'Игрок'),
        'wood': data.get('wood', 0),
        'crystals': data.get('crystals', 0),
        'treeLevel': data.get('treeLevel', 1),
        'totalTrees': data.get('totalTrees', 0),
        'lastUpdated': datetime.now().isoformat()
    }
    save_json('leaderboard.json', lb)
    
    return jsonify({'success': True})

# ============ API для торгов ============

@app.route('/api/trades', methods=['GET'])
def get_trades():
    """Получить список торгов для игрока"""
    user_id = request.args.get('user_id', '')
    trades = load_json('trades.json')
    
    # Фильтруем: общие + прямые для этого игрока
    trade_list = []
    for trade in trades.values():
        target = trade.get('targetId')
        if not target or target == user_id:
            trade_list.append(trade)
    
    trade_list.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
    return jsonify({'success': True, 'trades': trade_list})

@app.route('/api/trades/create', methods=['POST'])
def create_trade():
    """Создать новое предложение"""
    data = request.json
    trade_id = str(int(datetime.now().timestamp() * 1000))
    
    trades = load_json('trades.json')
    trades[trade_id] = {
        'id': trade_id,
        'sellerId': data.get('sellerId'),
        'sellerName': data.get('sellerName', 'Игрок'),
        'targetId': data.get('targetId'),  # null = общий рынок
        'skinId': data.get('skinId'),
        'skinName': data.get('skinName'),
        'skinEmoji': data.get('skinEmoji'),
        'price': data.get('price', 0),
        'createdAt': datetime.now().isoformat()
    }
    save_json('trades.json', trades)
    
    return jsonify({'success': True, 'trade': trades[trade_id]})

@app.route('/api/trades/buy', methods=['POST'])
def buy_trade():
    """Купить скин"""
    data = request.json
    trade_id = data.get('trade_id')
    buyer_id = data.get('buyer_id')
    
    trades = load_json('trades.json')
    trade = trades.get(trade_id)
    
    if not trade:
        return jsonify({'success': False, 'error': 'Торг не найден'}), 404
    
    if trade['sellerId'] == buyer_id:
        return jsonify({'success': False, 'error': 'Нельзя купить свой скин'}), 400
    
    if trade.get('targetId') and trade['targetId'] != buyer_id:
        return jsonify({'success': False, 'error': 'Скин предназначен другому игроку'}), 403
    
    # Удаляем торг
    del trades[trade_id]
    save_json('trades.json', trades)
    
    # Возвращаем информацию о продавце для перевода средств
    return jsonify({
        'success': True,
        'sellerId': trade['sellerId'],
        'price': trade['price'],
        'skinId': trade['skinId']
    })

@app.route('/api/trades/cancel', methods=['POST'])
def cancel_trade():
    """Отменить своё предложение"""
    data = request.json
    trade_id = data.get('trade_id')
    user_id = data.get('user_id')
    
    trades = load_json('trades.json')
    trade = trades.get(trade_id)
    
    if not trade:
        return jsonify({'success': False, 'error': 'Торг не найден'}), 404
    
    if trade['sellerId'] != user_id:
        return jsonify({'success': False, 'error': 'Не ваш торг'}), 403
    
    del trades[trade_id]
    save_json('trades.json', trades)
    
    return jsonify({'success': True})

# ============ API для профиля ============

@app.route('/api/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    """Получить профиль игрока"""
    profiles = load_json('profiles.json')
    profile = profiles.get(user_id, {'wood': 0, 'crystals': 0})
    return jsonify({'success': True, 'profile': profile})

@app.route('/api/profile/save', methods=['POST'])
def save_profile():
    """Сохранить профиль игрока"""
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'error': 'user_id required'}), 400
    
    profiles = load_json('profiles.json')
    profiles[user_id] = {
        'wood': data.get('wood', 0),
        'crystals': data.get('crystals', 0),
        'stars': data.get('stars', 0),
        'axePower': data.get('axePower', 1),
        'autoWood': data.get('autoWood', 0),
        'critChance': data.get('critChance', 0),
        'critMultiplier': data.get('critMultiplier', 2.0),
        'crystalToWoodRate': data.get('crystalToWoodRate', 0),
        'comboBonus': data.get('comboBonus', 0),
        'treeHP': data.get('treeHP', 15),
        'maxTreeHP': data.get('maxTreeHP', 15),
        'totalTrees': data.get('totalTrees', 0),
        'treeLevel': data.get('treeLevel', 1),
        'activeSkin': data.get('activeSkin', 'default'),
        'ownedSkins': data.get('ownedSkins', ['default']),
        'upgrades': data.get('upgrades', {}),
        'lastUpdated': datetime.now().isoformat()
    }
    save_json('profiles.json', profiles)
    
    return jsonify({'success': True})

@app.route('/')
def home():
    return jsonify({'status': 'ok', 'message': 'Дровосек-кликер API работает!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)