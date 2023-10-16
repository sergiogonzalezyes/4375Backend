from server import app


@app.route("/")
def home():
    return "Hello, World!"
    

@app.route("/dashboard")
def api():
    return "Hello from localhost 5000!"