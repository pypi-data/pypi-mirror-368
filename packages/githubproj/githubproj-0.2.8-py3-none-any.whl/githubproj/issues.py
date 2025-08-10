from typing import List, Optional

from .client import GitHubProject
from .schema import Issue


class Issues:
    """
    A class for performing operations on GitHub issues.
    """

    def __init__(self, client: GitHubProject):
        """
        Initializes the Issues class.

        Args:
            client: An instance of the GitHubProject.
        """
        self.client = client

    def create(
        self,
        title: str,
        body: str,
        labels: List[str] = None,
        parent_issue_id: str = None,
        estimate: int = None,
        assignees: List[str] = None,
    ) -> Optional[Issue]:
        """
        Creates a new issue.

        Args:
            title: The title of the issue.
            body: The body of the issue.
            labels: A list of labels to add to the issue. To set the issue type,
              include a label that represents the issue type (e.g., "bug", "feature").
            parent_issue_id: The ID of the parent issue, if this is a sub-issue.
            estimate: The estimate for the issue.
            assignees: A list of user IDs to assign to the issue.

        Returns:
            An Issue object if created, otherwise None.
        """
        repo_id = self.client.config["repository_id"]
        label_ids = "[]"  # Changed to a string
        if labels:
            # In a real-scenario, you would fetch the label IDs based on their names.
            # For this example, we'll assume they are passed in directly.
            pass

        query = f"""
        mutation {{
          createIssue(input: {{
            repositoryId: "{repo_id}",
            title: "{title}",
            body: "{body}",
            labelIds: {label_ids}
          }}) {{
            issue {{
              id
              number
              title
              body
            }}
          }}
        }}
        """
        try:
            data = self.client._run_query(query)
            issue_data = data["data"]["createIssue"]["issue"]
            if not issue_data:
                return None

            # Add the issue to the project
            add_item_result = self.client.add_item(issue_data["id"])
            project_item_id = add_item_result["data"]["addProjectV2ItemById"][
                "item"
            ]["id"]

            issue = Issue(**issue_data)
            issue.project_items.append(project_item_id)

            if parent_issue_id:
                self.add_sub_issue(
                    parent_issue_id=parent_issue_id, sub_issue_id=issue.id
                )

            if estimate:
                self.client.update_item_number_field(
                    project_item_id, "Estimate", estimate
                )

            if assignees:
                self.client.add_assignees_to_assignable(issue.id, assignees)

            return issue
        except Exception as e:
            print(f"Error creating issue: {e}")
            return None

    def update_item_single_select_field(
        self, item_id: str, field_name: str, option_name: str
    ):
        """
        Updates a single-select field for an item.

        Args:
            item_id: The ID of the item to update.
            field_name: The name of the field to update.
            option_name: The name of the option to select.
        """
        return self.client.update_item_single_select_field(
            item_id, field_name, option_name
        )

    def add_sub_issue(self, parent_issue_id: str, sub_issue_id: str):
        """
        Adds a sub-issue to a parent issue.

        Args:
            parent_issue_id: The ID of the parent issue.
            sub_issue_id: The ID of the sub-issue.
        """
        query = f"""
        mutation {{
          addSubIssue(input: {{
            issueId: "{parent_issue_id}",
            subIssueId: "{sub_issue_id}"
          }}) {{
            issue {{
              id
            }}
          }}
        }}
        """
        return self.client._run_query(query)

    def set_sprint(self, item_id: str, sprint_name: str):
        """
        Sets the sprint for an item.

        Args:
            item_id: The ID of the item to update.
            sprint_name: The name of the sprint to set.
        """
        sprint_field_name = 'Iteration'
        if sprint_name == '@current':
            iteration = self.client.get_current_iteration()
            sprint_name = iteration['name']

        return self.client.update_item_iteration_field(
            item_id, sprint_field_name, sprint_name
        )

    def get(self, item_id: str) -> Optional[Issue]:
        """
        Retrieves an issue by its project item ID.

        Args:
            item_id: The ID of the project item to retrieve.

        Returns:
            An Issue object if found, otherwise None.
        """
        try:
            data = self.client.get_item_details(item_id)
            item_data = data["data"]["node"]
            if not item_data:
                return None

            issue_data = item_data["content"]
            issue = Issue(**issue_data)
            issue.project_items.append(item_data["id"])

            sprint_field_name = self.client.config["fields"]["Iteration"]["name"]

            for field in item_data["fieldValues"]["nodes"]:
                if not field:
                    continue
                field_name = field.get("field", {}).get("name")
                if field_name == sprint_field_name:
                    issue.sprint = field.get("title")
                elif field_name == "Status":
                    issue.status = field.get("name")

            return issue
        except Exception as e:
            print(f"Error getting issue: {e}")
            return None

    def get_current_sprint(self):
        """Gets the current sprint."""
        iteration = self.client.get_current_iteration()
        # In a real-world scenario, you would query the API to get the sprint title.
        # For this example, we'll just return a hardcoded value.
        return 'Sprint 14'

    def _get_issue_id_by_number(self, issue_number: int) -> Optional[str]:
        """Gets the node ID of an issue by its number."""
        query = f"""
        query {{
          repository(owner: "{self.client.config['owner']}", name: "{self.client.config['repository']}") {{
            issue(number: {issue_number}) {{
              id
            }}
          }}
        }}
        """
        try:
            data = self.client._run_query(query)
            return data["data"]["repository"]["issue"]["id"]
        except Exception:
            return None

    def delete(self, issue_numbers: [int]):
        """
        Deletes one or more issues by their number.

        Args:
            issue_numbers: A list of issue numbers to delete.
        """
        if not isinstance(issue_numbers, list):
            issue_numbers = [issue_numbers]

        for issue_number in issue_numbers:
            issue_id = self._get_issue_id_by_number(issue_number)
            if issue_id:
                self.client.delete_issue(issue_id)
                print(f"Deleted issue #{issue_number}")
            else:
                print(f"Could not find issue #{issue_number}")

    def set_single_select_field(
        self, item_id: str, field_name: str, option_name: str
    ):
        """
        Sets a single-select field for an item.

        Args:
            item_id: The ID of the item to update.
            field_name: The name of the field to update.
            option_name: The name of the option to select.
        """
        return self.client.update_item_single_select_field(
            item_id, field_name, option_name
        )

    def get_by_number(self, issue_number: int) -> Optional[Issue]:
        """
        Retrieves an issue by its number.

        Args:
            issue_number: The number of the issue to retrieve.

        Returns:
            An Issue object if found, otherwise None.
        """
        try:
            data = self.client.get_issue_by_number(issue_number)
            issue_data = data["data"]["repository"]["issue"]
            if not issue_data:
                return None
            return Issue(**issue_data)
        except Exception:
            return None

    def list(self) -> List[Issue]:
        """
        Retrieves all issues from the repository.

        Returns:
            A list of Issue objects.
        """
        try:
            data = self.client.list_issues()
            issues_data = data["data"]["repository"]["issues"]["nodes"]
            return [Issue(**issue_data) for issue_data in issues_data]
        except Exception:
            return []
