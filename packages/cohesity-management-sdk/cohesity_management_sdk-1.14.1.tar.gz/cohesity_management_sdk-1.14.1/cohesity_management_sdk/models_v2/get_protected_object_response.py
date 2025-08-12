# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.protected_object_info

class GetProtectedObjectResponse(object):

    """Implementation of the 'GetProtectedObjectResponse' model.

    Specifies the protected objects response.

    Attributes:
        object (ProtectedObjectInfo): Specifies the details of a protected
            object.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object":'object'
    }

    def __init__(self,
                 object=None):
        """Constructor for the GetProtectedObjectResponse class"""

        # Initialize members of the class
        self.object = object


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
        object = cohesity_management_sdk.models_v2.protected_object_info.ProtectedObjectInfo.from_dictionary(dictionary.get('object')) if dictionary.get('object') else None

        # Return an object of this model
        return cls(object)


