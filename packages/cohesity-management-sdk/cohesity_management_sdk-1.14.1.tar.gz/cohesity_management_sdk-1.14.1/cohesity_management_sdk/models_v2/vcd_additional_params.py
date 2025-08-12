# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.vcdv_center_info

class VCDAdditionalParams(object):

    """Implementation of the 'VCD Additional Params.' model.

    Additional params for VCD protection source.

    Attributes:
        vcenter_info_list (list of VCDVCenterInfo): Specifies the list of
            vCenters associated with this VCD protection source.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "vcenter_info_list":'vcenterInfoList'
    }

    def __init__(self,
                 vcenter_info_list=None):
        """Constructor for the VCDAdditionalParams class"""

        # Initialize members of the class
        self.vcenter_info_list = vcenter_info_list


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
        vcenter_info_list = None
        if dictionary.get("vcenterInfoList") is not None:
            vcenter_info_list = list()
            for structure in dictionary.get('vcenterInfoList'):
                vcenter_info_list.append(cohesity_management_sdk.models_v2.vcdv_center_info.VCDVCenterInfo.from_dictionary(structure))

        # Return an object of this model
        return cls(vcenter_info_list)


