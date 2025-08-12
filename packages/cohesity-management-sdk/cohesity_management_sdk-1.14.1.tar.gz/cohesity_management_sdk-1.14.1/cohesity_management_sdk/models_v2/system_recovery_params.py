# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class SystemRecoveryParams(object):
    """Implementation of the 'SystemRecoveryParams' model.

    Specifies the parameters to perform a system recovery

    Attributes:
        full_nas_path (string): Specifies the path to the recovery view.
    """

    _names = {
        "full_nas_path":"fullNasPath",
    }

    def __init__(self,
                 full_nas_path=None):
        """Constructor for the SystemRecoveryParams class"""

        self.full_nas_path = full_nas_path


    @classmethod
    def from_dictionary(cls, dictionary):
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

        full_nas_path = dictionary.get('fullNasPath')

        return cls(
            full_nas_path
        )