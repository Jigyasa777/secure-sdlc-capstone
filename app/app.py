from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, Secure-ish World! This is my Capstone app."

@app.route("/echo")
def echo():
    user_input = request.args.get("msg", "")
    return f"You said: {user_input}"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "admin123":
            return "Welcome to the admin panel (not secure!)"
        else:
            return "Invalid credentials"
    return '''
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    '''

@app.route("/admin")
def admin():
    return "Admin dashboard – needs protection!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
