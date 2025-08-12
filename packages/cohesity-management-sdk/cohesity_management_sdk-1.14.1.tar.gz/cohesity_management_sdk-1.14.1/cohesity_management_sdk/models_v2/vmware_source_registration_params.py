# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.register_vmware_v_center_request_parameters
import cohesity_management_sdk.models_v2.register_vmware_es_xi_host_request_parameters
import cohesity_management_sdk.models_v2.register_vmware__vcloud_director_request_parameters

class VmwareSourceRegistrationParams(object):

    """Implementation of the 'VmwareSourceRegistrationParams' model.

    Specifies the paramaters to register a VMware source.

    Attributes:
        mtype (Type32Enum): Specifies the VMware Source type.
        v_center_params (RegisterVmwareVCenterRequestParameters): Specifies
            parameters to register VMware vCenter.
        esxi_params (RegisterVmwareESXiHostRequestParameters): Specifies
            parameters to register VMware ESXi host.
        vcd_params (RegisterVmwareVcloudDirectorRequestParameters): Specifies
            parameters to register VMware vCloud director.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mtype":'type',
        "v_center_params":'vCenterParams',
        "esxi_params":'esxiParams',
        "vcd_params":'vcdParams'
    }

    def __init__(self,
                 mtype=None,
                 v_center_params=None,
                 esxi_params=None,
                 vcd_params=None):
        """Constructor for the VmwareSourceRegistrationParams class"""

        # Initialize members of the class
        self.mtype = mtype
        self.v_center_params = v_center_params
        self.esxi_params = esxi_params
        self.vcd_params = vcd_params


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
        mtype = dictionary.get('type')
        v_center_params = cohesity_management_sdk.models_v2.register_vmware_v_center_request_parameters.RegisterVmwareVCenterRequestParameters.from_dictionary(dictionary.get('vCenterParams')) if dictionary.get('vCenterParams') else None
        esxi_params = cohesity_management_sdk.models_v2.register_vmware_es_xi_host_request_parameters.RegisterVmwareESXiHostRequestParameters.from_dictionary(dictionary.get('esxiParams')) if dictionary.get('esxiParams') else None
        vcd_params = cohesity_management_sdk.models_v2.register_vmware__vcloud_director_request_parameters.RegisterVmwareVcloudDirectorRequestParameters.from_dictionary(dictionary.get('vcdParams')) if dictionary.get('vcdParams') else None

        # Return an object of this model
        return cls(mtype,
                   v_center_params,
                   esxi_params,
                   vcd_params)


