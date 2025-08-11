from typing import Optional

from .client import GitHubProject


class Project:
    """
    A class for performing operations on GitHub projects.
    """

    def __init__(self, client: GitHubProject):
        """
        Initializes the Project class.

        Args:
            client: An instance of the GitHubProject.
        """
        self.client = client

    def update(
        self,
        title: Optional[str] = None,
        short_description: Optional[str] = None,
        readme: Optional[str] = None,
        public: Optional[bool] = None,
        closed: Optional[bool] = None,
    ):
        """
        Updates the project.

        Args:
            title: The new title of the project.
            short_description: The new short description of the project.
            readme: The new readme of the project.
            public: Whether the project should be public.
            closed: Whether the project should be closed.
        """
        return self.client.update_project(
            title=title,
            short_description=short_description,
            readme=readme,
            public=public,
            closed=closed,
        )
