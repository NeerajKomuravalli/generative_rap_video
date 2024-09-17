import requests
from typing import Tuple

from data_exchange.models import ProjectStatus


def get_project_status(project_name) -> Tuple[bool, ProjectStatus]:
    url = f"http://localhost:8000/project_status/{project_name}"

    # Send a POST request to the endpoint
    response = requests.get(url)
    if response.status_code == 200:
        if response.json()["success"] is True:
            project_status = response.json()["status"]
            return True, ProjectStatus(**project_status)
        else:
            error = response.json()["error"]
            return False, f"Failed to get project status with {error}"
    else:
        return False, f"Failed to get project status with code {response.status_code}"
