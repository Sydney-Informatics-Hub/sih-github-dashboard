from dataclasses import dataclass
from functools import cache

from requests import Response, Session


@dataclass
class Repository:
    name: str
    description: str
    url: str


@dataclass
class UserRepository:
    repo_name: str
    user_name: str
    user_url: str
    avatar_url: str
    contributions: int


class GithubAPIHandler:
    ROOT_PATH: str = "https://api.github.com"

    def __init__(self, org_name: str, token: str):
        self.org_name: str = org_name
        self.session: Session = Session()
        self.session.headers.update({"Authorization": f"Bearer {token}", "X-GitHub-Api-Version": "2022-11-28"})

    def _get_paginated_data(self, url: str, params=None) -> list:
        """
        Get paginated data from an endpoint. Top-level of returned data must be a list
        :param url: the endpoint of the query
        :type url: str
        :param params: query-specific params to be added
        :type params: dict
        :return: the data returned from multiple queries, concatenated
        :rtype: list
        """
        if params is None:
            params = {}
        concat_data: list = []

        curr_page: int = 1
        pages_remain: bool = True
        while pages_remain:
            query_params = {"per_page": 100, "page": curr_page}
            query_params.update(params)
            response: Response = self.session.get(url, params=query_params)
            link_header = response.headers.get('link')
            pages_remain = (link_header is not None) and ('rel=\"next\"' in link_header)
            curr_page += 1

            if response.status_code != 200:
                continue

            data = response.json()

            if type(data) is not list:
                raise TypeError(f"Response data must be a list, instead got {type(data)}")
            concat_data.extend(data)

        return concat_data

    @cache
    def get_repo_list(self) -> list[Repository]:
        """
        :return: a list of the names of all public repositories owned by the organisation
        :rtype: list
        """
        query_path: str = '/'.join([self.ROOT_PATH, "orgs", self.org_name, "repos"])
        query_data = self._get_paginated_data(query_path, {"type": "public"})
        repo_list: list[Repository] = []
        for repo_info in query_data:
            repo = Repository(repo_info["name"], repo_info["description"], repo_info["html_url"])
            repo_list.append(repo)

        return repo_list

    @cache
    def get_user_contributions(self, repo_name: str) -> list[UserRepository]:
        query_path: str = '/'.join([self.ROOT_PATH, "repos", self.org_name, repo_name, "contributors"])
        query_data = self._get_paginated_data(query_path)
        contributor_list: list[UserRepository] = []
        for contrib_info in query_data:
            contrib = UserRepository(repo_name, contrib_info["login"], contrib_info["html_url"],
                                     contrib_info["avatar_url"], contrib_info["contributions"])
            contributor_list.append(contrib)

        return contributor_list
