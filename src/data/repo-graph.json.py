import json
import os

from GithubAPIHandler import GithubAPIHandler, Repository, UserRepository


def build_repository_json(api_handler: GithubAPIHandler) -> str:
    nodes: list[dict] = []
    links: list[dict] = []

    repository_radius: int = 7
    contributor_radius: int = 10

    repo_list: list[Repository] = api_handler.get_repo_list()
    existing_contributors: set[str] = set()
    for repo in repo_list:
        nodes.append({"id": repo.name, "group": "Repository", "radius": repository_radius})

        contributor_list: list[UserRepository] = api_handler.get_user_contributions(repo.name)
        for contrib in contributor_list:
            if contrib.user_name not in existing_contributors:
                existing_contributors.add(contrib.user_name)
                nodes.append({"id": contrib.user_name, "group": "Contributor", "radius": contributor_radius})
            links.append({"source": contrib.repo_name, "target": contrib.user_name})

    json_obj = {"nodes": nodes, "links": links}

    return json.dumps(json_obj)


def main():
    github_token = os.environ["GITHUB_TOKEN"]
    org_name = "Sydney-Informatics-Hub"
    api_handler = GithubAPIHandler(org_name, github_token)
    json: str = build_repository_json(api_handler)
    print(json)


main()
