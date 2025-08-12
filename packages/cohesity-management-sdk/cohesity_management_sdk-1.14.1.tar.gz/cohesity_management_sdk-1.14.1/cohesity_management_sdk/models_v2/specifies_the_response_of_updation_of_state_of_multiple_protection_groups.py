# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.failed_protection_group_details

class SpecifiesTheResponseOfUpdationOfStateOfMultipleProtectionGroups(object):

    """Implementation of the 'Specifies the response of updation of state of multiple Protection Groups.' model.

    TODO: type model description here.

    Attributes:
        failed_protection_groups (list of FailedProtectionGroupDetails):
            Specifies a list of Protection Group ids along with details for
            which updation of state was failed.
        successful_protection_group_ids (list of string): Specifies a list of
            Protection Group ids for which updation of state was successful.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "failed_protection_groups":'failedProtectionGroups',
        "successful_protection_group_ids":'successfulProtectionGroupIds'
    }

    def __init__(self,
                 failed_protection_groups=None,
                 successful_protection_group_ids=None):
        """Constructor for the SpecifiesTheResponseOfUpdationOfStateOfMultipleProtectionGroups class"""

        # Initialize members of the class
        self.failed_protection_groups = failed_protection_groups
        self.successful_protection_group_ids = successful_protection_group_ids


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
        failed_protection_groups = None
        if dictionary.get("failedProtectionGroups") is not None:
            failed_protection_groups = list()
            for structure in dictionary.get('failedProtectionGroups'):
                failed_protection_groups.append(cohesity_management_sdk.models_v2.failed_protection_group_details.FailedProtectionGroupDetails.from_dictionary(structure))
        successful_protection_group_ids = dictionary.get('successfulProtectionGroupIds')

        # Return an object of this model
        return cls(failed_protection_groups,
                   successful_protection_group_ids)


