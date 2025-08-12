# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.file_operation

class SnapshotDiffResult(object):

    """Implementation of the 'SnapshotDiffResult' model.

    Attributes:
        status (Status32enum): TODO Type description here.
        file_operations (list of FileOperation): TODO Type description
            here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "status":'status',
        "file_operations":'fileOperations'
    }

    def __init__(self,
                 status=None,
                 file_operations=None):
        """Constructor for the SnapshotDiffResult class"""

        # Initialize members of the class
        self.status = status
        self.file_operations = file_operations


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        status = dictionary.get('status')
        file_operations = None
        if dictionary.get("fileOperations") is not None:
            file_operations = list()
            for structure in dictionary.get('fileOperations'):
                file_operations.append(cohesity_management_sdk.models_v2.file_operation.FileOperation.from_dictionary(structure))

        # Return an object of this model
        return cls(status,
                   file_operations)