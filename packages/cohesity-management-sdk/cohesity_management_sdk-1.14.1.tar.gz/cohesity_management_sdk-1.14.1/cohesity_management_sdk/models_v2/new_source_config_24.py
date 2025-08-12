# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_hyperv_v_ms_new_scvmm_source_config
import cohesity_management_sdk.models_v2.recover_hyperv_v_ms_new_standalone_host_source_config
import cohesity_management_sdk.models_v2.recover_hyperv_v_ms_new_standalone_cluster_source_config

class NewSourceConfig24(object):

    """Implementation of the 'NewSourceConfig24' model.

    Specifies the new destination Source configuration parameters where the
    VMs will be recovered. This is mandatory if recoverToNewSource is set to
    true.

    Attributes:
        source_type (SourceType1Enum): Specifies the type of HyperV source to
            which the VMs are being restored.
        scvmm_server_params (RecoverHypervVMsNewSCVMMSourceConfig): Specifies
            the new destination Source configuration where the VMs will be
            recovered.
        standalone_host_params
            (RecoverHypervVMsNewStandaloneHostSourceConfig): Specifies the new
            destination Source configuration where the VMs will be recovered.
        standalone_cluster_params
            (RecoverHypervVMsNewStandaloneClusterSourceConfig): Specifies the
            new destination Source configuration where the VMs will be
            recovered.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source_type":'sourceType',
        "scvmm_server_params":'scvmmServerParams',
        "standalone_host_params":'standaloneHostParams',
        "standalone_cluster_params":'standaloneClusterParams'
    }

    def __init__(self,
                 source_type=None,
                 scvmm_server_params=None,
                 standalone_host_params=None,
                 standalone_cluster_params=None):
        """Constructor for the NewSourceConfig24 class"""

        # Initialize members of the class
        self.source_type = source_type
        self.scvmm_server_params = scvmm_server_params
        self.standalone_host_params = standalone_host_params
        self.standalone_cluster_params = standalone_cluster_params


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
        source_type = dictionary.get('sourceType')
        scvmm_server_params = cohesity_management_sdk.models_v2.recover_hyperv_v_ms_new_scvmm_source_config.RecoverHypervVMsNewSCVMMSourceConfig.from_dictionary(dictionary.get('scvmmServerParams')) if dictionary.get('scvmmServerParams') else None
        standalone_host_params = cohesity_management_sdk.models_v2.recover_hyperv_v_ms_new_standalone_host_source_config.RecoverHypervVMsNewStandaloneHostSourceConfig.from_dictionary(dictionary.get('standaloneHostParams')) if dictionary.get('standaloneHostParams') else None
        standalone_cluster_params = cohesity_management_sdk.models_v2.recover_hyperv_v_ms_new_standalone_cluster_source_config.RecoverHypervVMsNewStandaloneClusterSourceConfig.from_dictionary(dictionary.get('standaloneClusterParams')) if dictionary.get('standaloneClusterParams') else None

        # Return an object of this model
        return cls(source_type,
                   scvmm_server_params,
                   standalone_host_params,
                   standalone_cluster_params)


