from flask import Flask, render_template, request


app = Flask(__name__)

# Route for the main homepage
@app.route("/")
def home():
    return render_template("index.html")

# Route for Linux Lab page
@app.route("/linux-lab")
def linux_lab():
    return render_template("linux-lab.html")

# Route for Ansible Lab page
@app.route("/ansible-lab")
def ansible_lab():
    return render_template("ansible-lab.html")


@app.before_request
def log_request_info():
    print(f"Request URL: {request.url}")
    print(f"Request Path: {request.path}")

# Add more routes for other labs...

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
