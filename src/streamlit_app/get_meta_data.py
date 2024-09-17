import requests

from data_exchange.models import ProjectData


def get_metadata(project_name: str):
    # Create meta data
    url = f"http://localhost:8000/get_metadata/{project_name}"

    # Send a GET request to the endpoint
    response = requests.get(url)

    # Check the response
    if response.status_code == 200:
        if response.json()["success"] is True:
            return True, ProjectData(**response.json()["metadata"])
        else:
            error = response.json()["error"]
            return False, f"Failed to get metadata with {error}"
    else:
        return (
            False,
            f"Failed to get metadata with status code {response.status_code}",
        )
