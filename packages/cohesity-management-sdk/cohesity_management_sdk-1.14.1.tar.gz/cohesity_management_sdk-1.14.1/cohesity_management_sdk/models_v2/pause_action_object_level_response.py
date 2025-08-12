# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.error

class PauseActionObjectLevelResponse(object):

    """Implementation of the 'PauseActionObjectLevelResponse' model.

    Specifies the infomration about status of pause action.

    Attributes:
        error (Error): Specifies the error object with error code and a
            message.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "error":'error'
    }

    def __init__(self,
                 error=None):
        """Constructor for the PauseActionObjectLevelResponse class"""

        # Initialize members of the class
        self.error = error


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
        error = cohesity_management_sdk.models_v2.error.Error.from_dictionary(dictionary.get('error')) if dictionary.get('error') else None

        # Return an object of this model
        return cls(error)


