import os, requests
from .database_manager import DatabaseManager
from .utils.aws_secrets_manager import SecretsManagerClient
import json
from .configuration import ConfigurationManager


class Dataflow:
    def __init__(self):
        self.secrets_manager = SecretsManagerClient()

    def auth(self, session_id: str):
        """
        Retrieve and return user information using their session ID.
        
        Args:
            session_id (str): User's session ID from cookies
            
        Returns:
            dict: User information including username, name, email, and role
        """
        try:
            dataflow_config = ConfigurationManager('/dataflow/app/auth_config/dataflow_auth.cfg')
            auth_api = dataflow_config.get_config_value('auth', 'ui_auth_api')
            response = requests.get(
                auth_api,
                cookies={"dataflow_session": session_id, "jupyterhub-hub-login": ""}
            )
            
            if response.status_code != 200:
                return response.json()
            
            user_data = response.json()
            user_dict = {
                "user_name": user_data["user_name"], 
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"] if user_data.get("last_name") else "",
                "email": user_data["email"],
                "role": user_data["base_role"]
            }
            return user_dict
                  
        except Exception as e:
            return e
    
    def variable(self, variable_name: str):
        """
        Retrieve a Dataflow variable.
        
        Args:
            variable_name (str): Name of the variable to retrieve
            
        Returns:
            str or None: Variable value if found, None otherwise
        """
        try:
            host_name = os.environ.get("HOSTNAME", "")
            user_name = host_name.replace("jupyter-", "") if host_name.startswith("jupyter-") else host_name
            runtime = os.environ.get("RUNTIME")
            slug = os.environ.get("SLUG")

            dataflow_config = ConfigurationManager('/dataflow/app/auth_config/dataflow_auth.cfg')
            variable_api = dataflow_config.get_config_value("auth", "db_get_variables")
            if not variable_api:
                print("[Dataflow.variable] Variable Unreachable")
                return None

            if runtime:
                query_params = {
                    "variable_key": variable_name,
                    "runtime": runtime,
                    "slug": slug
                }
                response = requests.get(variable_api, params=query_params)
                if response.status_code == 200:
                    response_text = response.text.strip().strip('"')
                    return response_text
                
                query_params["slug"] = "global"
                response = requests.get(variable_api, params=query_params)
                if response.status_code == 200:
                    response_text = response.text.strip().strip('"')
                    return response_text
                else: 
                    return None

            query_params = {
                "variable_key": variable_name,
                "runtime": None,
                "slug": None,
                "created_by": user_name
            }
            response = requests.get(variable_api, params=query_params)
            if response.status_code == 200:
                response_text = response.text.strip().strip('"')
                return response_text
            else:
                return None
        except Exception as e:
            print(f"[Dataflow.variable] Exception occurred: {e}")
            return None
        
    def secret(self, secret_name: str):
        """
        Retrieve a Dataflow secret value.
        
        Args:
            secret_name (str): Name of the secret to retrieve
            
        Returns:
            str or None: Secret value if found, None otherwise
        """
        try:
            host_name = os.environ.get("HOSTNAME", "")
            user_name = host_name.replace("jupyter-", "") if host_name.startswith("jupyter-") else host_name
            runtime = os.environ.get("RUNTIME")
            slug = os.environ.get("SLUG")

            dataflow_config = ConfigurationManager('/dataflow/app/auth_config/dataflow_auth.cfg')
            secret_api = dataflow_config.get_config_value("auth", "db_get_secrets")
            if not secret_api:
                print("[Dataflow.secret] Secret API Unreachable")
                return None

            query_params = {
                "secret_key": secret_name,
                "created_by": user_name
            }

            if runtime:
                query_params["runtime"] = runtime
            if slug:
                query_params["slug"] = slug

            response = requests.get(secret_api, params=query_params)
            
            if response.status_code == 200:
                response_text = response.text.strip().strip('"')
                return response_text
            else:
                return None
        except Exception as e:
            print(f"[Dataflow.secret] Exception occurred: {e}")
            return None

    def connection(self, conn_id: str, mode="session"):
        """
        Connects with a Dataflow connection.
        
        Args:
            conn_id (str): Connection identifier
            mode (str): Return type - "session" (default) or "engine" or "url"
            
        Returns:
            Session or Engine: SQLAlchemy session or engine based on mode
        """
        try:
            host_name = os.environ["HOSTNAME"]
            user_name=host_name.replace("jupyter-","")
            runtime = os.environ.get("RUNTIME")
            slug = os.environ.get("SLUG")
            
            vault_path = "connections"
            secret = self.secrets_manager.get_secret_by_key(vault_path, user_name, conn_id, runtime, slug)

            conn_type = secret['conn_type'].lower()
            username = secret['login']
            password = secret.get('password', '')
            host = secret['host']
            port = secret['port']
            database = secret.get('schemas', '')

            user_info = f"{username}:{password}@" if password else f"{username}@"
            db_info = f"/{database}" if database else ""

            connection_string = f"{conn_type}://{user_info}{host}:{port}{db_info}"

            extra = secret.get('extra', '')            
            if extra:
                try:
                    extra_params = json.loads(extra)
                    if extra_params:
                        extra_query = "&".join(f"{key}={value}" for key, value in extra_params.items())
                        connection_string += f"?{extra_query}"
                except json.JSONDecodeError:
                    # If 'extra' is not valid JSON, skip adding extra parameters
                    pass

            if mode == "url":
                return connection_string
    
            connection_instance = DatabaseManager(connection_string)
            if mode == "engine":
                return connection_instance.get_engine()
            elif mode == "session":
                return next(connection_instance.get_session())
        
        except Exception as e:
            return None