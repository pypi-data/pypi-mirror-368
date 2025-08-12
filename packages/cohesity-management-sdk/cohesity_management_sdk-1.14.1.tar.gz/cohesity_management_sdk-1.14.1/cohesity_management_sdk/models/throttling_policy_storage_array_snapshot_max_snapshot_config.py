# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.uda_throttling_params
import cohesity_management_sdk.models.nas_throttling_params


class ThrottlingPolicy_RegisteredSourceThrottlingConfig(object):

    """Implementation of the 'ThrottlingPolicy_RegisteredSourceThrottlingConfig' model.

    TODO: type description here.


    Attributes:

        max_concurrent_backups (int): TODO: type description here.
        nas_throttling_params (NasThrottlingParams): This is applicable to all
            NAS sources. The parameters can be overridden
            by job.env_backup_params.nas_backup_params().throttling_params() in job
            settings.
        uda_throttling_params (UdaThrottlingParams): Throttling windows which
            will be applicable in case of nas_throttling_params = kScheduleBased.
    """


    # Create a mapping from Model property names to API property names
    _names = {
        "max_concurrent_backups":'maxConcurrentBackups',
        "nas_throttling_params":'nasThrottlingParams',
        "uda_throttling_params":'udaThrottlingParams',
    }
    def __init__(self,
                 max_concurrent_backups=None,
                 nas_throttling_params=None,
                 uda_throttling_params=None,
            ):

        """Constructor for the ThrottlingPolicy_RegisteredSourceThrottlingConfig class"""

        # Initialize members of the class
        self.max_concurrent_backups = max_concurrent_backups
        self.nas_throttling_params = nas_throttling_params
        self.uda_throttling_params = uda_throttling_params

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
        max_concurrent_backups = dictionary.get('maxConcurrentBackups')
        nas_throttling_params = cohesity_management_sdk.models.nas_throttling_params.NasThrottlingParams.from_dictionary(dictionary.get('nasThrottlingParams')) if dictionary.get('nasThrottlingParams') else None
        uda_throttling_params = cohesity_management_sdk.models.uda_throttling_params.UdaThrottlingParams.from_dictionary(dictionary.get('udaThrottlingParams')) if dictionary.get('udaThrottlingParams') else None

        # Return an object of this model
        return cls(
            max_concurrent_backups,
            nas_throttling_params,
            uda_throttling_params
)