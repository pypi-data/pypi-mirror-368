# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class HadoopDiscoveryParams(object):

    """Implementation of the 'HadoopDiscoveryParams' model.

    Specifies an Object containing information about discovering a Hadoop
    source.

    Attributes:
        config_directory (string): Specifies the configuration directory
        host (string):  Specifies the host IP.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "config_directory": 'configDirectory',
        "host": 'host'
    }

    def __init__(self,
                 config_directory=None,
                 host=None):
        """Constructor for the HadoopDiscoveryParams class"""

        # Initialize members of the class
        self.config_directory = config_directory
        self.host = host


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
        config_directory = dictionary.get('configDirectory', None)
        host = dictionary.get('host', None)

        # Return an object of this model
        return cls(config_directory,
                   host)


