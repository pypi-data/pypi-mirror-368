# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.protection_group_info

class ViewProtection(object):

    """Implementation of the 'View Protection.' model.

    Specifies information about the Protection Groups that are protecting the
    View.

    Attributes:
        magneto_entity_id (long|int): Specifies the id of the Protection
            Source that is using this View.
        protection_groups (list of ProtectionGroupInfo): Array of Protection
            Group. Specifies the Protection Group that are protecting the
            View.
        inactive (bool): Specifies if this View is an inactive View that was
            created on this Remote Cluster to store the Snapshots created by
            replication. This inactive View cannot be NFS or SMB mounted.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "magneto_entity_id":'magnetoEntityId',
        "protection_groups":'protectionGroups',
        "inactive":'inactive'
    }

    def __init__(self,
                 magneto_entity_id=None,
                 protection_groups=None,
                 inactive=None):
        """Constructor for the ViewProtection class"""

        # Initialize members of the class
        self.magneto_entity_id = magneto_entity_id
        self.protection_groups = protection_groups
        self.inactive = inactive


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
        magneto_entity_id = dictionary.get('magnetoEntityId')
        protection_groups = None
        if dictionary.get("protectionGroups") is not None:
            protection_groups = list()
            for structure in dictionary.get('protectionGroups'):
                protection_groups.append(cohesity_management_sdk.models_v2.protection_group_info.ProtectionGroupInfo.from_dictionary(structure))
        inactive = dictionary.get('inactive')

        # Return an object of this model
        return cls(magneto_entity_id,
                   protection_groups,
                   inactive)


