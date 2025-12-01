from flask import Flask, request, jsonify
import random

app = Flask(__name__)

@app.route('/model/api/predict', methods=['GET'])
def get_random_number():
    x=request.args.get('x')
    y=request.args.get('y')
    z=request.args.get('z')
    eda=request.args.get('eda')
    hr=request.args.get('hr')
    temp=request.args.get('temp')
    random_int = random.randint(0, 2)
    response = {
            "stress_level_prediction": str(random_int)
        }

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)