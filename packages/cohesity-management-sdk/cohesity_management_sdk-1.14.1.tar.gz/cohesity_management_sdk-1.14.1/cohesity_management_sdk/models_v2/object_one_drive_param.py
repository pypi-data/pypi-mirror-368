# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_recover_object_snapshot_params
import cohesity_management_sdk.models_v2.one_drive_param

class ObjectOneDriveParam(object):

    """Implementation of the 'ObjectOneDriveParam' model.

    Specifies OneDrive recovery parameters associated with a user.

    Attributes:
        owner_info (CommonRecoverObjectSnapshotParams): Specifies the OneDrive owner info.
        one_drive_params (list of OneDriveParam): Specifies parameters to
            recover a OneDrive.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "owner_info":'ownerInfo',
        "one_drive_params":'oneDriveParams'
    }

    def __init__(self,
                 owner_info=None,
                 one_drive_params=None):
        """Constructor for the ObjectOneDriveParam class"""

        # Initialize members of the class
        self.owner_info = owner_info
        self.one_drive_params = one_drive_params


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
        owner_info = cohesity_management_sdk.models_v2.common_recover_object_snapshot_params.CommonRecoverObjectSnapshotParams.from_dictionary(dictionary.get('ownerInfo')) if dictionary.get('ownerInfo') else None
        one_drive_params = None
        if dictionary.get("oneDriveParams") is not None:
            one_drive_params = list()
            for structure in dictionary.get('oneDriveParams'):
                one_drive_params.append(cohesity_management_sdk.models_v2.one_drive_param.OneDriveParam.from_dictionary(structure))

        # Return an object of this model
        return cls(owner_info,
                   one_drive_params)