# -*- coding: utf-8 -*-


class FailedProtectionGroupDetails(object):

    """Implementation of the 'FailedProtectionGroupDetails' model.

    Specifies a list of ids of Protection Group that failed to update along
    with error details

    Attributes:
        protection_group_id (string): Specifies the id of the failed
            protection group.
        error_message (string): Specifies the error mesage for failed
            protection group.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protection_group_id":'protectionGroupId',
        "error_message":'errorMessage'
    }

    def __init__(self,
                 protection_group_id=None,
                 error_message=None):
        """Constructor for the FailedProtectionGroupDetails class"""

        # Initialize members of the class
        self.protection_group_id = protection_group_id
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
        protection_group_id = dictionary.get('protectionGroupId')
        error_message = dictionary.get('errorMessage')

        # Return an object of this model
        return cls(protection_group_id,
                   error_message)


