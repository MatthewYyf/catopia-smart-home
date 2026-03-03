from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/devices', methods=['GET'])
def devices():
    return

@app.route('/cat', methods=['GET'])
def get_cat():
    return

@app.route('/config', methods=['GET'])
def get_config():
    return

@app.route('/events', methods=['POST'])
def post_events():
    return

@app.route('/commands', methods=['POST'])
def post_commands():
    return

if __name__ == '__main__':
    app.run(debug=True)
