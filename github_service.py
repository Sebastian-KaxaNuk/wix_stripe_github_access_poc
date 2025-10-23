import requests
from config import GITHUB_OWNER, GITHUB_REPO, GITHUB_PAT

#%%

def add_collaborator(
        github_username: str,
        permission: str = "pull"
) -> tuple[bool, str]:
    """
    Invita a un usuario al repositorio privado.
    """
    if not github_username:
        return False, "Empty GitHub username"

    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/collaborators/{github_username}"
    headers = {
        "Authorization": f"Bearer {GITHUB_PAT}",
        "Accept": "application/vnd.github+json"
    }
    data = {"permission": permission}
    resp = requests.put(url, json=data, headers=headers, timeout=15)

    if resp.status_code in (201, 204):
        return True, f"Access granted to {github_username}."
    else:
        return False, f"GitHub API error {resp.status_code}: {resp.text}"
