import requests
from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

server_url = 'http://<server_ip>:5000'
client_username = 'client'
client_password = 'client_password'

# Authenticate and get token
response = requests.post(f'{server_url}/login', json={'username': client_username, 'password': client_password})
token = response.json().get('access_token')


# SocketIO event handler for receiving JSON data
@socketio.on('new_json_data')
def handle_new_json_data(data):
    print("Received JSON data:", data)
    # wall_trader class, run the trading code here
    # to do


# Connect to the server with the token
if __name__ == '__main__':
    socketio.connect(f'{server_url}?token={token}')
    socketio.run(app, host='0.0.0.0', port=5001)
