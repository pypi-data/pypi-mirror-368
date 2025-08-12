from abc import ABC, abstractmethod
from typing import Dict, List

"""
BaseSchemaRetriever defines the abstract interface for retrieving schema information
from various data sources in Azure Data Lake Storage (ADLS) Gen2 or Microsoft Fabric OneLake.

Subclasses should implement the get_schema method to extract and return the schema
of the dataset located at the specified directory.

Attributes:
    account_name (str): The storage account or workspace name.
    file_system_name (str): The file system (container) name.
    directory_path (str): The path to the directory to inspect.
    token (str): The authentication token.
    expires_on (str): The token expiration timestamp.

Methods:
    get_schema(): Abstract method to be implemented by subclasses. Should return
                  the schema as a dictionary mapping table names to lists of column
                  definitions (each as a dict with column name and type).
"""

class BaseSchemaRetriever(ABC):
    def __init__(self, account_name, file_system_name, directory_path, token, expires_on):
        """
        Initialize the schema retriever with connection parameters.

        Args:
            account_name (str): The storage account or workspace name.
            file_system_name (str): The file system (container) name.
            directory_path (str): The path to the directory to inspect.
            token (str): The authentication token.
            expires_on (str): The token expiration timestamp.
        """
        self.account_name = account_name
        self.file_system_name = file_system_name
        self.directory_path = directory_path
        self.token = token
        self.expires_on = expires_on

    @abstractmethod
    def get_schema(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Retrieve the schema information for the dataset.

        Returns:
            Dict[str, List[Dict[str, str]]]: A dictionary mapping table names to lists of
            column definitions (each as a dict with column name and type).
        """
        pass
