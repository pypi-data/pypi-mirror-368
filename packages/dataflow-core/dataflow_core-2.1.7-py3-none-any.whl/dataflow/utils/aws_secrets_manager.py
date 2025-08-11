import boto3
from botocore.exceptions import ClientError, EndpointConnectionError, NoCredentialsError
import json
from .json_handler import JsonHandler

class SecretsManagerClient:
    """
    A class to interact with AWS Secrets Manager for managing secrets.

    Attributes:
        client: The Boto3 client for Secrets Manager.
        json_handler: An instance of JsonHandler for handling JSON operations.
    """
    def __init__(self):
        self.json_handler = JsonHandler()
        try:
            self.client = boto3.client('secretsmanager')
        except EndpointConnectionError as e:
            self.logger.error(f"Failed to initialize SecretsManagerClient: {e}")
            raise Exception(f"Failed to initialize SecretsManagerClient: Unable to connect to the endpoint. {e}")
        except NoCredentialsError as e:
            self.logger.error(f"Failed to initialize SecretsManagerClient: {e}")
            raise Exception(f"Failed to initialize SecretsManagerClient: No AWS credentials found. {e}")


    def get_secret_by_key(self, vault_path, user_name, conn_id: str, runtime, slug):
        """
        Get information about a specific secret using a dynamically constructed vault path.

        Args:
            vault_path (str): The base vault path.
            user_name (str): The user name.
            conn_id (str): The key of the secret to retrieve.
            runtime (str, optional): The runtime environment. Defaults to None.
            slug (str, optional): The slug identifier. Defaults to None.

        Returns:
            str: Information about the secret in JSON format.

        Raises:
            Exception: If the operation fails.
        """
        try:
            if runtime and slug:
                secret_name = f"{runtime}/{slug}/{vault_path}/{conn_id}"
            else:
                secret_name = f"{user_name}/{vault_path}/{conn_id}"
            
            response = self.client.get_secret_value(SecretId=secret_name)
            secret_data = json.loads(response.get('SecretString'))

            return secret_data
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                raise Exception(f"Secret named '{conn_id}' not found with path '{secret_name}'")
            else:
                raise Exception(f"Failed to get secret '{conn_id}': {e}")
