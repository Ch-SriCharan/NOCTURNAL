from flask import Flask, render_template
import subprocess

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/call")
def call_patient():
    subprocess.Popen(["python3", "offline_ivr.py"])
    return "📞 Calling patient..."

if __name__ == "__main__":
    app.run(port=5000, debug=True)