# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.down_tiering_inclusion_policy
import cohesity_management_sdk.models_v2.down_tiering_exclusion_policy

class DownTieringPolicy(object):

    """Implementation of the 'DownTieringPolicy' model.

    Specifies the Data Migration downtiering policy.

    Attributes:
        skip_back_symlink (bool): Specifies whether to create a symlink for
            the migrated data from source to target.
        auto_orphan_data_cleanup (bool): Specifies whether to remove the
            orphan data from the target if the symlink is removed from the
            source.
        inclusion (DownTieringInclusionPolicy): Specifies the files selection
            rules for downtiering.
        exclusion (DownTieringExclusionPolicy): Specifies the files exclusion
            rules for downtiering.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "skip_back_symlink":'skipBackSymlink',
        "auto_orphan_data_cleanup":'autoOrphanDataCleanup',
        "inclusion":'inclusion',
        "exclusion":'exclusion'
    }

    def __init__(self,
                 skip_back_symlink=True,
                 auto_orphan_data_cleanup=True,
                 inclusion=None,
                 exclusion=None):
        """Constructor for the DownTieringPolicy class"""

        # Initialize members of the class
        self.skip_back_symlink = skip_back_symlink
        self.auto_orphan_data_cleanup = auto_orphan_data_cleanup
        self.inclusion = inclusion
        self.exclusion = exclusion


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
        skip_back_symlink = dictionary.get("skipBackSymlink") if dictionary.get("skipBackSymlink") else True
        auto_orphan_data_cleanup = dictionary.get("autoOrphanDataCleanup") if dictionary.get("autoOrphanDataCleanup") else True
        inclusion = cohesity_management_sdk.models_v2.down_tiering_inclusion_policy.DownTieringInclusionPolicy.from_dictionary(dictionary.get('inclusion')) if dictionary.get('inclusion') else None
        exclusion = cohesity_management_sdk.models_v2.down_tiering_exclusion_policy.DownTieringExclusionPolicy.from_dictionary(dictionary.get('exclusion')) if dictionary.get('exclusion') else None

        # Return an object of this model
        return cls(skip_back_symlink,
                   auto_orphan_data_cleanup,
                   inclusion,
                   exclusion)


