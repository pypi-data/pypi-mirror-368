# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.san_group_entity_recover_params
import cohesity_management_sdk.models.san_storage_array_snapshot_recover_params

class SANRecoverParams(object):

    """Implementation of the 'SANRecoverParams' model.

    Attributes:
        san_group_recover_params (SANGroupEntityRecoverParams): Field to
            contain volumes entity information for a SAN protection
            group.
        san_storage_array_snap_params (SANStorageArraySnapshotRecoverParams):
            TODO: Type description here.        

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "san_group_recover_params": 'sanGroupRecoverParams',
        "san_storage_array_snap_params": 'sanStorageArraySnapParams'
    }

    def __init__(self,
                 san_group_recover_params=None,
                 san_storage_array_snap_params=None):
        """Constructor for the SANRecoverParams class"""

        # Initialize members of the class
        self.san_group_recover_params = san_group_recover_params
        self.san_storage_array_snap_params = san_storage_array_snap_params


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
        san_group_recover_params = cohesity_management_sdk.models.san_group_entity_recover_params.SANGroupEntityRecoverParams.from_dictionary(dictionary.get('sanGroupRecoverParams')) if dictionary.get('sanGroupRecoverParams') else None
        san_storage_array_snap_params = cohesity_management_sdk.models.san_storage_array_snapshot_recover_params.SANStorageArraySnapshotRecoverParams.from_dictionary(dictionary.get('sanStorageArraySnapParams', None)) if dictionary.get('sanStorageArraySnapParams') else None

        # Return an object of this model
        return cls(san_group_recover_params,
                   san_storage_array_snap_params)


