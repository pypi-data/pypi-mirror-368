# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.uda_throttling_params

class UdaBackupSourceParams(object):

    """Implementation of the 'UdaBackupSourceParams' model.

    Attributes:
        throttling_params (UdaThrottlingParams): TODO: Type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "throttling_params":'throttlingParams'
    }

    def __init__(self,
                 throttling_params=None):
        """Constructor for the UdaBackupSourceParams class"""

        # Initialize members of the class
        self.throttling_params = throttling_params


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
        throttling_params = cohesity_management_sdk.models.uda_throttling_params.UdaThrottlingParams.from_dictionary(dictionary.get('throttlingParams')) if dictionary.get('throttlingParams') else None

        # Return an object of this model
        return cls(throttling_params)


