import json 

class JsonHandler:
    """
    Helper class for handling JSON serialization and deserialization.
    """

    def __init__(self):
        pass

    def dict_to_json(self, data_dict):
        """
        Serialize a dictionary to JSON string.

        Args:
            data_dict (dict): The dictionary to serialize.

        Returns:
            str: The JSON string representation of the dictionary.
        """
        return json.dumps(data_dict)

    def json_to_dict(self, json_string):
        """
        Deserialize a JSON string to dictionary.

        Args:
            json_string (str): The JSON string to deserialize.

        Returns:
            dict: The dictionary representation of the JSON string.
        """
        return json.loads(json_string)
