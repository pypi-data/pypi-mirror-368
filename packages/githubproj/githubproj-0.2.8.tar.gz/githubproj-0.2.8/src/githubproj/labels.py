"""
A module for managing GitHub labels.
"""

from typing import Any, Dict, List, Optional

import yaml

from .client import GithubClient
from .schema import Label


class Labels:
    """
    A class for performing operations on GitHub labels.
    """

    def __init__(
        self, client: GithubClient, config_path: str = 'projects/config.yml'
    ):
        """
        Initializes the Labels class.

        Args:
            client: An instance of the GithubClient.
            config_path: The path to the configuration file.
        """
        self.client = client
        self.config = self._load_config(config_path)
        self.repo_id = self.config['repository']['id']
        self.project_owner = self.config['projects'][0]['owner']
        self.repo_name = self.config['repository']['name']
        self.standard_labels = self.config.get('standard_labels', [])

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Loads the configuration from a YAML file.

        Args:
            config_path: The path to the configuration file.

        Returns:
            A dictionary containing the configuration.
        """
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def list(self) -> List[Label]:
        """
        Retrieves all labels for the repository.

        Returns:
            A list of Label objects.
        """
        query = f"""
        query {{
          repository(
            owner: "{self.project_owner}", name: "{self.repo_name}"
          ) {{
            labels(first: 100) {{
              nodes {{
                id
                name
                color
                description
              }}
            }}
          }}
        }}
        """
        data = self.client.execute_query(query)
        labels_data = data['data']['repository']['labels']['nodes']
        return [Label(**label) for label in labels_data]

    def get(self, name: str) -> Optional[Label]:
        """
        Retrieves a label by its name.

        Args:
            name: The name of the label to retrieve.

        Returns:
            A Label object if found, otherwise None.
        """
        labels = self.list()
        for label in labels:
            if label.name == name:
                return label
        return None

    def create(self, name: str, color: str, description: str = '') -> Label:
        """
        Creates a new label.

        Args:
            name: The name of the label.
            color: The hex color of the label, without the leading '#'.
            description: A description for the label.

        Returns:
            The created Label object.
        """
        query = f"""
        mutation {{
          createLabel(input: {{
            repositoryId: "{self.repo_id}",
            name: "{name}",
            color: "{color}",
            description: "{description}"
          }}) {{
            label {{
              id
              name
              color
              description
            }}
          }}
        }}
        """
        data = self.client.execute_query(query)
        return Label(**data['data']['createLabel']['label'])

    def update(
        self, label_id: str, name: str, color: str, description: str
    ) -> Label:
        """
        Updates an existing label.

        Args:
            label_id: The ID of the label to update.
            name: The new name for the label.
            color: The new hex color for the label.
            description: The new description for the label.

        Returns:
            The updated Label object.
        """
        query = f"""
        mutation {{
          updateLabel(input: {{
            id: "{label_id}",
            name: "{name}",
            color: "{color}",
            description: "{description}"
          }}) {{
            label {{
              id
              name
              color
              description
            }}
          }}
        }}
        """
        data = self.client.execute_query(query)
        return Label(**data['data']['updateLabel']['label'])

    def sync(self) -> List[Label]:
        """
        Synchronizes the labels in the GitHub repository with the
        standard_labels list in the config.

        - If a label exists, it's updated to match the standard color and
          description.
        - If a label does not exist, it's created.

        Returns:
            A list of the synced Label objects.
        """
        synced_labels = []
        self.list()

        for label_def in self.standard_labels:
            name = label_def['name']
            color = label_def['color']
            description = label_def['description']

            existing_label = self.get(name)

            if existing_label:
                # Update Existing Label
                updated_label = self.update(
                    label_id=existing_label.id,
                    name=name,
                    color=color,
                    description=description,
                )
                synced_labels.append(updated_label)
            else:
                # Create New Label
                new_label = self.create(
                    name=name, color=color, description=description
                )
                synced_labels.append(new_label)

        return synced_labels
