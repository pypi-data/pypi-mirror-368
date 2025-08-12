# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.protected_object_info
import cohesity_management_sdk.models_v2.pagination_info

class GetProtectedObjectsResponse(object):

    """Implementation of the 'GetProtectedObjectsResponse' model.

    Specifies the protected objects response.

    Attributes:
        objects (list of ProtectedObjectInfo): Specifies the protected object
            backup configuration and lastRun details if it has happned.
        pagination_info (PaginationInfo): Specifies information needed to
            support pagination.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "pagination_info":'paginationInfo'
    }

    def __init__(self,
                 objects=None,
                 pagination_info=None):
        """Constructor for the GetProtectedObjectsResponse class"""

        # Initialize members of the class
        self.objects = objects
        self.pagination_info = pagination_info


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
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.protected_object_info.ProtectedObjectInfo.from_dictionary(structure))
        pagination_info = cohesity_management_sdk.models_v2.pagination_info.PaginationInfo.from_dictionary(dictionary.get('paginationInfo')) if dictionary.get('paginationInfo') else None

        # Return an object of this model
        return cls(objects,
                   pagination_info)


