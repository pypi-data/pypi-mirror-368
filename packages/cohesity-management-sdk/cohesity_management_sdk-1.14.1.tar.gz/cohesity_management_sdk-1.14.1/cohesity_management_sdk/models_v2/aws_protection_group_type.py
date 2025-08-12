# -*- coding: utf-8 -*-


class AWSProtectionGroupType(object):

    """Implementation of the 'AWS Protection Group type.' model.

    AWS Protection Group type.

    Attributes:
        environment (EnvironmentEnum): Specifies AWS Protection Group type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "environment":'environment'
    }

    def __init__(self,
                 environment=None):
        """Constructor for the AWSProtectionGroupType class"""

        # Initialize members of the class
        self.environment = environment


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
        environment = dictionary.get('environment')

        # Return an object of this model
        return cls(environment)


