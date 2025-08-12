# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.cdp_source_object_info

class MongoDBObjectParams(object):

    """Implementation of the 'MongoDBObjectParams' model.

    Specifies the parameters for MongoDB object.

    Attributes:
        cdp_info (CdpSourceObjectInfo): Specifies the Continuous Data Protection (CDP) details about
          this object. This is only available if this object if protected by a CDP
          enabled policy.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cdp_info":'cdpInfo',
    }

    def __init__(self,
                 cdp_info=None):
        """Constructor for the MongoDBObjectParams class"""

        # Initialize members of the class
        self.cdp_info = cdp_info


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
        cdp_info = cohesity_management_sdk.models_v2.cdp_source_object_info.CdpSourceObjectInfo.from_dictionary(dictionary.get('cdpInfo')) if dictionary.get('cdpInfo') else None

        # Return an object of this model
        return cls(cdp_info)