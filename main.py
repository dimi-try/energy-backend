import hmac
import hashlib
import time
import os
import urllib.parse
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv


load_dotenv()
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

def validate(hash_str, init_data):
    parsed_query = urllib.parse.parse_qs(init_data)

    init_data = sorted([ chunk.split("=") 
        for chunk in urllib.parse.unquote(init_data).split("&") 
            if chunk[:len("hash=")]!="hash="], key=lambda x: x[0])
    init_data = "\n".join([f"{rec[0]}={rec[1]}" for rec in init_data])

    secret_key = hmac.new("WebAppData".encode(), BOT_TOKEN.encode(), hashlib.sha256 ).digest()
    data_check = hmac.new( secret_key, init_data.encode(), hashlib.sha256)

    return data_check.hexdigest() == hash_str


app = Flask(__name__)

CORS(app, resources={r"/auth/*": {"origins": "*"}})

@app.route('/auth/verify', methods=['POST'])
def authorization_test():
    authorization_data = request.json
    
    parsed_query = urllib.parse.parse_qs(authorization_data)
    hash_received = parsed_query.get('hash', [None])[0]
    auth_date = int(parsed_query.get('auth_date', 0)[0])

    if not hash_received:
        return jsonify({'success': False, 'message': 'Hash not provided'}), 400

    if validate(hash_received, authorization_data):
        current_unix_time = int(time.time())
        timeout_seconds = 3600 
        if current_unix_time - auth_date > timeout_seconds:
            return jsonify({'success': False, 'message': 'Verification failed due to timeout'}), 403
        return jsonify({'success': True, 'message': 'Verification successful'})
    else:
        return jsonify({'success': False, 'message': 'Verification failed'}), 403


if __name__ == '__main__':
    app.run(debug=True)