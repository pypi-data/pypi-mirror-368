# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.protection_group_identifier

class ProtectedObjectsSearchMetadata(object):

    """Implementation of the 'Protected Objects Search Metadata' model.

    Specifies the metadata information about the Protection Groups, Protection
    Policy etc., for search result

    Attributes:
        unique_protection_group_identifiers (list of
            ProtectionGroupIdentifier): Specifies the list of unique
            Protection Group identifiers for all the Objects returned in the
            response.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "unique_protection_group_identifiers":'uniqueProtectionGroupIdentifiers'
    }

    def __init__(self,
                 unique_protection_group_identifiers=None):
        """Constructor for the ProtectedObjectsSearchMetadata class"""

        # Initialize members of the class
        self.unique_protection_group_identifiers = unique_protection_group_identifiers


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
        unique_protection_group_identifiers = None
        if dictionary.get("uniqueProtectionGroupIdentifiers") is not None:
            unique_protection_group_identifiers = list()
            for structure in dictionary.get('uniqueProtectionGroupIdentifiers'):
                unique_protection_group_identifiers.append(cohesity_management_sdk.models_v2.protection_group_identifier.ProtectionGroupIdentifier.from_dictionary(structure))

        # Return an object of this model
        return cls(unique_protection_group_identifiers)


