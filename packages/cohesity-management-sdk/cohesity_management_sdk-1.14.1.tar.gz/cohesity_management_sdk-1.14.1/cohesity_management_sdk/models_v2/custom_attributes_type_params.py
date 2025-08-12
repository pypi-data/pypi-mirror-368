# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.fallback_option

class CustomAttributesTypeParams(object):

    """Implementation of the 'CustomAttributesTypeParams' model.

    Specifies the params for CustomAttributes mapping type mapping.

    Attributes:
        uid_attr_name (string): Specifies the custom field name in Active
            Directory user properties to get the UID.
        gid_attr_name (string): Specifies the custom field name in Active
            Directory user properties to get the GID.
        fallback_option (FallbackOption): Specifies a fallback user id mapping
            param in case the primary config does not work.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "uid_attr_name":'uidAttrName',
        "gid_attr_name":'gidAttrName',
        "fallback_option":'fallbackOption'
    }

    def __init__(self,
                 uid_attr_name=None,
                 gid_attr_name=None,
                 fallback_option=None):
        """Constructor for the CustomAttributesTypeParams class"""

        # Initialize members of the class
        self.uid_attr_name = uid_attr_name
        self.gid_attr_name = gid_attr_name
        self.fallback_option = fallback_option


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
        uid_attr_name = dictionary.get('uidAttrName')
        gid_attr_name = dictionary.get('gidAttrName')
        fallback_option = cohesity_management_sdk.models_v2.fallback_option.FallbackOption.from_dictionary(dictionary.get('fallbackOption')) if dictionary.get('fallbackOption') else None

        # Return an object of this model
        return cls(uid_attr_name,
                   gid_attr_name,
                   fallback_option)


