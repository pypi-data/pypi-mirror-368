# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.downtiering_file_age_policy

class FileStubbingParams(object):

    """Implementation of the 'FileStubbingParams' model.

    Attributes:
        auto_orphan_data_cleanup (bool): Specifies whether to remove the
            orphan data from the target if the symlink is removed from the
            source.
        downtiering_file_age (DowntieringFileAgePolicy): TODO: type description here.
        skip_back_symlink (bool): Specifies whether to create a symlink for
            the migrated data from source to target.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "auto_orphan_data_cleanup":'autoOrphanDataCleanup',
        "downtiering_file_age":'downtieringFileAge',
        "skip_back_symlink":'skipBackSymlink'
    }

    def __init__(self,
                 auto_orphan_data_cleanup=None,
                 downtiering_file_age=None,
                 skip_back_symlink=None):
        """Constructor for the FileStubbingParams class"""

        # Initialize members of the class
        self.auto_orphan_data_cleanup = auto_orphan_data_cleanup
        self.downtiering_file_age = downtiering_file_age
        self.skip_back_symlink = skip_back_symlink


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
        auto_orphan_data_cleanup = dictionary.get('autoOrphanDataCleanup')
        downtiering_file_age = cohesity_management_sdk.models_v2.downtiering_file_age_policy.DowntieringFileAgePolicy.from_dictionary(
            dictionary.get('downtieringFileAge')) if dictionary.get('downtieringFileAge') else None
        skip_back_symlink = dictionary.get('skipBackSymlink')

        # Return an object of this model
        return cls(auto_orphan_data_cleanup,
                   downtiering_file_age,
                   skip_back_symlink)