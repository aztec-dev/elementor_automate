from flask import Flask, render_template, request, jsonify
import requests 
import logging
from requests.auth import HTTPBasicAuth
app = Flask(__name__)

@app.route("/")
def index():
    logging.warning("")
    return render_template('index.html')

@app.route("/check_wp_cred", methods=["POST"])
def check_wp_cred():
    """
    Docstring for check_wp_cred:
    checks the users inputted wp credentials and displays basic wp info
    """
    site = request.form['site']
    # site = 'https://upwardconsultingprojects.com.au/'
    username = request.form['username']
    # username = 'upwardAdmin'
    account_password = request.form['account_password']
    # account_password = 'L8rljhSFtBMFV8bxj8nrpU1f'

    endpoint = f"{site}/wp-json/wp/v2/posts?_embed"

    response = requests.get(
        endpoint,
        auth=HTTPBasicAuth(username, account_password)
    )
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({
            "status": response.reason,
            "code": response.status_code
        }), response.status_code
    
if __name__ == "__main__":
    app.run(debug=True)