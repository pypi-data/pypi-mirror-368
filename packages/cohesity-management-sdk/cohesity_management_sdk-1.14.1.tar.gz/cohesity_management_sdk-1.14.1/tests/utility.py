import json
import unittest

from cohesity_management_sdk.api_helper import APIHelper


class TestUtility(unittest.TestCase):
    def verify_model_coverage(self, model_class, model_json_file):
        """
        Verifies that all attributes in the model class are present in the provided JSON file.

        Args:
        model_class (object): The model class to be verified.
        model_json_file (str): The JSON file containing the attributes to be verified.

        """

        # Read the attributes from the JSON file
        model_json_file = f"tests/{model_json_file}"
        with open(model_json_file, "r") as file:
            input_json_str = file.read()

        # Try and unserialize the json str into the model class.
        model_instance = APIHelper.json_deserialize(
            input_json_str, model_class.from_dictionary
        )

        self.assertIsInstance(model_instance, model_class)
        # Serialize the instance into json equivalent.
        serialized_model_instance = APIHelper.json_serialize(model_instance)

        assert isinstance(
            serialized_model_instance, str
        ), "Expected serialized_model_instance to be a string"

        # The input json and the serialized model string should be same.
        self.assertEqual(
            serialized_model_instance,
            json.dumps(json.loads(input_json_str), sort_keys=True),
            "Original json and deserialized data doesn't match",
        )
