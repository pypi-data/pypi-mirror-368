# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.recover_vmware_v_ms_es_xi_source_config
import cohesity_management_sdk.models_v2.recover_vmware_v_ms_vcloud_director_source_config_1
import cohesity_management_sdk.models_v2.recover_vmware_v_ms_v_center_source_config

class NewSourceConfig6(object):

    """Implementation of the 'NewSourceConfig6' model.

    Specifies the new destination Source configuration parameters where the
    VMs will be recovered. This is mandatory if recoverToNewSource is set to
    true.

    Attributes:
        source_type (string): Specifies the type of VMware source to which the
            VMs are being restored.
        standalone_host_params (RecoverVmwareVmEsxiSourceConfig):Recover VMware VMs ESXi Source Config.
        v_center_params (RecoverVmwareVmVCenterSourceConfig): Recover VMware VMs vCenter Source Config.
        vcloud_director_params (RecoverVmwareVMsVcloudDirectorSourceConfig1):
            Specifies the new destination Source configuration where the VMs
            will be recovered for vCloudDirector sources.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source_type":'sourceType',
        "standalone_host_params":'standaloneHostParams',
        "v_center_params":'vCenterParams',
        "vcloud_director_params":'vCloudDirectorParams'
    }

    def __init__(self,
                 source_type='kvCloudDirector',
                 standalone_host_params=None,
                 v_center_params=None,
                 vcloud_director_params=None):
        """Constructor for the NewSourceConfig6 class"""

        # Initialize members of the class
        self.source_type = source_type
        self.standalone_host_params = standalone_host_params
        self.v_center_params = v_center_params
        self.vcloud_director_params = vcloud_director_params


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
        source_type = dictionary.get("sourceType") if dictionary.get("sourceType") else 'kvCloudDirector'
        standalone_host_params = cohesity_management_sdk.models_v2.recover_vmware_v_ms_es_xi_source_config.RecoverVmwareVMsESXiSourceConfig.from_dictionary(dictionary.get('standaloneHostParams')) if dictionary.get('standaloneHostParams') else None
        v_center_params = cohesity_management_sdk.models_v2.recover_vmware_v_ms_v_center_source_config.RecoverVmwareVMsVCenterSourceConfig.from_dictionary(dictionary.get('vCenterParams')) if dictionary.get('vCenterParams') else None
        vcloud_director_params = cohesity_management_sdk.models_v2.recover_vmware_v_ms_vcloud_director_source_config_1.RecoverVmwareVMsVcloudDirectorSourceConfig1.from_dictionary(dictionary.get('vCloudDirectorParams')) if dictionary.get('vCloudDirectorParams') else None

        # Return an object of this model
        return cls(source_type,
                   standalone_host_params,
                   v_center_params,
                   vcloud_director_params)