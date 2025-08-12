# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.data_tiering_target
import cohesity_management_sdk.models_v2.uptiering_file_age_policy

class FileUptieringParams(object):

    """Implementation of the 'FileUptieringParams' model.

    Params common to Uptiering and Downtiering params

    Attributes:
        include_all_files (bool): If set, all files in the view will be uptiered regardless
            of file_select_policy, num_file_access, hot_file_window, file_size
            constraints.
        target (DataTieringTarget): Specifies target for data tiering.
        uptiering_file_age (UptieringFileAgePolicy): TODO: type description here.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "include_all_files":'includeAllFiles',
        "target":'target',
        "uptiering_file_age":'uptieringFileAge'
    }

    def __init__(self,
                 include_all_files=None,
                 target=None,
                 uptiering_file_age=None):
        """Constructor for the FileUptieringParams class"""

        # Initialize members of the class
        self.include_all_files = include_all_files
        self.target = target
        self.uptiering_file_age = uptiering_file_age


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
        include_all_files = dictionary.get('includeAllFiles')
        target = cohesity_management_sdk.models_v2.data_tiering_target.DataTieringTarget.from_dictionary(
            dictionary.get('target')) if dictionary.get('target') else None
        uptiering_file_age = cohesity_management_sdk.models_v2.uptiering_file_age_policy.UptieringFileAgePolicy.from_dictionary(
            dictionary.get('uptieringFileAge')) if dictionary.get('uptieringFileAge') else None

        # Return an object of this model
        return cls(include_all_files,
                   target,
                   uptiering_file_age)