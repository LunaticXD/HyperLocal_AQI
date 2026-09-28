from flask import Flask, request

app = Flask(__name__)

@app.route('/data', methods=['POST'])
def receive():

    data = request.json

    print("Received Sensor Data:")
    print(data)

    return {"status": "success"}, 200

if __name__ == '__main__':
    app.run(host='192.168.43.23', port=5000)