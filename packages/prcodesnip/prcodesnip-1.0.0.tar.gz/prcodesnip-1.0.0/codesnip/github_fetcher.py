import requests

def fetch_pr_data(repo, pr_number, token):
    headers = {"Authorization": f"token {token}"}
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    response = requests.get(url, headers=headers)
    pr = response.json()
    return {
        "title": pr.get("title", ""),
        "body": pr.get("body", ""),
        "diff_url": pr.get("diff_url", "")
    }
