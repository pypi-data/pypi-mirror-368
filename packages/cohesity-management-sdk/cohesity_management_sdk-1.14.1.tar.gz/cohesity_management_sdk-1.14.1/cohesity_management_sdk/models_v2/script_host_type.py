# -*- coding: utf-8 -*-


class ScriptHostType(object):

    """Implementation of the 'ScriptHostType' model.

    Script Host Type

    Attributes:
        script_host_type (ScriptHostType1Enum): Specifies the host type of the
            pre/post script.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "script_host_type":'scriptHostType'
    }

    def __init__(self,
                 script_host_type=None):
        """Constructor for the ScriptHostType class"""

        # Initialize members of the class
        self.script_host_type = script_host_type


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
        script_host_type = dictionary.get('scriptHostType')

        # Return an object of this model
        return cls(script_host_type)


