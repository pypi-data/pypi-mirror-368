# -*- coding: utf-8 -*-


class CancelObjectRunsResult(object):

    """Implementation of the 'CancelObjectRunsResult' model.

    Result after canceling object runs.

    Attributes:
        object_id (long|int): Specifies the id of the object.
        error_message (string): Specifies the error message if any error
            happens.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object_id":'objectId',
        "error_message":'errorMessage'
    }

    def __init__(self,
                 object_id=None,
                 error_message=None):
        """Constructor for the CancelObjectRunsResult class"""

        # Initialize members of the class
        self.object_id = object_id
        self.error_message = error_message


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
        object_id = dictionary.get('objectId')
        error_message = dictionary.get('errorMessage')

        # Return an object of this model
        return cls(object_id,
                   error_message)


