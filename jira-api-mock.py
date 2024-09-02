# jira-api-mock.py

import os
from flask import Flask, jsonify, request, send_from_directory
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask_swagger_ui import get_swaggerui_blueprint
import logging
from localutils.jira_api_mockup import JiraApiMockup

app = Flask(__name__)
auth = HTTPBasicAuth()

# Ustawienie katalogu logów
log_dir = '/app/data'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Konfiguracja logowania
logging.basicConfig(filename=os.path.join(log_dir, 'jira_api.log'), level=logging.INFO, 
                    format='%(asctime)s %(levelname)s %(message)s')

# Użytkownicy do autoryzacji
users = {
    "admin": generate_password_hash("secret")
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

jira_api = JiraApiMockup()

# Swagger UI setup
SWAGGER_URL = '/swagger'
API_URL = '/swagger.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "JIRA API Mockup"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/swagger.yaml')
def swagger_yaml():
    return send_from_directory('.', 'swagger.yaml')

@app.route('/issues', methods=['GET'])
@auth.login_required
def get_issues():
    """
    Endpoint do pobierania wszystkich zgłoszeń.
    """
    return jira_api.get_issues()

@app.route('/issues/<issue_id>', methods=['GET'])
@auth.login_required
def get_issue(issue_id):
    """
    Endpoint do pobierania szczegółów konkretnego zgłoszenia.

    Args:
        issue_id (str): ID zgłoszenia.
    """
    return jira_api.get_issue(issue_id)

@app.route('/issues', methods=['POST'])
@auth.login_required
def create_issue():
    """
    Endpoint do tworzenia nowego zgłoszenia.
    """
    return jira_api.create_issue()

@app.route('/issues/<issue_id>', methods=['PUT'])
@auth.login_required
def update_issue(issue_id):
    """
    Endpoint do aktualizacji istniejącego zgłoszenia.

    Args:
        issue_id (str): ID zgłoszenia.
    """
    return jira_api.update_issue(issue_id)

@app.route('/issues/<issue_id>', methods=['DELETE'])
@auth.login_required
def delete_issue(issue_id):
    """
    Endpoint do usuwania zgłoszenia.

    Args:
        issue_id (str): ID zgłoszenia.
    """
    return jira_api.delete_issue(issue_id)

@app.route('/projects', methods=['GET'])
@auth.login_required
def get_projects():
    """
    Endpoint do pobierania wszystkich projektów.
    """
    return jira_api.get_projects()

@app.route('/owners', methods=['GET'])
@auth.login_required
def get_owners():
    """
    Endpoint do pobierania wszystkich właścicieli.
    """
    return jira_api.get_owners()

@app.route('/issue_types', methods=['GET'])
@auth.login_required
def get_issue_types():
    """
    Endpoint do pobierania wszystkich typów zgłoszeń.
    """
    return jira_api.get_issue_types()

@app.route('/subtypes', methods=['GET'])
@auth.login_required
def get_subtypes():
    """
    Endpoint do pobierania wszystkich podtypów zgłoszeń.
    """
    return jira_api.get_subtypes()

@app.route('/projects/<project_key>/teams', methods=['POST'])
@auth.login_required
def add_team_to_project(project_key):
    """
    Endpoint do dodawania zespołu do projektu.

    Args:
        project_key (str): Klucz projektu.

    Returns:
        JSON: Zaktualizowane szczegóły projektu lub błąd 404, jeśli projekt nie istnieje.
    """
    data = request.json
    team_name = data.get("team_name")
    team_members = data.get("team_members")
    if not team_name or not team_members:
        return jsonify({"error": "Invalid input"}), 400
    return jira_api.add_team_to_project(project_key, team_name, team_members)

if __name__ == '__main__':
    app.run(debug=True)