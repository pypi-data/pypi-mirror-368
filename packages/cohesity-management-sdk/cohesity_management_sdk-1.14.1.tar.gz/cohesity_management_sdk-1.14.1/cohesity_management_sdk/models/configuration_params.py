# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class ConfigurationParams(object):

    """Implementation of the 'ConfigurationParams' model.

    Attributes:
        key (string): TODO: Type description here.
        reason (string): TODO: Type description here.
        value (string): TODO: Type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "key":'key',
        "reason":'reason',
        "value":'value'
    }

    def __init__(self,
                 key=None,
                 reason=None,
                 value=None):
        """Constructor for the ConfigurationParams class"""

        # Initialize members of the class
        self.key = key
        self.reason = reason
        self.value = value


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
        key = dictionary.get('key')
        reason = dictionary.get('reason')
        value = dictionary.get('value')

        # Return an object of this model
        return cls(key,
                   reason,
                   value)


