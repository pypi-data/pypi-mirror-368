# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.rigel_claim_info
import cohesity_management_sdk.models_v2.rigel_connection_info

class RigelRegistrationConfig(object):

    """Implementation of the 'Rigel Registration Config.' model.

    Specifies the Rigel Registration Config.

    Attributes:
        reg_info (RigelClaimInfo): Specifies the Rigel registration info.
        control_plane_connection_info (RigelConnectionInfo): Specifies the
            Rigel connection info.
        data_plane_connection_info (RigelConnectionInfo): Specifies the Rigel
            connection info.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "reg_info":'regInfo',
        "control_plane_connection_info":'controlPlaneConnectionInfo',
        "data_plane_connection_info":'dataPlaneConnectionInfo'
    }

    def __init__(self,
                 reg_info=None,
                 control_plane_connection_info=None,
                 data_plane_connection_info=None):
        """Constructor for the RigelRegistrationConfig class"""

        # Initialize members of the class
        self.reg_info = reg_info
        self.control_plane_connection_info = control_plane_connection_info
        self.data_plane_connection_info = data_plane_connection_info


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
        reg_info = cohesity_management_sdk.models_v2.rigel_claim_info.RigelClaimInfo.from_dictionary(dictionary.get('regInfo')) if dictionary.get('regInfo') else None
        control_plane_connection_info = cohesity_management_sdk.models_v2.rigel_connection_info.RigelConnectionInfo.from_dictionary(dictionary.get('controlPlaneConnectionInfo')) if dictionary.get('controlPlaneConnectionInfo') else None
        data_plane_connection_info = cohesity_management_sdk.models_v2.rigel_connection_info.RigelConnectionInfo.from_dictionary(dictionary.get('dataPlaneConnectionInfo')) if dictionary.get('dataPlaneConnectionInfo') else None

        # Return an object of this model
        return cls(reg_info,
                   control_plane_connection_info,
                   data_plane_connection_info)


