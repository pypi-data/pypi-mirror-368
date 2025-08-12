# -*- coding: utf-8 -*-


class TearDownStatus(object):

    """Implementation of the 'TearDownStatus' model.

    Tear Down Status

    Attributes:
        tear_down_status (TearDownStatus2Enum): Specifies the tear down
            status.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "tear_down_status":'tearDownStatus'
    }

    def __init__(self,
                 tear_down_status=None):
        """Constructor for the TearDownStatus class"""

        # Initialize members of the class
        self.tear_down_status = tear_down_status


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
        tear_down_status = dictionary.get('tearDownStatus')

        # Return an object of this model
        return cls(tear_down_status)


