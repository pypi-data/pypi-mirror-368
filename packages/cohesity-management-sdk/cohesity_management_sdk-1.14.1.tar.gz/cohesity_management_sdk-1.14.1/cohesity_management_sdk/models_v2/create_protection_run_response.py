# -*- coding: utf-8 -*-


class CreateProtectionRunResponse(object):

    """Implementation of the 'Create protection run response.' model.

    Specifies the response for create a protection run. On success, the system
    will accept the request and return the Protection Group id for which the
    run is supposed to start. The actual run may start at a later time if the
    system is busy. Consumers must query the Protection Group to see the run.

    Attributes:
        protection_group_id (string): Specifies id of the Protection Group
            which must be polled for seeing the new run.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protection_group_id":'protectionGroupId'
    }

    def __init__(self,
                 protection_group_id=None):
        """Constructor for the CreateProtectionRunResponse class"""

        # Initialize members of the class
        self.protection_group_id = protection_group_id


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

        # Return an object of this model
        return cls(protection_group_id)


