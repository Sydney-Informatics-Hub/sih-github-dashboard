import dataclasses
import os
import sys

from pandas import DataFrame

from GithubAPIHandler import GithubAPIHandler, UserRepository, Repository


def build_contributions_table(api_handler: GithubAPIHandler) -> DataFrame:
    contrib_info: dict = {field.name: [] for field in dataclasses.fields(UserRepository)}

    repo_list: list[Repository] = api_handler.get_repo_list()
    for repo in repo_list:
        user_contribs: list[UserRepository] = api_handler.get_user_contributions(repo.name)
        for contrib in user_contribs:
            contrib_dict = dataclasses.asdict(contrib)
            for attr in contrib_dict:
                attr_value = contrib_dict[attr]
                contrib_info[attr].append(attr_value)

    return DataFrame(contrib_info)


def main():
    github_token = os.environ["GITHUB_TOKEN"]
    org_name = "Sydney-Informatics-Hub"
    api_handler = GithubAPIHandler(org_name, github_token)
    df: DataFrame = build_contributions_table(api_handler)
    df.to_csv(sys.stdout, index=False)


main()
