# -*- coding: utf-8 -*-


class CdpSourceObjectInfo(object):

    """Implementation of the 'CdpSourceObjectInfo' model.

    Specifies the CDP related information for a given object. This field
      will only be populated when protection source having protection groups which
      are configured with policy having CDP retention settings.

    Attributes:
        cdp_enabled (bool): Specifies whether CDP is currently active or not. CDP might have
          been active on this object before, but it might not be anymore.
        protection_group_ids (string): Specifies the protection group ids which belong to this source
          object for which CDP is enabled.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cdp_enabled":'cdpEnabled',
        "protection_group_ids":'protectionGroupIds',
    }

    def __init__(self,
                 cdp_enabled=None,
                 protection_group_ids=None):
        """Constructor for the CdpSourceObjectInfo class"""

        # Initialize members of the class
        self.cdp_enabled = cdp_enabled
        self.protection_group_ids = protection_group_ids


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
        cdp_enabled = dictionary.get('cdpEnabled')
        protection_group_ids = dictionary.get('protectionGroupIds')

        # Return an object of this model
        return cls(cdp_enabled,
                   protection_group_ids)