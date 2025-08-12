# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.user
import cohesity_management_sdk.models_v2.object_summary

class CommonTdmObjectResponseParams(object):

    """Implementation of the 'CommonTdmObjectResponseParams' model.

    Specifies the common parameters for a TDM object response.

    Attributes:
        id (string): Specifies the unique ID of the object.
        name (string): Specifies the name of the object.
        status (Status11Enum): Specifies the current status of the object.
        environment (Environment12Enum): Specifies the environment of the
            object.
        created_by_user (User): Specifies the user, who created the object.
        last_refreshed_at (long|int): Specifies the timestamp (in usecs from
            epoch) when the object was last refreshed.
        size_bytes (long|int): Specifies the size (in bytes) of the object.
        parent (ObjectSummary): Specifies the parent of the object.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "environment":'environment',
        "name":'name',
        "status":'status',
        "created_by_user":'createdByUser',
        "last_refreshed_at":'lastRefreshedAt',
        "size_bytes":'sizeBytes',
        "parent":'parent'
    }

    def __init__(self,
                 id=None,
                 environment=None,
                 name=None,
                 status=None,
                 created_by_user=None,
                 last_refreshed_at=None,
                 size_bytes=None,
                 parent=None):
        """Constructor for the CommonTdmObjectResponseParams class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.status = status
        self.environment = environment
        self.created_by_user = created_by_user
        self.last_refreshed_at = last_refreshed_at
        self.size_bytes = size_bytes
        self.parent = parent


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
        id = dictionary.get('id')
        environment = dictionary.get('environment')
        name = dictionary.get('name')
        status = dictionary.get('status')
        created_by_user = cohesity_management_sdk.models_v2.user.User.from_dictionary(dictionary.get('createdByUser')) if dictionary.get('createdByUser') else None
        last_refreshed_at = dictionary.get('lastRefreshedAt')
        size_bytes = dictionary.get('sizeBytes')
        parent = cohesity_management_sdk.models_v2.object_summary.ObjectSummary.from_dictionary(dictionary.get('parent')) if dictionary.get('parent') else None

        # Return an object of this model
        return cls(id,
                   environment,
                   name,
                   status,
                   created_by_user,
                   last_refreshed_at,
                   size_bytes,
                   parent)


