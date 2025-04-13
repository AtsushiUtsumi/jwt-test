from flask import Flask, request, jsonify, make_response, render_template
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required, set_access_cookies, unset_jwt_cookies
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# JWTの設定
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')  # 本番環境では必ず環境変数から取得してください
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  # 開発環境ではFalse、本番環境ではTrueに設定
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

jwt = JWTManager(app)

# テスト用のユーザー情報（実際のアプリケーションではデータベースを使用してください）
USERS = {
    'user@example.com': {
        'password': 'password123',
        'name': 'Test User'
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    if not email or not password:
        return jsonify({'msg': 'メールアドレスとパスワードを入力してください'}), 400

    user = USERS.get(email)
    if not user or user['password'] != password:
        return jsonify({'msg': 'メールアドレスまたはパスワードが間違っています'}), 401

    # アクセストークンの作成
    access_token = create_access_token(identity=email)
    
    # レスポンスの作成
    response = jsonify({'msg': 'ログインに成功しました', 'user': user['name']})
    # クッキーにトークンを設定
    set_access_cookies(response, access_token)
    
    return response

@app.route('/logout', methods=['POST'])
def logout():
    response = jsonify({'msg': 'ログアウトしました'})
    unset_jwt_cookies(response)
    return response

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    user_info = USERS.get(current_user)
    return jsonify({
        'msg': 'アクセストークンは有効です',
        'user': user_info['name'],
        'email': current_user
    })

if __name__ == '__main__':
    app.run(debug=True)