'''from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO
import gevent
import time
import requests
import socket

# Flask app initialization
app = Flask(__name__)
socketio = SocketIO(app, async_mode='gevent')  # Using gevent as async mode

# Temporary hard-coded user data for login (you can replace this with a database later)
users = {
    "you@example.com": "password123"  # email: password
}

# Firebase Realtime Database setup
FIREBASE_URL = ''  # Replace with your Firebase URL
FIREBASE_SECRET = ''  # Replace with your Firebase secret key

# Function to get Firebase data
def get_firebase_data():
    try:
        response = requests.get(FIREBASE_URL, params={'auth': FIREBASE_SECRET})
        return response.json() if response.status_code == 200 else {}
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving data from Firebase: {e}")
        return {}

# Function to continuously fetch data from Firebase and send updates to frontend
def fetch_data_continuously():
    while True:
        firebase_data = get_firebase_data()
        socketio.emit('firebase_update', firebase_data)  # Emit the data to frontend using WebSocket
        time.sleep(5)  # Fetch data every 5 seconds

# Route for login page
@app.route('/')
def login_page():
    return render_template('login.html')

# Route to handle login form submission
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Check if the user exists and the password matches
    if email in users and users[email] == password:
        return jsonify({"message": "Login successful!"}), 200
    else:
        return jsonify({"message": "Invalid email or password."}), 401

# Route for dashboard (after successful login)
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Function to get the local machine's IP address
def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

# Main section to run the application
if __name__ == "__main__":
    ip_address = get_local_ip()  # Get the machine's IP address
    print(f"Server is running at http://{ip_address}:5000")  # Use port 5000 as in the example
    
    gevent.spawn(fetch_data_continuously)  # Start background thread to fetch data
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)  # Run Flask app on port 5000
'''
'''import logging
import requests
import socket
import time
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from gevent.event import Event
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize Flask app and SocketIO with gevent
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, async_mode='gevent')

# Setup Flask-Limiter for rate limiting
limiter = Limiter(app, key_func=get_remote_address)

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Stop event for background task control
stop_event = Event()

# Firebase Realtime Database setup
FIREBASE_URL = 'https://ml-transport-1-default-rtdb.firebaseio.com/vehicle_data.json'  # Replace with your Firebase URL
FIREBASE_SECRET = 'ItQZCGVw8HvBMKM03oVJKRfZAWAi6112wUHIwdXk'  # Replace with your Firebase secret key

# Temporary hard-coded user data for login (replace with a database later)
users = {
    "you@example.com": "password123"  # email: password
}

# Function to get Firebase data
def get_firebase_data():
    try:
        response = requests.get(FIREBASE_URL, params={'auth': FIREBASE_SECRET})
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to retrieve data from Firebase. Status Code: {response.status_code}")
            return {}
    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving data from Firebase: {e}")
        return {}

# Function to continuously fetch data from Firebase and send updates to frontend
def fetch_data_continuously():
    while not stop_event.is_set():
        firebase_data = get_firebase_data()
        socketio.emit('firebase_update', firebase_data)  # Emit the data to frontend using WebSocket
        stop_event.wait(5)  # Fetch data every 5 seconds

# Route for login page
@app.route('/')
def login_page():
    return render_template('login.html')

# Route to handle login form submission
@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Rate limit: 5 attempts per minute
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Check if the user exists and the password matches
    if email in users and users[email] == password:
        return jsonify({"message": "Login successful!"}), 200
    else:
        return jsonify({"message": "Invalid email or password."}), 401

# Route for dashboard (after successful login)
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Function to get the local machine's IP address
def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

# Start data fetch when the app starts
@app.before_first_request
def start_data_fetch():
    gevent.spawn(fetch_data_continuously)

# Stop data fetch when the app shuts down
@app.teardown_appcontext
def stop_data_fetch(exception=None):
    stop_event.set()

# Main section to run the application
if __name__ == "__main__":
    ip_address = get_local_ip()  # Get the machine's IP address
    logging.info(f"Server is running at http://{ip_address}:5000")  # Use port 5000
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)  # Run Flask app on port 5000
'''
'''import logging
import requests
import socket
import time
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from gevent.event import Event
from flask_cors import CORS
import gevent

# Initialize Flask app and SocketIO with gevent
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, async_mode='gevent')

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Stop event for background task control
stop_event = Event()

# Firebase Realtime Database setup
FIREBASE_URL = 'https://ml-transport-1-default-rtdb.firebaseio.com/vehicle_data.json'  # Replace with your Firebase URL
FIREBASE_SECRET = 'ItQZCGVw8HvBMKM03oVJKRfZAWAi6112wUHIwdXk'  # Replace with your Firebase secret key

# Temporary hard-coded user data for login (replace with a database later)
users = {
    "you@example.com": "password123"  # email: password
}

# Rate limiting logic
login_attempts = {}
BLOCK_TIME = 60  # 1 minute block time for too many attempts
MAX_ATTEMPTS = 5

def rate_limit_check(ip):
    current_time = time.time()
    if ip in login_attempts:
        attempts, first_attempt_time = login_attempts[ip]
        if attempts >= MAX_ATTEMPTS:
            if current_time - first_attempt_time < BLOCK_TIME:
                return False
            else:
                # Reset count after block time expires
                login_attempts[ip] = [0, current_time]
        else:
            login_attempts[ip][0] += 1
    else:
        login_attempts[ip] = [1, current_time]
    return True

# Function to get Firebase data
def get_firebase_data():
    try:
        response = requests.get(FIREBASE_URL, params={'auth': FIREBASE_SECRET})
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to retrieve data from Firebase. Status Code: {response.status_code}")
            return {}
    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving data from Firebase: {e}")
        return {}

# Function to continuously fetch data from Firebase and send updates to frontend
def fetch_data_continuously():
    while not stop_event.is_set():
        firebase_data = get_firebase_data()
        socketio.emit('firebase_update', firebase_data)  # Emit the data to frontend using WebSocket
        stop_event.wait(5)  # Fetch data every 5 seconds

# Route for login page
@app.route('/')
def login_page():
    return render_template('login.html')

# Route to handle login form submission
@app.route('/login', methods=['POST'])
def login():
    ip_address = request.remote_addr
    if not rate_limit_check(ip_address):
        return jsonify({"message": "Too many attempts, try again later."}), 429

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Check if the user exists and the password matches
    if email in users and users[email] == password:
        return jsonify({"message": "Login successful!"}), 200
    else:
        return jsonify({"message": "Invalid email or password."}), 401

# Route for dashboard (after successful login)
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Function to get the local machine's IP address
def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

# Start data fetch when the client connects
@socketio.on('connect')
def start_data_fetch():
    logging.info("Client connected. Starting data fetch.")
    gevent.spawn(fetch_data_continuously)

# Stop data fetch when the app shuts down
@app.teardown_appcontext
def stop_data_fetch(exception=None):
    stop_event.set()

# Main section to run the application
if __name__ == "__main__":
    ip_address = get_local_ip()  # Get the machine's IP address
    logging.info(f"Server is running at http://{ip_address}:5000")  # Use port 5000
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)  # Run Flask app on port 5000
'''
import logging
import requests
import socket
import time
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from gevent.event import Event
from flask_cors import CORS
import gevent

# Initialize Flask app and SocketIO with gevent
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, async_mode='gevent')

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Stop event for background task control
stop_event = Event()

# Firebase Realtime Database setup
FIREBASE_URL = 'https://ml-transport-1-default-rtdb.firebaseio.com/vehicle_data.json'  # Replace with your Firebase URL
FIREBASE_SECRET = 'ItQZCGVw8HvBMKM03oVJKRfZAWAi6112wUHIwdXk'  # Replace with your Firebase secret key

# Temporary hard-coded user data for login (replace with a database later)
users = {
    "you@example.com": "password123"  # email: password
}

# Rate limiting logic
login_attempts = {}
BLOCK_TIME = 60  # 1 minute block time for too many attempts
MAX_ATTEMPTS = 5

def rate_limit_check(ip):
    current_time = time.time()
    if ip in login_attempts:
        attempts, first_attempt_time = login_attempts[ip]
        if attempts >= MAX_ATTEMPTS:
            if current_time - first_attempt_time < BLOCK_TIME:
                return False
            else:
                # Reset count after block time expires
                login_attempts[ip] = [0, current_time]
        else:
            login_attempts[ip][0] += 1
    else:
        login_attempts[ip] = [1, current_time]
    return True

# Function to get Firebase data
def get_firebase_data():
    try:
        response = requests.get(FIREBASE_URL, params={'auth': FIREBASE_SECRET})
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to retrieve data from Firebase. Status Code: {response.status_code}")
            return {}
    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving data from Firebase: {e}")
        return {}

# Function to continuously fetch data from Firebase and send updates to frontend
def fetch_data_continuously():
    while not stop_event.is_set():
        firebase_data = get_firebase_data()
        socketio.emit('firebase_update', firebase_data)  # Emit the data to frontend using WebSocket
        stop_event.wait(5)  # Fetch data every 5 seconds

# Route for login page
@app.route('/')
def login_page():
    return render_template('login.html')

# Route to handle login form submission
@app.route('/login', methods=['POST'])
def login():
    ip_address = request.remote_addr
    if not rate_limit_check(ip_address):
        return jsonify({"message": "Too many attempts, try again later."}), 429

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Check if the user exists and the password matches
    if email in users and users[email] == password:
        return jsonify({"message": "Login successful!"}), 200
    else:
        return jsonify({"message": "Invalid email or password."}), 401

# Route for dashboard (after successful login)
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Function to get the local machine's IP address
def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

# Start data fetch when the client connects
@socketio.on('connect')
def start_data_fetch():
    logging.info("Client connected. Starting data fetch.")
    gevent.spawn(fetch_data_continuously)

# Stop data fetch when the app shuts down
@app.teardown_appcontext
def stop_data_fetch(exception=None):
    stop_event.set()

# Main section to run the application
if __name__ == "__main__":
    ip_address = get_local_ip()  # Get the machine's IP address
    logging.info(f"Server is running at http://{ip_address}:5000")  # Use port 5000
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)  # Run Flask app on port 5000
