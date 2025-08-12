import os
import re
from typing import Dict, List, Optional
from pydantic import Field
import requests

from wexample_helpers_api.enums.http import HttpMethod
from .abstract_remote import AbstractRemote


GITLAB_API_TOKEN: str = "GITLAB_API_TOKEN"
GITLAB_DEFAULT_URL: str = "GITLAB_DEFAULT_URL"


class GitlabRemote(AbstractRemote):
    base_url: str = Field(
        default="https://gitlab.com/api/v4",
        description="GitLab API base URL"
    )

    def model_post_init(self, *args, **kwargs):
        super().model_post_init(*args, **kwargs)

        self.default_headers.update({
            "PRIVATE-TOKEN": os.getenv(GITLAB_API_TOKEN)
        })

        if os.getenv(GITLAB_DEFAULT_URL) is not None:
            self.base_url = os.getenv(GITLAB_DEFAULT_URL)

    def get_expected_env_keys(self) -> List[str]:
        return [
            GITLAB_API_TOKEN,
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
        data = {
            "name": name,
            "path": name,
            "description": description,
            "visibility": "private" if private else "public",
            "initialize_with_readme": False,
            "namespace_id": self._get_namespace_id(namespace)
        }

        response = self.make_request(
            method=HttpMethod.POST,
            endpoint="projects",
            data=data,
            call_origin=__file__
        )
        return response.json()

    def check_connection(self) -> bool:
        try:
            url = f"{self.base_url.rstrip('/')}/user"

            response = requests.head(
                url,
                headers=self.default_headers,
                timeout=self.timeout
            )

            return response.status_code == 200

        except requests.exceptions.RequestException as e:
            return False

    def check_repository_exists(self, name: str, namespace: str) -> bool:
        """
        Check if a repository exists in the specified namespace.
        
        Args:
            name: Repository name
            namespace: Organization or user name (mandatory)
        """
        try:
            endpoint = f"projects/{namespace}%2F{name}"
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
            remote_url: Complete GitLab repository URL
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

    def _get_namespace_id(self, namespace_path: str) -> Optional[int]:
        try:
            response = requests.get(
                f"{self.base_url.rstrip('/')}/namespaces",
                params={"search": namespace_path},
                headers=self.default_headers,
                timeout=self.timeout
            )
            if response.status_code == 200:
                namespaces = response.json()
                for ns in namespaces:
                    if ns["path"] == namespace_path:
                        return ns["id"]
            return None
        except requests.exceptions.RequestException:
            return None

    @classmethod
    def detect_remote_type(cls, remote_url: str) -> bool:
        # Support both gitlab.com and custom GitLab instances
        return bool(re.search(r'gitlab\.[a-zA-Z0-9.-]+[:/]', remote_url))

    def parse_repository_url(self, remote_url: str) -> Dict[str, str]:
        """
        Parse a GitLab repository URL to extract repository information.
        Supports both HTTPS and SSH URLs and custom GitLab instances:
        - https://gitlab.example.com/owner/repo.git
        - git@gitlab.example.com:owner/repo.git
        """
        # Extract the path part after the domain
        if remote_url.startswith('git@'):
            path = remote_url.split(':', 1)[1]
        else:
            # For HTTPS URLs, split on the third slash to get the path
            parts = remote_url.split('/', 3)
            path = parts[3] if len(parts) > 3 else ''

        # Remove .git suffix if present
        path = path.replace('.git', '')
        
        # Split the path into parts and extract name and namespace
        url_parts = path.split('/')
        if len(url_parts) >= 2:
            repo_name = url_parts[-1]
            namespace = url_parts[-2]
            return {
                'name': repo_name,
                'namespace': namespace
            }
        
        return {
            'name': url_parts[0],
            'namespace': ''
        }