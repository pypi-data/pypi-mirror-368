import requests
import pandas as pd
import ast
from typing import Union


class PowerBIClient:
    # Power BI Client Class
    """
    PowerBIClient handles authentication and API calls to the Power BI REST API.

    Attributes:
        tenant_id (str): Azure AD tenant ID.
        client_id (str): App's client ID registered in Azure.
        client_secret (str): App's client secret.
        access_token (str): Access token retrieved using client credentials.
    """

    # Init and get token
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        """
        Initialize the client and retrieve an access token.

        Args:
            tenant_id (str): Azure AD tenant ID.
            client_id (str): Client/application ID.
            client_secret (str): Client/application secret.
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.powerbi.com/v1.0/myorg/groups/"
        self.access_token = None

    def get_token(self) -> str:
        """
        Retrieve an OAuth2 access token for the Power BI REST API.

        Returns:
            str: The access token string.
        """
        # Grab token
        header = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "login.microsoftonline.com:443",
        }

        data = {
            "grant_type": "client_credentials",
            "scope": "https://analysis.windows.net/powerbi/api/.default",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        result = requests.post(
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token",
            headers=header,
            data=data,
        )

        token_data = result.json()

        self.access_token = token_data["access_token"]

        return self.access_token

    def get_header(self) -> dict:
        """
        Get the headers required for authenticated API calls.

        Returns:
            dict: Headers with content type and bearer token.
        """

        token = self.get_token()

        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

    # Helper functions
    def extract_connection_details(self, x: Union[str, dict]) -> pd.Series:
        """
        Extract connection details from a stringified dictionary or a dictionary.

        Args:
            x (Union[str, dict]): The input value to extract connection details from.

        Returns:
            pd.Series: A series with connection details such as server, database, etc.
        """
        try:
            if isinstance(x, str):
                details = ast.literal_eval(x)
            elif isinstance(x, dict):
                details = x
            else:
                return pd.Series(
                    [None] * 5,
                    index=["server", "database", "connectionString", "url", "path"],
                )

            return pd.Series(
                {
                    "server": details.get("server"),
                    "database": details.get("database"),
                    "connectionString": details.get("connectionString"),
                    "url": details.get("url"),
                    "path": details.get("path"),
                }
            )
        except Exception as e:
            print(f"Error parsing connectionDetails: {e}")
            return pd.Series(
                [None] * 5,
                index=["server", "database", "connectionString", "url", "path"],
            )

    # Trigger actions
    def execute_query(
        self, workspace_id: str, dataset_id: str, query: str
    ) -> requests.Response:
        """
        Execute a DAX query against a Power BI dataset.

        Args:
            workspace_id (str): The Power BI workspace ID.
            dataset_id (str): The dataset ID.
            query (str): The DAX query to execute.

        Returns:
            requests.Response: The HTTP response containing the query results.
        """
        url = f"{self.base_url}/{workspace_id}/datasets/{dataset_id}/executeQueries"
        body = {
            "queries": [{"query": query}],
            "serializerSettings": {"includeNulls": True},
        }
        result = requests.post(url, headers=self.get_header(), json=body)
        return result

    def refresh_dataflow(self, workspace_id: str, dataflow_id: str) -> None:
        """
        Trigger a refresh for a specific dataflow.

        Args:
            workspace_id (str): The Power BI workspace ID.
            dataflow_id (str): The dataflow ID.
        """
        url = f"{self.base_url}/{workspace_id}/dataflows/{dataflow_id}/refreshes"
        result = requests.post(url, headers=self.get_header())
        if result.status_code == 200:
            print(f"Start refreshing dataflow {dataflow_id}")
        else:
            print(
                f"Failed to refresh dataflow {dataflow_id}. Status code: {result.status_code}"
            )

    def refresh_dataset(self, workspace_id: str, dataset_id: str) -> None:
        """
        Trigger a refresh for a specific dataset.

        Args:
            workspace_id (str): The Power BI workspace ID.
            dataset_id (str): The dataset ID.
        """
        url = f"{self.base_url}/{workspace_id}/datasets/{dataset_id}/refreshes"
        result = requests.post(url, headers=self.get_header())
        if result.status_code == 202:
            print(f"Start refreshing dataset {dataset_id}")
        else:
            print(
                f"Failed to refresh dataset {dataset_id}. Status code: {result.status_code}"
            )

    # Get data functions
    def get_report_by_workspace(self, workspace_id: str) -> requests.Response:
        """
        Retrieve all reports from a specified Power BI workspace.

        Args:
            workspace_id (str): The ID of the Power BI workspace.

        Returns:
            requests.Response: The HTTP response containing report metadata.
        """
        get_report_url = f"{self.base_url}/{workspace_id}/reports"
        result = requests.get(url=get_report_url, headers=self.get_header())
        return result

    def get_dataset_by_workspace(self, workspace_id: str) -> requests.Response:
        """
        Retrieve all datasets from a specified Power BI workspace.

        Args:
            workspace_id (str): The ID of the Power BI workspace.

        Returns:
            requests.Response: The HTTP response containing dataset metadata.
        """
        get_dataset_url = f"{self.base_url}/{workspace_id}/datasets"
        result = requests.get(url=get_dataset_url, headers=self.get_header())
        return result

    def get_dataflow_by_workspace(self, workspace_id: str) -> requests.Response:
        """
        Retrieve all dataflows from a specified Power BI workspace.

        Args:
            workspace_id (str): The ID of the Power BI workspace.

        Returns:
            requests.Response: The HTTP response containing dataflow metadata.
        """
        get_dataflow_url = f"{self.base_url}/{workspace_id}/dataflows"
        result = requests.get(url=get_dataflow_url, headers=self.get_header())
        return result

    def get_dataset_refresh_history_by_id(self, workspace_id, dataset_id, top_n=10):
        """
        Get dataset refresh history by dataset id.
        Args:
            workspace_id (str): The ID of the Power BI workspace.
            dataset_id (str): The ID of the Power BI dataset.
            top_n (int): The number of most recent refreshes to retrieve. Default is 10.
        Returns:
            result (requests.Response): The response object containing the dataset refresh history.
        """
        # Define URL endpoint
        get_dataset_refresh_history_url = f"{self.base_url}/{workspace_id}/datasets/{dataset_id}/refreshes?$top={top_n}"
        # Send API to get data
        result = requests.get(
            url=get_dataset_refresh_history_url, headers=self.get_header()
        )
        return result

    def get_dataflow_refresh_history_by_id(self, workspace_id, dataflow_id):
        """
        Get dataflow refresh history by dataflow id.
        Args:
            workspace_id (str): The ID of the Power BI workspace.
            dataflow_id (str): The ID of the Power BI dataflow.
        Returns:
            result (requests.Response): The response object containing the dataflow refresh history.
        """
        get_dataflow_refresh_history_url = (
            f"{self.base_url}/{workspace_id}/dataflows/{dataflow_id}/transactions"
        )
        # Send API to get data
        result = requests.get(
            url=get_dataflow_refresh_history_url, headers=self.get_header()
        )

        return result

    def get_dataset_sources_by_id(self, workspace_id, dataset_id):
        """
        Get dataset sources by dataset id.

        Args:
            workspace_id (str): The ID of the Power BI workspace.
            dataset_id (str): The ID of the Power BI dataset.
        Returns:
            result (requests.Response): The response object containing the dataset sources.
        """
        # Define URL endpoint
        get_dataset_source_url = (
            f"{self.base_url}/{workspace_id}/datasets/{dataset_id}/datasources"
        )
        # Send API to get data
        result = requests.get(url=get_dataset_source_url, headers=self.get_header())
        return result

    def get_dataflow_sources_by_id(self, workspace_id, dataflow_id):
        """
        Get dataflow sources by dataflow id.

        Args:
            workspace_id (str): The ID of the Power BI workspace.
            dataflow_id (str): The ID of the Power BI dataflow.
        Returns:
            result (requests.Response): The response object containing the dataflow sources.
        """
        # Define URL endpoint
        get_dataflow_source_url = (
            f"{self.base_url}/{workspace_id}/dataflows/{dataflow_id}/datasources"
        )
        # Send API to get data
        result = requests.get(url=get_dataflow_source_url, headers=self.get_header())
        return result

    def get_report_sources_by_id(self, workspace_id, report_id):
        """
        Get report sources by report id.

        Args:
            workspace_id (str): The ID of the Power BI workspace.
            report_id (str): The ID of the Power BI report.
        Returns:
            result (requests.Response): The response object containing the report sources.
        """
        # Define URL endpoint
        get_report_source_url = (
            f"{self.base_url}/{workspace_id}/reports/{report_id}/datasources"
        )
        # Send API to get data
        result = requests.get(url=get_report_source_url, headers=self.get_header())
        return result

    def get_dataset_users_by_id(self, workspace_id, dataset_id):
        """
        Get dataset users by dataset id.

        Args:
            workspace_id (str): The ID of the Power BI workspace.
            dataset_id (str): The ID of the Power BI dataset.
        Returns:
            result (requests.Response): The response object containing the dataset users.
        """
        # Define URL endpoint
        get_dataset_users_url = (
            f"{self.base_url}/{workspace_id}/datasets/{dataset_id}/users"
        )
        # Send API to get data
        result = requests.get(url=get_dataset_users_url, headers=self.get_header())
        return result

    def get_dataset_tables_by_id(self, workspace_id, dataset_id):
        """
        Get dataset tables by dataset id.

        Args:
            workspace_id (str): The ID of the Power BI workspace.
            dataset_id (str): The ID of the Power BI dataset.
        Returns:
            result (requests.Response): The response object containing the dataset tables.
        """
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/executeQueries"

        # Query to execute
        query_body = {
            "queries": [{"query": "EVALUATE INFO.VIEW.TABLES()"}],
            "serializerSettings": {"includeNulls": True},
        }

        response = requests.post(url, headers=self.get_header(), json=query_body)

        return response

    def get_dataset_columns_by_id(self, workspace_id, dataset_id):
        """
        Get dataset columns by dataset id.

        Args:
            workspace_id (str): The ID of the Power BI workspace.
            dataset_id (str): The ID of the Power BI dataset.
        Returns:
            result (requests.Response): The response object containing the dataset columns.
        """
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/executeQueries"

        # Query to execute
        query_body = {
            "queries": [{"query": "EVALUATE INFO.VIEW.COLUMNS()"}],
            "serializerSettings": {"includeNulls": True},
        }

        response = requests.post(url, headers=self.get_header(), json=query_body)

        return response

    def get_dataset_measures_by_id(self, workspace_id, dataset_id):
        """
        Get dataset measures by dataset id.

        Args:
            workspace_id (str): The ID of the Power BI workspace.
            dataset_id (str): The ID of the Power BI dataset.
        Returns:
            result (requests.Response): The response object containing the dataset measures.
        """
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/executeQueries"

        # Query to execute
        query_body = {
            "queries": [{"query": "EVALUATE INFO.VIEW.MEASURES()"}],
            "serializerSettings": {"includeNulls": True},
        }

        response = requests.post(url, headers=self.get_header(), json=query_body)

        return response

    def get_dataset_calc_dependencies_by_id(self, workspace_id, dataset_id):
        """
        Get dataset calculation dependencies by dataset id.
        Args:
            workspace_id (str): The ID of the Power BI workspace.
            dataset_id (str): The ID of the Power BI dataset.
        Returns:
            result (requests.Response): The response object containing the dataset calculation dependencies.
        """
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/executeQueries"
        # Query to execute
        query_body = {
            "queries": [{"query": "EVALUATE INFO.CALCDEPENDENCY()"}],
            "serializerSettings": {"includeNulls": True},
        }

        response = requests.post(url, headers=self.get_header(), json=query_body)

        return response

    # Get data in bulk
    def get_all_workspaces(self) -> pd.DataFrame:
        """
        Retrieve all Power BI workspaces available to the authenticated user.

        Returns:
            pd.DataFrame: A DataFrame containing workspace metadata with columns such as 'id' and 'name'.
        """
        result = requests.get(url=self.base_url, headers=self.get_header())
        df_get_all_workspaces = pd.DataFrame.from_dict(
            result.json()["value"], orient="columns"
        )
        return df_get_all_workspaces

    def get_all_datasets(self) -> pd.DataFrame:
        """
        Retrieve all datasets from all available Power BI workspaces.

        This function loops through all workspaces accessible by the user and fetches dataset metadata
        from each, combining them into a single DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing dataset metadata, enriched with workspace context.
        """
        df_get_all_workspaces = self.get_all_workspaces()
        workspace_id_list = df_get_all_workspaces["id"]
        df_get_all_datasets = pd.DataFrame()

        for workspace_id in workspace_id_list:
            try:
                workspace_name = df_get_all_workspaces.query(f'id == "{workspace_id}"')[
                    "name"
                ].iloc[0]
                result = self.get_dataset_by_workspace(workspace_id)
                if result.status_code == 200:
                    df = pd.DataFrame.from_dict(
                        result.json()["value"], orient="columns"
                    )
                    df["workspaceId"] = workspace_id
                    df["workspaceName"] = workspace_name
                    df = df.astype("str")
                    df_get_all_datasets = pd.concat([df_get_all_datasets, df])
            except Exception as e:
                print(f"Error processing workspace {workspace_id}: {e}")
                continue

        return df_get_all_datasets

    def get_all_dataflows(self) -> pd.DataFrame:
        """
        Retrieve all dataflows from all accessible Power BI workspaces.

        This method loops through each workspace the user has access to and fetches all dataflows,
        enriching the results with the associated workspace ID and name.

        Returns:
            pd.DataFrame: A DataFrame containing dataflow metadata for each workspace,
            with additional columns for 'workspaceId' and 'workspaceName'.
        """
        df_get_all_workspaces = self.get_all_workspaces()
        workspace_id_list = df_get_all_workspaces["id"]
        df_get_all_dataflows = pd.DataFrame()

        for workspace_id in workspace_id_list:
            try:
                workspace_name = df_get_all_workspaces.query(f'id == "{workspace_id}"')[
                    "name"
                ].iloc[0]

                result = self.get_dataflow_by_workspace(workspace_id)
                if result.status_code == 200:
                    df = pd.DataFrame.from_dict(
                        result.json()["value"], orient="columns"
                    )
                    df["workspaceId"] = workspace_id
                    df["workspaceName"] = workspace_name
                    df = df.astype("str")
                    df_get_all_dataflows = pd.concat([df_get_all_dataflows, df])
            except Exception as e:
                print(f"Error processing workspace {workspace_id}: {e}")
                continue

        return df_get_all_dataflows

    def get_all_reports(self) -> pd.DataFrame:
        """
        Retrieve all reports from all accessible Power BI workspaces.

        This method iterates through each available workspace, fetches the reports, and
        combines them into a single DataFrame. It adds the workspace name as a column for context.

        Returns:
            pd.DataFrame: A DataFrame containing report metadata across all workspaces,
            including a 'workspaceName' column.
        """
        df_get_all_workspaces = self.get_all_workspaces()
        workspace_id_list = df_get_all_workspaces["id"]
        df_get_all_reports = pd.DataFrame()

        for workspace_id in workspace_id_list:
            try:
                workspace_name = df_get_all_workspaces.query(f'id == "{workspace_id}"')[
                    "name"
                ].iloc[0]
                result = self.get_report_by_workspace(workspace_id)
                if result.status_code == 200:
                    df = pd.DataFrame.from_dict(
                        result.json()["value"], orient="columns"
                    )
                    df["workspaceName"] = workspace_name
                    df = df.astype("str")
                    df_get_all_reports = pd.concat([df_get_all_reports, df])
            except Exception as e:
                print(f"Error processing workspace {workspace_id}: {e}")
                continue

        return df_get_all_reports

    def get_all_dataset_refresh_history(self) -> pd.DataFrame:
        """
        Retrieve the refresh history for all refreshable datasets in Power BI.

        Returns:
            pd.DataFrame: A DataFrame containing refresh logs with metadata for each dataset,
            including dataset and workspace details.
        """
        # Get all datasets
        df_get_all_datasets = self.get_all_datasets()
        # Get dataset refresh history
        df_get_all_datasets_refresh_history = pd.DataFrame()
        list_of_ds = df_get_all_datasets.query('isRefreshable == "True"')["id"]
        # Loop through dataset
        for dataset_id in list_of_ds:
            try:
                # Get workspace id
                workspace_id = df_get_all_datasets.query(
                    'id == "{0}"'.format(dataset_id)
                )["workspaceId"].iloc[0]
                # Get workspace name
                workspace_name = df_get_all_datasets.query(
                    'id == "{0}"'.format(dataset_id)
                )["workspaceName"].iloc[0]
                # Get dataset name
                dataset_name = df_get_all_datasets.query(
                    'id == "{0}"'.format(dataset_id)
                )["name"].iloc[0]
                # Send API to get data
                result = self.get_dataset_refresh_history_by_id(
                    workspace_id, dataset_id
                )
                # If result success then proceed:
                if result.status_code == 200:
                    # Parse data from json output
                    df = pd.DataFrame.from_dict(
                        result.json()["value"], orient="columns"
                    )
                    # Add column
                    df["datasetId"] = dataset_id
                    # Add column
                    df["datasetName"] = dataset_name
                    # Add column
                    df["workspaceId"] = workspace_id
                    # Add column
                    df["workspaceName"] = workspace_name
                    # Convert all columns to string type (optional)
                    df = df.astype("str")
                    # Append data
                    df_get_all_datasets_refresh_history = pd.concat(
                        [df_get_all_datasets_refresh_history, df]
                    )
            except Exception as e:
                print(f"Error processing dataset log {dataset_id}: {e}")
                continue

        return df_get_all_datasets_refresh_history

    def get_all_dataflow_refresh_history(self) -> pd.DataFrame:
        """
        Retrieve the refresh history for all dataflows in Power BI.

        Returns:
            pd.DataFrame: A DataFrame with refresh transactions for each dataflow,
            including related workspace metadata.
        """
        # Get all dataflows
        df_get_all_dataflows = self.get_all_dataflows()
        # Get dataflow refresh history
        df_get_all_dataflows_refresh_history = pd.DataFrame()
        list_of_dataflows = df_get_all_dataflows["objectId"]

        # Loop through dataflow
        for dataflow_id in list_of_dataflows:
            try:
                # Get workspace id
                workspace_id = df_get_all_dataflows.query(
                    'objectId == "{0}"'.format(dataflow_id)
                )["workspaceId"].iloc[0]
                # Get workspace name
                workspace_name = df_get_all_dataflows.query(
                    'objectId == "{0}"'.format(dataflow_id)
                )["workspaceName"].iloc[0]
                # Get dataflow name
                dataflow_name = df_get_all_dataflows.query(
                    'objectId == "{0}"'.format(dataflow_id)
                )["name"].iloc[0]
                # Send API to get data
                result = self.get_dataflow_refresh_history_by_id(
                    workspace_id, dataflow_id
                )
                # If api_call success then proceed:
                if result.status_code == 200:
                    # Parse data from json output
                    df = pd.DataFrame.from_dict(
                        result.json()["value"], orient="columns"
                    )
                    # Add column
                    df["dataflowId"] = dataflow_id
                    # Add column
                    df["dataflowName"] = dataflow_name
                    # Add column
                    df["workspaceId"] = workspace_id
                    # Add column
                    df["workspaceName"] = workspace_name
                    # Convert all columns to string type (optional)
                    df = df.astype("str")
                    # Append data
                    df_get_all_dataflows_refresh_history = pd.concat(
                        [df_get_all_dataflows_refresh_history, df]
                    )
            except Exception as e:
                print(f"Error processing dataflow {dataflow_id}: {e}")
                continue

        return df_get_all_dataflows_refresh_history

    def get_all_dataset_users(self) -> pd.DataFrame:
        """
        Retrieve user access information for all datasets in Power BI.

        Returns:
            pd.DataFrame: A DataFrame listing all users with access to each dataset,
            along with dataset and workspace identifiers.
        """

        # Get all datasets
        df_get_all_datasets = self.get_all_datasets()
        # Filter Usage Report dataset
        df_get_all_datasets = df_get_all_datasets[
            ~df_get_all_datasets["name"].str.contains("Usage Metrics")
        ]
        # Get report list
        dataset_id_list = df_get_all_datasets["id"]
        # Define an empty dataframe
        df_get_all_dataset_users = pd.DataFrame()
        # Loop through dataset
        for dataset_id in dataset_id_list:
            try:
                workspace_id = df_get_all_datasets.query(f'id == "{dataset_id}"')[
                    "workspaceId"
                ].iloc[0]
                workspace_name = df_get_all_datasets.query(f'id == "{dataset_id}"')[
                    "workspaceName"
                ].iloc[0]
                dataset_name = df_get_all_datasets.query(f'id == "{dataset_id}"')[
                    "name"
                ].iloc[0]
                # Send API call to get data
                result = self.get_dataset_users_by_id(workspace_id, dataset_id)
                # If result success then proceed:
                if result.status_code == 200:
                    # Create dataframe to store data
                    df = pd.DataFrame.from_dict(
                        result.json()["value"], orient="columns"
                    )
                    # Add workspace name column
                    df["workspaceId"] = workspace_id
                    df["workspaceName"] = workspace_name
                    df["datasetId"] = dataset_id
                    df["datasetName"] = dataset_name
                    # Convert all columns to string type (optional)
                    df = df.astype("str")
                    # Append data
                    df_get_all_dataset_users = pd.concat([df_get_all_dataset_users, df])
            except Exception as e:
                print(f"Error processing dataset {dataset_id}: {e}")
                continue

        return df_get_all_dataset_users

    def get_all_dataset_sources(self) -> pd.DataFrame:
        """
        Retrieve all data sources used across datasets in Power BI.

        Returns:
            pd.DataFrame: A DataFrame listing the connection details (server, database, URL, etc.)
            for each dataset source, including dataset and workspace metadata.
        """
        # Filter Usage Report dataset
        df_get_all_datasets = self.get_all_datasets()
        df_get_all_datasets = df_get_all_datasets[
            ~df_get_all_datasets["name"].str.contains("Usage Metrics")
        ]
        # Get report list
        dataset_id_list = df_get_all_datasets["id"]
        # Define an empty dataframe
        df_get_all_dataset_sources = pd.DataFrame()

        # Loop through dataset
        for dataset_id in dataset_id_list:
            try:
                workspace_id = df_get_all_datasets.query(f'id == "{dataset_id}"')[
                    "workspaceId"
                ].iloc[0]
                workspace_name = df_get_all_datasets.query(f'id == "{dataset_id}"')[
                    "workspaceName"
                ].iloc[0]
                dataset_name = df_get_all_datasets.query(f'id == "{dataset_id}"')[
                    "name"
                ].iloc[0]
                # Send API call to get data
                result = self.get_dataset_sources_by_id(workspace_id, dataset_id)
                # If result success then proceed:
                if result.status_code == 200:
                    # Create dataframe to store data
                    df = pd.DataFrame(result.json()["value"])
                    # Add workspace name column
                    df["workspaceId"] = workspace_id
                    df["workspaceName"] = workspace_name
                    df["datasetId"] = dataset_id
                    df["datasetName"] = dataset_name
                    # Extract more useful columns
                    df[["server", "database", "connectionString", "url", "path"]] = df[
                        "connectionDetails"
                    ].apply(self.extract_connection_details)
                    # Convert all columns to string type (optional)
                    df = df.astype("str")
                    # Append data
                    df_get_all_dataset_sources = pd.concat(
                        [df_get_all_dataset_sources, df]
                    )
            except Exception as e:
                print(
                    f"Get dataset sources - Error processing dataset {dataset_id}: {e}"
                )
                print(
                    f"Get dataset sources - Error processing dataset {dataset_id}: {e}"
                )
                continue

        return df_get_all_dataset_sources

    def get_all_dataflow_sources(self) -> pd.DataFrame:
        """
        Retrieve all data sources used across dataflows in Power BI.

        Returns:
            pd.DataFrame: A DataFrame listing connection details for each dataflow source,
            including dataflow and workspace metadata.
        """
        # Get all dataflows
        df_get_all_dataflows = self.get_all_dataflows()
        # Get report list
        dataflow_id_list = df_get_all_dataflows["objectId"]
        # Define an empty dataframe
        df_get_all_dataflow_sources = pd.DataFrame()
        # Loop through dataset
        for dataflow_id in dataflow_id_list:
            workspace_id = df_get_all_dataflows.query(f'objectId == "{dataflow_id}"')[
                "workspaceId"
            ].iloc[0]
            workspace_name = df_get_all_dataflows.query(f'objectId == "{dataflow_id}"')[
                "workspaceName"
            ].iloc[0]
            dataflow_name = df_get_all_dataflows.query(f'objectId == "{dataflow_id}"')[
                "name"
            ].iloc[0]

            result = self.get_dataflow_sources_by_id(workspace_id, dataflow_id)
            # If result success then proceed:
            if result.status_code == 200:
                try:
                    # Create dataframe to store data
                    df = pd.DataFrame(result.json()["value"])
                    # Add workspace name column
                    df["workspaceId"] = workspace_id
                    df["workspaceName"] = workspace_name
                    df["dataflowId"] = dataflow_id
                    df["dataflowName"] = dataflow_name
                    # Extract more useful columns
                    df[["server", "database", "connectionString", "url", "path"]] = df[
                        "connectionDetails"
                    ].apply(self.extract_connection_details)
                    # Convert all columns to string type (optional)
                    df = df.astype("str")
                    # Append data
                    df_get_all_dataflow_sources = pd.concat(
                        [df_get_all_dataflow_sources, df]
                    )
                except Exception as e:
                    print(f"Error processing dataflow {dataflow_id}: {e}")
                    continue

        return df_get_all_dataflow_sources

    def get_all_report_sources(self) -> pd.DataFrame:
        """
        Retrieve all data sources used across reports in Power BI.

        Returns:
            pd.DataFrame: A DataFrame listing connection details for each report source,
            including report and workspace metadata.
        """
        # Get all reports
        df_get_all_reports = self.get_all_reports()
        # Get report list
        report_id_list = df_get_all_reports["id"]
        # Define an empty dataframe
        df_get_all_report_sources = pd.DataFrame()
        # Loop through dataset
        for report_id in report_id_list:
            try:
                workspace_id = df_get_all_reports.query(f'id == "{report_id}"')[
                    "workspaceId"
                ].iloc[0]
                workspace_name = df_get_all_reports.query(f'id == "{report_id}"')[
                    "workspaceName"
                ].iloc[0]
                report_name = df_get_all_reports.query(f'id == "{report_id}"')[
                    "name"
                ].iloc[0]
                result = self.get_report_sources_by_id(workspace_id, report_id)
                # If result success then proceed:
                if result.status_code == 200:
                    # Create dataframe to store data
                    df = pd.DataFrame(result.json()["value"])
                    # Add workspace name column
                    df["workspaceId"] = workspace_id
                    df["workspaceName"] = workspace_name
                    df["reportId"] = report_id
                    df["reportName"] = report_name
                    # Extract more useful columns
                    df[["server", "database", "connectionString", "url", "path"]] = df[
                        "connectionDetails"
                    ].apply(self.extract_connection_details)
                    # Convert all columns to string type (optional)
                    df = df.astype("str")
                    # Append data
                    df_get_all_report_sources = pd.concat(
                        [df_get_all_report_sources, df]
                    )
            except Exception as e:
                print(f"Error processing report {report_id}: {e}")
                continue

        return df_get_all_report_sources

    def get_all_dataset_tables(self) -> pd.DataFrame:
        """
        Retrieve all tables from all datasets in Power BI.

        Returns:
            pd.DataFrame: A DataFrame containing table metadata for each dataset,
            including dataset and workspace identifiers.
        """
        df_get_all_datasets = self.get_all_datasets()
        dataset_id_list = df_get_all_datasets["id"]
        df_get_all_dataset_tables = pd.DataFrame()

        for dataset_id in dataset_id_list:
            try:
                workspace_id = df_get_all_datasets.query(f'id == "{dataset_id}"')[
                    "workspaceId"
                ].iloc[0]
                workspace_name = df_get_all_datasets.query(f'id == "{dataset_id}"')[
                    "workspaceName"
                ].iloc[0]
                dataset_name = df_get_all_datasets.query(f'id == "{dataset_id}"')[
                    "name"
                ].iloc[0]
                result = self.get_dataset_tables_by_id(workspace_id, dataset_id)
                if result.status_code == 200:
                    df = pd.DataFrame.from_dict(
                        result.json()["results"][0]["tables"][0]["rows"],
                        orient="columns",
                    )
                    df["workspaceId"] = workspace_id
                    df["workspaceName"] = workspace_name
                    df["datasetId"] = dataset_id
                    df["datasetName"] = dataset_name
                    # Rename columns to remove brackets
                    df.columns = [
                        col.replace("[", "").replace("]", "") for col in df.columns
                    ]
                    df = df.astype("str")
                    df_get_all_dataset_tables = pd.concat(
                        [df_get_all_dataset_tables, df]
                    )
            except Exception as e:
                print(
                    f"Get dataset tables - Error processing dataset {dataset_id}: {e}"
                )
                continue

        return df_get_all_dataset_tables

    def get_all_dataset_columns(self) -> pd.DataFrame:
        """
        Retrieve all columns from all datasets in Power BI.

        Returns:
            pd.DataFrame: A DataFrame containing column metadata for each dataset,
            including dataset and workspace identifiers.
        """
        df_get_all_datasets = self.get_all_datasets()
        dataset_id_list = df_get_all_datasets["id"]
        df_get_all_dataset_columns = pd.DataFrame()

        for dataset_id in dataset_id_list:
            try:
                workspace_id = df_get_all_datasets.query(f'id == "{dataset_id}"')[
                    "workspaceId"
                ].iloc[0]
                workspace_name = df_get_all_datasets.query(f'id == "{dataset_id}"')[
                    "workspaceName"
                ].iloc[0]
                dataset_name = df_get_all_datasets.query(f'id == "{dataset_id}"')[
                    "name"
                ].iloc[0]
                result = self.get_dataset_columns_by_id(workspace_id, dataset_id)
                if result.status_code == 200:
                    df = pd.DataFrame.from_dict(
                        result.json()["results"][0]["tables"][0]["rows"],
                        orient="columns",
                    )
                    df["workspaceId"] = workspace_id
                    df["workspaceName"] = workspace_name
                    df["datasetId"] = dataset_id
                    df["datasetName"] = dataset_name
                    df = df.astype("str")
                    # Rename columns to remove brackets
                    df.columns = [
                        col.replace("[", "").replace("]", "") for col in df.columns
                    ]
                    df_get_all_dataset_columns = pd.concat(
                        [df_get_all_dataset_columns, df]
                    )
            except Exception as e:
                print(
                    f"Get dataset columns - Error processing dataset {dataset_id}: {e}"
                )
                continue

        return df_get_all_dataset_columns

    def get_all_dataset_measures(self) -> pd.DataFrame:
        """
        Retrieve all measures from all datasets in Power BI.

        Returns:
            pd.DataFrame: A DataFrame containing measure metadata for each dataset,
            including dataset and workspace identifiers.
        """
        df_get_all_datasets = self.get_all_datasets()
        dataset_id_list = df_get_all_datasets["id"]
        df_get_all_dataset_measures = pd.DataFrame()

        for dataset_id in dataset_id_list:
            try:
                workspace_id = df_get_all_datasets.query(f'id == "{dataset_id}"')[
                    "workspaceId"
                ].iloc[0]
                workspace_name = df_get_all_datasets.query(f'id == "{dataset_id}"')[
                    "workspaceName"
                ].iloc[0]
                dataset_name = df_get_all_datasets.query(f'id == "{dataset_id}"')[
                    "name"
                ].iloc[0]
                result = self.get_dataset_measures_by_id(workspace_id, dataset_id)
                if result.status_code == 200:
                    df = pd.DataFrame.from_dict(
                        result.json()["results"][0]["tables"][0]["rows"],
                        orient="columns",
                    )
                    df["workspaceId"] = workspace_id
                    df["workspaceName"] = workspace_name
                    df["datasetId"] = dataset_id
                    df["datasetName"] = dataset_name
                    df = df.astype("str")
                    # Rename columns to remove brackets
                    df.columns = [
                        col.replace("[", "").replace("]", "") for col in df.columns
                    ]
                    df_get_all_dataset_measures = pd.concat(
                        [df_get_all_dataset_measures, df]
                    )
            except Exception as e:
                print(
                    f"Get dataset measures - Error processing dataset {dataset_id}: {e}"
                )
                continue

        return df_get_all_dataset_measures

    def get_all_dataset_calc_dependencies(self) -> pd.DataFrame:
        """
        Retrieve all calculation dependencies from all datasets in Power BI.
        Returns:
            pd.DataFrame: A DataFrame containing calculation dependency metadata for each dataset,
            including dataset and workspace identifiers.
        """
        df_get_all_datasets = self.get_all_datasets()
        dataset_id_list = df_get_all_datasets["id"]
        df_get_all_dataset_calc_dependencies = pd.DataFrame()

        for dataset_id in dataset_id_list:
            try:
                workspace_id = df_get_all_datasets.query(f'id == "{dataset_id}"')[
                    "workspaceId"
                ].iloc[0]
                workspace_name = df_get_all_datasets.query(f'id == "{dataset_id}"')[
                    "workspaceName"
                ].iloc[0]
                dataset_name = df_get_all_datasets.query(f'id == "{dataset_id}"')[
                    "name"
                ].iloc[0]
                result = self.get_dataset_calc_dependencies_by_id(
                    workspace_id, dataset_id
                )
                if result.status_code == 200:
                    df = pd.DataFrame.from_dict(
                        result.json()["results"][0]["tables"][0]["rows"],
                        orient="columns",
                    )
                    df["workspaceId"] = workspace_id
                    df["workspaceName"] = workspace_name
                    df["datasetId"] = dataset_id
                    df["datasetName"] = dataset_name
                    df = df.astype("str")
                    # Rename columns to remove brackets
                    df.columns = [
                        col.replace("[", "").replace("]", "") for col in df.columns
                    ]
                    df_get_all_dataset_calc_dependencies = pd.concat(
                        [df_get_all_dataset_calc_dependencies, df]
                    )
            except Exception as e:
                print(
                    f"Get dataset calculation dependecy - Error processing dataset {dataset_id}: {e}"
                )
                continue
