# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.user

class TdmSnapshot(object):

    """Implementation of the 'TdmSnapshot' model.

    Specifies the response params for a TDM snapshot.

    Attributes:
        label (string): Specifies the label for the snapshot.
        id (string): Specifies the ID of the snapshot.
        is_automated (bool): Specifies whether the snapshot was taken
            automatically by the scheduler.
        created_at (long|int): Specifies the time (in usecs from epoch) when
            the snapshot was created.
        updated_at (long|int): Specifies the time (in usecs from epoch) when
            the snapshot was last updated.
        created_by_user (User): Specifies the details of the user, who created
            the snapshot. This will be null for snapshots, that are taken by
            system, such as a scheduler.
        updated_by_user (User): Specifies the details of the user, who last
            updated the snapshot.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "label":'label',
        "is_automated":'isAutomated',
        "created_at":'createdAt',
        "updated_at":'updatedAt',
        "created_by_user":'createdByUser',
        "updated_by_user":'updatedByUser'
    }

    def __init__(self,
                 id=None,
                 label=None,
                 is_automated=None,
                 created_at=None,
                 updated_at=None,
                 created_by_user=None,
                 updated_by_user=None):
        """Constructor for the TdmSnapshot class"""

        # Initialize members of the class
        self.label = label
        self.id = id
        self.is_automated = is_automated
        self.created_at = created_at
        self.updated_at = updated_at
        self.created_by_user = created_by_user
        self.updated_by_user = updated_by_user


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
        label = dictionary.get('label')
        is_automated = dictionary.get('isAutomated')
        created_at = dictionary.get('createdAt')
        updated_at = dictionary.get('updatedAt')
        created_by_user = cohesity_management_sdk.models_v2.user.User.from_dictionary(dictionary.get('createdByUser')) if dictionary.get('createdByUser') else None
        updated_by_user = cohesity_management_sdk.models_v2.user.User.from_dictionary(dictionary.get('updatedByUser')) if dictionary.get('updatedByUser') else None

        # Return an object of this model
        return cls(id,
                   label,
                   is_automated,
                   created_at,
                   updated_at,
                   created_by_user,
                   updated_by_user)


