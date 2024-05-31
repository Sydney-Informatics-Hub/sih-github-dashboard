import dataclasses
import os
import sys

from pandas import DataFrame

from GithubAPIHandler import GithubAPIHandler, Repository


def build_repository_table(api_handler: GithubAPIHandler) -> DataFrame:
    repo_info: dict = {field.name: [] for field in dataclasses.fields(Repository)}

    repo_list: list[Repository] = api_handler.get_repo_list()
    for repo in repo_list:
        repo_dict = dataclasses.asdict(repo)
        for attr in repo_dict:
            attr_value = repo_dict[attr]
            repo_info[attr].append(attr_value)

    return DataFrame(repo_info)


def main():
    github_token = os.environ["GITHUB_TOKEN"]
    org_name = "Sydney-Informatics-Hub"
    api_handler = GithubAPIHandler(org_name, github_token)
    df: DataFrame = build_repository_table(api_handler)
    df.to_csv(sys.stdout, index=False)


main()
