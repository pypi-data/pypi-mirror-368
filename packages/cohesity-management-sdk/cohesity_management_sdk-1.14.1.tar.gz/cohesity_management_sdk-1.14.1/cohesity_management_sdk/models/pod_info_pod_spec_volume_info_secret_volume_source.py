# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class PodInfo_PodSpec_VolumeInfo_SecretVolumeSource(object):

    """Implementation of the 'PodInfo_PodSpec_VolumeInfo_SecretVolumeSource' model.

    Attributes:
        secret_name (string): TODO: Type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "secret_name":'secretName'
    }

    def __init__(self,
                 secret_name=None):
        """Constructor for the PodInfo_PodSpec_VolumeInfo_SecretVolumeSource class"""

        # Initialize members of the class
        self.secret_name = secret_name


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
        secret_name = dictionary.get('secretName')

        # Return an object of this model
        return cls(secret_name)


