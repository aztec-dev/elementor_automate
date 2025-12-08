from flask import Flask, render_template, request, jsonify
import requests 
from requests.auth import HTTPBasicAuth
app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/check_wp_cred", methods=["POST"])
def check_wp_cred():
    """
    Docstring for check_wp_cred:
    checks the users inputted wp credentials and displays basic wp info
    """
    site = request.form['site']
    username = request.form['username']
    account_password = request.form['account_password']

    endpoint = f"{site}/wp-json/wp/v2/posts"

    response = requests.get(
        endpoint,
        auth=HTTPBasicAuth(username, account_password)
    )
    if response.status_code == 200:
        return jsonify({
            "status": "success",
            "post_count": len(response.json())
        })
    else:
        return jsonify({
            "status": "failed",
            "code": response.status_code
        }), 401
    
if __name__ == "__main__":
    app.run(debug=True)