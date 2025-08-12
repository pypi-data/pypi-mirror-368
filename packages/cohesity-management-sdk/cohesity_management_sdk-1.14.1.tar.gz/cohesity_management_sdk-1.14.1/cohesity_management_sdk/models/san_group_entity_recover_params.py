# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.san_group_entity_recover_params_san_volume_recover_params

class SANGroupEntityRecoverParams(object):

    """Implementation of the 'SANGroupEntityRecoverParams' model.

    Attributes:
        volume_recover_params_vec (list of
            SANGroupEntityRecoverParams_SANVolumeRecoverParams): Information
            about all the volumes in a group recover task.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "volume_recover_params_vec":'volumeRecoverParamsVec'
    }

    def __init__(self,
                 volume_recover_params_vec=None):
        """Constructor for the SANGroupEntityRecoverParams class"""

        # Initialize members of the class
        self.volume_recover_params_vec = volume_recover_params_vec


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
        volume_recover_params_vec = None
        if dictionary.get("volumeRecoverParamsVec") is not None:
            volume_recover_params_vec = list()
            for structure in dictionary.get('volumeRecoverParamsVec'):
                volume_recover_params_vec.append(cohesity_management_sdk.models.san_group_entity_recover_params_san_volume_recover_params.SANGroupEntityRecoverParams_SANVolumeRecoverParams.from_dictionary(structure))

        # Return an object of this model
        return cls(volume_recover_params_vec)


