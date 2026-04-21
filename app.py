from flask import Flask, render_template, jsonify
from q_learning import train, env, q_table
import numpy as np

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/train")
def start_train():
    train(500)
    return jsonify({"message":"Training Complete"})

@app.route("/run")
def run_model():
    state = env.reset()
    floor, req = state

    action = int(np.argmax(q_table[floor][req]))

    actions = ["UP","DOWN","STAY","OPEN"]

    return jsonify({
        "current_floor": floor,
        "request_floor": req,
        "action": actions[action]
    })

if __name__ == "__main__":
    app.run(debug=True)