import requests


def check_github_version():
    """Check NXBrew-dl version on GitHub. Returns version and associated URL"""

    url = "https://api.github.com/repos/bbtufty/nxbrew-dl/releases/latest"
    r = requests.get(url)

    json = r.json()

    # Pull out version and URL
    version = json["name"]
    github_url = json["html_url"]

    return version, github_url
