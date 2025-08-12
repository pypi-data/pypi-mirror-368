# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.snapshot_information_for_an_object
import cohesity_management_sdk.models_v2.attempt_information_for_an_object

class SnapshotRunInformationForAnObject(object):

    """Implementation of the 'Snapshot run information for an object.' model.

    Specifies information about backup run for an object.

    Attributes:
        snapshot_info (SnapshotInformationForAnObject): Snapshot info for an
            object.
        failed_attempts (list of AttemptInformationForAnObject): Failed backup
            attempts for an object.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "snapshot_info":'snapshotInfo',
        "failed_attempts":'failedAttempts'
    }

    def __init__(self,
                 snapshot_info=None,
                 failed_attempts=None):
        """Constructor for the SnapshotRunInformationForAnObject class"""

        # Initialize members of the class
        self.snapshot_info = snapshot_info
        self.failed_attempts = failed_attempts


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
        snapshot_info = cohesity_management_sdk.models_v2.snapshot_information_for_an_object.SnapshotInformationForAnObject.from_dictionary(dictionary.get('snapshotInfo')) if dictionary.get('snapshotInfo') else None
        failed_attempts = None
        if dictionary.get("failedAttempts") is not None:
            failed_attempts = list()
            for structure in dictionary.get('failedAttempts'):
                failed_attempts.append(cohesity_management_sdk.models_v2.attempt_information_for_an_object.AttemptInformationForAnObject.from_dictionary(structure))

        # Return an object of this model
        return cls(snapshot_info,
                   failed_attempts)


