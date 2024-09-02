# localutils/jira_api_mockup.py

import random
import json
import os
import logging
from flask import jsonify, request

DATA_FILE = 'jira_data.json'

class JiraApiMockup:
    """
    Klasa JiraApiMockup symuluje API JIRA do zarządzania zgłoszeniami, projektami i właścicielami.
    """

    def __init__(self):
        """
        Inicjalizuje instancję JiraApiMockup i ładuje dane z pliku JSON.
        """
        self.load_data()

    def load_data(self):
        """
        Ładuje dane z pliku JSON, jeśli istnieje. W przeciwnym razie inicjalizuje przykładowe dane.
        """
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as file:
                data = json.load(file)
                self.projects = data.get('projects', [])
                self.owners = data.get('owners', [])
                self.issues = data.get('issues', [])
        else:
            self.owners = [f"user{i}" for i in range(1, 21)]
            self.projects = [{"key": f"PROJ-{i}", "name": f"Project {i}", "teams": self.generate_teams()} for i in range(1, 11)]
            self.issues = [
                {
                    "id": "JIRA-1",
                    "title": "Issue 1",
                    "description": "Description for issue 1",
                    "status": "Open",
                    "assignee": random.choice(self.owners),
                    "project_key": random.choice(self.projects)["key"],
                    "type": "task"
                },
                {
                    "id": "JIRA-2",
                    "title": "Issue 2",
                    "description": "Description for issue 2",
                    "status": "In Progress",
                    "assignee": random.choice(self.owners),
                    "project_key": random.choice(self.projects)["key"],
                    "type": "task"
                }
            ]
        self.issue_types = ["task", "bug", "feature", "improvement", "epic"]
        self.subtypes = ["security", "performance", "usability", "compatibility", "other"]

    def generate_teams(self):
        """
        Generuje dwie drużyny ("infra" i "devs") z trzema losowymi członkami każda.
        """
        random.shuffle(self.owners)
        return {
            "infra": random.sample(self.owners, 3),
            "devs": random.sample(self.owners, 3)
        }

    def add_team_to_project(self, project_key, team_name, team_members):
        """
        Dodaje zespół do projektu na podstawie klucza projektu.

        Args:
            project_key (str): Klucz projektu.
            team_name (str): Nazwa zespołu.
            team_members (list): Lista członków zespołu.

        Returns:
            JSON: Zaktualizowane szczegóły projektu lub błąd 404, jeśli projekt nie istnieje.
        """
        logging.info(f"Adding team '{team_name}' to project '{project_key}'")
        project = next((project for project in self.projects if project["key"] == project_key), None)
        if project:
            if "teams" not in project:
                project["teams"] = {}
            project["teams"][team_name] = team_members
            self.save_data()
            logging.info(f"Team '{team_name}' added to project '{project_key}'")
            return jsonify(project)
        else:
            logging.warning(f"Attempt to add team to non-existent project with key: {project_key}")
            return jsonify({"error": "Project not found"}), 404

    def save_data(self):
        """
        Zapisuje aktualne dane do pliku JSON.
        """
        data = {
            'projects': self.projects,
            'owners': self.owners,
            'issues': self.issues
        }
        with open(DATA_FILE, 'w') as file:
            json.dump(data, file)

    def get_issues(self):
        """
        Zwraca listę wszystkich zgłoszeń w formacie JSON.
        """
        logging.info("Fetching all issues")
        return jsonify(self.issues)

    def get_issue(self, issue_id):
        """
        Zwraca szczegóły konkretnego zgłoszenia na podstawie jego ID.

        Args:
            issue_id (str): ID zgłoszenia.

        Returns:
            JSON: Szczegóły zgłoszenia lub błąd 404, jeśli zgłoszenie nie istnieje.
        """
        logging.info(f"Fetching issue with ID: {issue_id}")
        issue = next((issue for issue in self.issues if issue["id"] == issue_id), None)
        if issue:
            return jsonify(issue)
        else:
            return jsonify({"error": "Issue not found"}), 404

    def create_issue(self):
        """
        Tworzy nowe zgłoszenie na podstawie danych z żądania.

        Returns:
            JSON: Szczegóły nowo utworzonego zgłoszenia lub błąd 400, jeśli dane są nieprawidłowe.
        """
        new_issue = request.json
        if new_issue.get("type") not in self.issue_types:
            logging.warning("Attempt to create issue with invalid type")
            return jsonify({"error": "Invalid issue type"}), 400
        if "subtype" in new_issue and new_issue.get("subtype") not in self.subtypes:
            logging.warning("Attempt to create issue with invalid subtype")
            return jsonify({"error": "Invalid issue subtype"}), 400
        new_issue["id"] = f"JIRA-{len(self.issues) + 1}"
        self.issues.append(new_issue)
        self.save_data()
        logging.info(f"Issue created with ID: {new_issue['id']}")
        return jsonify(new_issue), 201

    def update_issue(self, issue_id):
        """
        Aktualizuje istniejące zgłoszenie na podstawie jego ID i danych z żądania.

        Args:
            issue_id (str): ID zgłoszenia.

        Returns:
            JSON: Zaktualizowane szczegóły zgłoszenia lub błąd 404, jeśli zgłoszenie nie istnieje.
        """
        logging.info(f"Updating issue with ID: {issue_id}")
        issue = next((issue for issue in self.issues if issue["id"] == issue_id), None)
        if issue:
            data = request.json
            issue.update(data)
            self.save_data()
            logging.info(f"Issue with ID: {issue_id} updated")
            return jsonify(issue)
        else:
            logging.warning(f"Attempt to update non-existent issue with ID: {issue_id}")
            return jsonify({"error": "Issue not found"}), 404

    def delete_issue(self, issue_id):
        """
        Usuwa zgłoszenie na podstawie jego ID.

        Args:
            issue_id (str): ID zgłoszenia.

        Returns:
            str: Pusty ciąg znaków z kodem statusu 204.
        """
        logging.info(f"Deleting issue with ID: {issue_id}")
        self.issues = [issue for issue in self.issues if issue["id"] != issue_id]
        self.save_data()
        logging.info(f"Issue with ID: {issue_id} deleted")
        return '', 204

    def get_projects(self):
        """
        Zwraca listę wszystkich projektów w formacie JSON.
        """
        logging.info("Fetching all projects")
        return jsonify(self.projects)

    def get_owners(self):
        """
        Zwraca listę wszystkich właścicieli w formacie JSON.
        """
        logging.info("Fetching all owners")
        return jsonify(self.owners)

    def get_issue_types(self):
        """
        Zwraca listę wszystkich typów zgłoszeń w formacie JSON.
        """
        logging.info("Fetching all issue types")
        return jsonify(self.issue_types)

    def get_subtypes(self):
        """
        Zwraca listę wszystkich podtypów zgłoszeń w formacie JSON.
        """
        logging.info("Fetching all subtypes")
        return jsonify(self.subtypes)