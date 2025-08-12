# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.o_365_one_drive_restore_entity_params_drive

class O365OneDriveRestoreEntityParams(object):

    """Implementation of the 'O365OneDriveRestoreEntityParams' model.

    This message defines the per object restore parameters for restoring a
    SINGLE user''s One Drive.'

    Attributes:
        drive_vec (list of O365OneDriveRestoreEntityParams_Drive): The list of
            drives that are being restored.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "drive_vec":'driveVec'
    }

    def __init__(self,
                 drive_vec=None):
        """Constructor for the O365OneDriveRestoreEntityParams class"""

        # Initialize members of the class
        self.drive_vec = drive_vec


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
        drive_vec = None
        if dictionary.get("driveVec") is not None:
            drive_vec = list()
            for structure in dictionary.get('driveVec'):
                drive_vec.append(cohesity_management_sdk.models.o_365_one_drive_restore_entity_params_drive.O365OneDriveRestoreEntityParams_Drive.from_dictionary(structure))

        # Return an object of this model
        return cls(drive_vec)


