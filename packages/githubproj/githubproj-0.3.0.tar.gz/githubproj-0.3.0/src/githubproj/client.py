from typing import Optional
import json
import subprocess
import sys

if sys.version_info < (3, 11):
    import toml
else:
    import tomllib as toml


import datetime


class GitHubProject:
    def __init__(self, config_path='config.toml'):
        """
        Initializes the client by loading configuration from a TOML file.
        """
        try:
            with open(config_path, 'rb') as f:
                self.config = toml.load(f)
        except FileNotFoundError:
            raise Exception(f'Configuration file not found at: {config_path}')
        except toml.TOMLDecodeError as e:
            raise Exception(f'Error decoding TOML file: {e}')

        self.project_id = self.config.get('project_id')
        if not self.project_id:
            raise ValueError('`project_id` not found in configuration file.')

    def _run_query(self, query):
        """
        Runs a GraphQL query using the gh CLI.
        """
        # Clean up the query by removing newlines and escaping quotes
        clean_query = ' '.join(query.strip().split())
        command = ['gh', 'api', 'graphql', '-f', f'query={clean_query}']
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, check=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            raise Exception(f'Error running gh command: {e.stderr}')
        except json.JSONDecodeError as e:
            raise Exception(f'Error decoding JSON response: {e}')

    def get_field_id(self, field_name):
        """Gets the ID of a field by its name from the config."""
        try:
            return self.config['fields'][field_name]['id']
        except KeyError:
            raise ValueError(
                f"Field '{field_name}' not found in configuration."
            )

    def get_option_id(self, field_name, option_name):
        """Gets the ID of a single-select option by its name."""
        try:
            return self.config['fields'][field_name]['options'][option_name]
        except KeyError:
            # If the option is not in the config, it might be a dynamic value like an issue number.
            # In a real-world scenario, you would query the API to find the option ID for the given name.
            # For this example, we'll assume the name is the ID.
            return option_name

    def get_details(self):
        """
        Gets the details of the project.
        """
        query = f"""
        query {{
            node(id: "{self.project_id}") {{
                ... on ProjectV2 {{
                    title
                    shortDescription
                    readme
                    public
                    closed
                    url
                    number
                }}
            }}
        }}
        """
        return self._run_query(query)

    def get_items(self, first=100):
        """
        Gets the items of the project.
        """
        query = f"""
        query {{
            node(id: "{self.project_id}") {{
                ... on ProjectV2 {{
                    items(first: {first}) {{
                        nodes {{
                            id
                            content {{
                                ... on DraftIssue {{
                                    title
                                    body
                                }}
                                ... on Issue {{
                                    title
                                    body
                                    number
                                    url
                                }}
                                ... on PullRequest {{
                                    title
                                    body
                                    number
                                    url
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        return self._run_query(query)

    def add_item(self, content_id):
        """
        Adds an item (issue or pull request) to the project.
        """
        query = f"""
        mutation {{
            addProjectV2ItemById(
                input: {{
                    projectId: "{self.project_id}"
                    contentId: "{content_id}"
                }}
            ) {{
                item {{
                    id
                }}
            }}
        }}
        """
        return self._run_query(query)

    def update_item_field_value(self, item_id, field_name, value):
        """
        Updates a field value for an item in the project using the field name.
        """
        field_id = self.get_field_id(field_name)

        # This part needs to be smarter to handle different value types
        # For now, assuming a simple text value update
        value_str = f'text: "{value}"'  # Simplified for this example

        query = f"""
        mutation {{
            updateProjectV2ItemFieldValue(
                input: {{
                    projectId: "{self.project_id}"
                    itemId: "{item_id}"
                    fieldId: "{field_id}"
                    value: {{
                        {value_str}
                    }}
                }}
            ) {{
                projectV2Item {{
                    id
                }}
            }}
        }}
        """
        return self._run_query(query)

    def update_item_single_select_field(
        self, item_id, field_name, option_name
    ):
        """
        Updates a single-select field for an item using the field and option
        names.
        """
        field_id = self.get_field_id(field_name)
        option_id = self.get_option_id(field_name, option_name)

        query = f"""
        mutation {{
            updateProjectV2ItemFieldValue(
                input: {{
                    projectId: "{self.project_id}"
                    itemId: "{item_id}"
                    fieldId: "{field_id}"
                    value: {{
                        singleSelectOptionId: "{option_id}"
                    }}
                }}
            ) {{
                projectV2Item {{
                    id
                }}
            }}
        }}
        """
        return self._run_query(query)

    def get_current_iteration(self):
        """Gets the current iteration."""
        today = datetime.date.today()
        iterations = self.config['fields']['Iteration']['iterations']
        current_iteration = None
        latest_start_date = None

        for start_date_str, iteration_id in iterations.items():
            start_date = datetime.datetime.strptime(
                start_date_str, '%Y-%m-%d'
            ).date()
            if start_date <= today:
                if latest_start_date is None or start_date > latest_start_date:
                    latest_start_date = start_date
                    current_iteration = {
                        'name': start_date_str,
                        'id': iteration_id,
                    }

        if current_iteration:
            return current_iteration
        else:
            raise ValueError('No current iteration found.')

    def get_iteration_id(self, iteration_name):
        """Gets the ID of an iteration by its name from the config."""
        if iteration_name == '@current':
            return self.get_current_iteration()['id']

        try:
            return self.config['fields']['Iteration']['iterations'][
                iteration_name
            ]
        except KeyError:
            raise ValueError(
                f"Iteration '{iteration_name}' not found in configuration."
            )

    def update_item_iteration_field(self, item_id, field_name, iteration_name):
        """
        Updates an iteration field for an item using the field and iteration names.
        """
        field_id = self.get_field_id(field_name)
        iteration_id = self.get_iteration_id(iteration_name)

        query = f"""
        mutation {{
            updateProjectV2ItemFieldValue(
                input: {{
                    projectId: "{self.project_id}"
                    itemId: "{item_id}"
                    fieldId: "{field_id}"
                    value: {{
                        iterationId: "{iteration_id}"
                    }}
                }}
            ) {{
                projectV2Item {{
                    id
                }}
            }}
        }}
        """
        return self._run_query(query)

    def update_item_number_field(self, item_id, field_name, number):
        """
        Updates a number field for an item using the field name and number.
        """
        field_id = self.get_field_id(field_name)

        query = f"""
        mutation {{
            updateProjectV2ItemFieldValue(
                input: {{
                    projectId: "{self.project_id}"
                    itemId: "{item_id}"
                    fieldId: "{field_id}"
                    value: {{
                        number: {number}
                    }}
                }}
            ) {{
                projectV2Item {{
                    id
                }}
            }}
        }}
        """
        return self._run_query(query)

    def add_assignees_to_assignable(self, assignable_id, assignee_ids):
        """Adds assignees to an assignable object."""
        assignee_ids_str = json.dumps(assignee_ids)
        query = f"""
        mutation {{
          addAssigneesToAssignable(input: {{
            assignableId: "{assignable_id}",
            assigneeIds: {assignee_ids_str}
          }}) {{
            assignable {{
              ... on Issue {{
                number
              }}
            }}
          }}
        }}
        """
        return self._run_query(query)

    def get_item_details(self, item_id: str):
        """Gets the details of a project item."""
        query = f"""
        query {{
          node(id: "{item_id}") {{
            ... on ProjectV2Item {{
              id
              isArchived
              content {{
                ... on Issue {{
                  title
                  number
                  body
                  id
                }}
              }}
              fieldValues(first: 20) {{
                nodes {{
                  ... on ProjectV2ItemFieldTextValue {{
                    text
                    field {{
                      ... on ProjectV2Field {{
                        name
                      }}
                    }}
                  }}
                  ... on ProjectV2ItemFieldSingleSelectValue {{
                    name
                    field {{
                      ... on ProjectV2SingleSelectField {{
                        name
                      }}
                    }}
                  }}
                  ... on ProjectV2ItemFieldIterationValue {{
                    title
                    startDate
                    field {{
                      ... on ProjectV2IterationField {{
                        name
                      }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
        """
        return self._run_query(query)

    def delete_item(self, item_id):
        """
        Deletes an item from the project.
        """
        query = f"""
        mutation {{
            deleteProjectV2Item(
                input: {{
                    projectId: "{self.project_id}"
                    itemId: "{item_id}"
                }}
            ) {{
                deletedItemId
            }}
        }}
        """
        return self._run_query(query)

    def delete_issue(self, issue_id):
        """Deletes an issue."""
        query = f"""
        mutation {{
          deleteIssue(input: {{
            issueId: "{issue_id}"
          }}) {{
            repository {{
              id
            }}
          }}
        }}
        """
        return self._run_query(query)

    def get_issue_by_number(self, issue_number: int):
        """Gets an issue by its number."""
        query = f"""
        query {{
          repository(owner: "{self.config['owner']}", name: "{self.config['repository']}") {{
            issue(number: {issue_number}) {{
              id
              number
              title
              body
            }}
          }}
        }}
        """
        return self._run_query(query)

    def list_issues(self):
        """Lists all issues in the repository."""
        query = f"""
        query {{
          repository(owner: "{self.config['owner']}", name: "{self.config['repository']}") {{
            issues(first: 100) {{
              nodes {{
                id
                number
                title
                body
              }}
            }}
          }}
        }}
        """
        return self._run_query(query)

    def archive_project_item(self, item_id):
        """Archives a project item."""
        query = f"""
        mutation {{
          archiveProjectV2Item(input: {{
            projectId: "{self.project_id}",
            itemId: "{item_id}"
          }}) {{
            item {{
              id
            }}
          }}
        }}
        """
        return self._run_query(query)

    def unarchive_project_item(self, item_id):
        """Unarchives a project item."""
        query = f"""
        mutation {{
          unarchiveProjectV2Item(input: {{
            projectId: "{self.project_id}",
            itemId: "{item_id}"
          }}) {{
            item {{
              id
            }}
          }}
        }}
        """
        return self._run_query(query)

    def update_project(
        self,
        title: Optional[str] = None,
        short_description: Optional[str] = None,
        readme: Optional[str] = None,
        public: Optional[bool] = None,
        closed: Optional[bool] = None,
    ):
        """Updates the project."""
        mutations = []
        if title:
            mutations.append(f'title: "{title}"')
        if short_description:
            mutations.append(f'shortDescription: "{short_description}"')
        if readme:
            mutations.append(f'readme: "{readme}"')
        if public is not None:
            mutations.append(f"public: {str(public).lower()}")
        if closed is not None:
            mutations.append(f"closed: {str(closed).lower()}")

        if not mutations:
            return

        query = f"""
        mutation {{
          updateProjectV2(input: {{
            projectId: "{self.project_id}",
            {', '.join(mutations)}
          }}) {{
            projectV2 {{
              id
            }}
          }}
        }}
        """
        return self._run_query(query)

    def clear_item_field_value(self, item_id, field_name):
        """Clears a field for an item."""
        field_id = self.get_field_id(field_name)
        query = f"""
        mutation {{
          clearProjectV2ItemFieldValue(input: {{
            projectId: "{self.project_id}",
            itemId: "{item_id}",
            fieldId: "{field_id}"
          }}) {{
            projectV2Item {{
              id
            }}
          }}
        }}
        """
        return self._run_query(query)

    def get_fields(self, first=20):
        """
        Gets the fields of the project.
        """
        query = f"""
        query{{
            node(id: "{self.project_id}") {{
                ... on ProjectV2 {{
                    fields(first: {first}) {{
                        nodes {{
                            ... on ProjectV2Field {{
                                id
                                name
                            }}
                            ... on ProjectV2IterationField {{
                                id
                                name
                                configuration {{
                                    iterations {{
                                        startDate
                                        id
                                    }}
                                }}
                            }}
                            ... on ProjectV2SingleSelectField {{
                                id
                                name
                                options {{
                                    id
                                    name
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        return self._run_query(query)
