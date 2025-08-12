# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.tdm_object
import cohesity_management_sdk.models_v2.pagination_info

class TdmObjects(object):

    """Implementation of the 'TdmObjects' model.

    Specifies a collection of TDM objects.

    Attributes:
        objects (list of TdmObject): Specifies the collection of TDM objects,
            filtered by the specified criteria.
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
        """Constructor for the TdmObjects class"""

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
                objects.append(cohesity_management_sdk.models_v2.tdm_object.TdmObject.from_dictionary(structure))
        pagination_info = cohesity_management_sdk.models_v2.pagination_info.PaginationInfo.from_dictionary(dictionary.get('paginationInfo')) if dictionary.get('paginationInfo') else None

        # Return an object of this model
        return cls(objects,
                   pagination_info)


