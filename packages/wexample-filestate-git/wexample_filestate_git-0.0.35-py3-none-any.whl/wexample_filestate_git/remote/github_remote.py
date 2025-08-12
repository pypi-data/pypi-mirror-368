import os
import re
from typing import Dict, List
from pydantic import Field

from wexample_helpers_api.enums.http import HttpMethod
from .abstract_remote import AbstractRemote

GITHUB_API_TOKEN: str = "GITHUB_API_TOKEN"
GITHUB_DEFAULT_URL: str = "GITHUB_DEFAULT_URL"


class GithubRemote(AbstractRemote):
    base_url: str = Field(
        default="https://api.github.com",
        description="GitHub API base URL"
    )

    def model_post_init(self, *args, **kwargs):
        super().model_post_init(*args, **kwargs)

        self.default_headers.update({
            "Authorization": f"token {os.getenv(GITHUB_API_TOKEN)}",
            "Accept": "application/vnd.github.v3+json"
        })

        if os.getenv(GITHUB_DEFAULT_URL) is not None:
            self.base_url = os.getenv(GITHUB_DEFAULT_URL)

    def get_expected_env_keys(self) -> List[str]:
        return [
            GITHUB_API_TOKEN,
        ]

    def create_repository(self, name: str, namespace: str, description: str = "", private: bool = False) -> Dict:
        """
        Create a new repository in the specified namespace.
        
        Args:
            name: Repository name
            namespace: Organization or user name (mandatory)
            description: Optional repository description
            private: Whether the repository should be private
        """
        endpoint = f"orgs/{namespace}/repos"

        response = self.make_request(
            method=HttpMethod.POST,
            endpoint=endpoint,
            data={
                "name": name,
                "description": description,
                "private": private,
                "auto_init": True
            },
            call_origin=__file__,
            expected_status_codes=[201],  # Only 201 Created is acceptable
            fatal_if_unexpected=True  # Any other status code should raise an error
        )
        return response.json()

    def check_repository_exists(self, name: str, namespace: str) -> bool:
        """
        Check if a repository exists in the specified namespace.
        
        Args:
            name: Repository name
            namespace: Organization or user name (mandatory)
        """
        try:
            endpoint = f"repos/{namespace}/{name}"
            response = self.make_request(
                endpoint=endpoint,
                call_origin=__file__,
                expected_status_codes=[200, 404]
            )
            return response.status_code == 200
        except Exception:
            return False

    def create_repository_if_not_exists(self, remote_url: str, description: str = "", private: bool = False) -> Dict:
        """
        Create a repository from a complete remote URL if it doesn't exist.
        
        Args:
            remote_url: Complete GitHub repository URL
            description: Optional repository description
            private: Whether the repository should be private
        """
        repo_info = self.parse_repository_url(remote_url)
        
        if not self.check_repository_exists(repo_info['name'], repo_info['namespace']):
            return self.create_repository(
                name=repo_info['name'],
                namespace=repo_info['namespace'],
                description=description,
                private=private
            )
        return {}

    def parse_repository_url(self, remote_url: str) -> Dict[str, str]:
        """
        Parse a GitHub repository URL to extract repository information.
        Supports both HTTPS and SSH URLs:
        - https://github.com/owner/repo.git
        - git@github.com:owner/repo.git
        """
        # Remove protocol and domain
        path = re.sub(r'^(https://github\.com/|git@github\.com:)', '', remote_url)
        # Remove .git suffix if present
        path = path.replace('.git', '')
        
        parts = path.split('/')
        if len(parts) >= 2:
            return {
                'name': parts[-1],
                'namespace': parts[-2]
            }
        return {
            'name': parts[0],
            'namespace': ''
        }

    @classmethod
    def detect_remote_type(cls, remote_url: str) -> bool:
        return bool(re.search(r'github\.com[:/]', remote_url))
