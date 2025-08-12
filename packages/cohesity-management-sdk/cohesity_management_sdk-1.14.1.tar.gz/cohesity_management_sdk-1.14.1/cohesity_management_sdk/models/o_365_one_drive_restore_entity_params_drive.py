# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.o_365_one_drive_restore_entity_params_drive_item

class O365OneDriveRestoreEntityParams_Drive(object):

    """Implementation of the 'O365OneDriveRestoreEntityParams_Drive' model.

    Attributes:
        drive_type (int):  Type of OneDrive drive being stored.
        is_entire_drive_required (bool): Specify if the entire drive is to be
            restored.
            This field should be false if restore_item_vec size > 0.
        restore_drive_id (string): Id of the drive whose items are being
            restored.
        restore_item_vec (list of O365OneDriveRestoreEntityParams_DriveItem): List
            of drive paths that need to be restored. Used for partial drive
            recovery

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "drive_type":'driveType',
        "is_entire_drive_required":'isEntireDriveRequired',
        "restore_drive_id":'restoreDriveId',
        "restore_item_vec":'restoreItemVec'
    }

    def __init__(self,
                 drive_type=None,
                 is_entire_drive_required=None,
                 restore_drive_id=None,
                 restore_item_vec=None):
        """Constructor for the O365OneDriveRestoreEntityParams_Drive class"""

        # Initialize members of the class
        self.drive_type = drive_type
        self.is_entire_drive_required = is_entire_drive_required
        self.restore_drive_id = restore_drive_id
        self.restore_item_vec = restore_item_vec


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
        drive_type = dictionary.get('driveType')
        is_entire_drive_required = dictionary.get('isEntireDriveRequired')
        restore_drive_id = dictionary.get('restoreDriveId')
        restore_item_vec = None
        if dictionary.get("restoreItemVec") is not None:
            restore_item_vec = list()
            for structure in dictionary.get('restoreItemVec'):
                restore_item_vec.append(cohesity_management_sdk.models.o_365_one_drive_restore_entity_params_drive_item.O365OneDriveRestoreEntityParams_DriveItem.from_dictionary(structure))

        # Return an object of this model
        return cls(drive_type,
                   is_entire_drive_required,
                   restore_drive_id,
                   restore_item_vec)