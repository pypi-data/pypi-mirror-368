# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.register_standalone_hyper_v_host_request_parameters
import cohesity_management_sdk.models_v2.register_hyper_v_scvmm_request_parameters
import cohesity_management_sdk.models_v2.register_hyper_v_failover_cluster_request_parameters

class HyperVSourceRegistrationParams(object):

    """Implementation of the 'HyperVSourceRegistrationParams' model.

    Specifies the paramaters to register a HyperV source.

    Attributes:
        scvmm_params (HyperVSCVMMrequestparameters): Specifies the parameters to register a HyperV SCVMM.
        standalone_cluster_params (RegisterHyperVfailoverclusterrequestparameters): Specifies the parameters to register a failover cluster.
        standalone_host_params (RegisterStandaloneHyperVhostrequestparameters): Specifies the parameters to register a standalone HyperV host.
        type (Type75Enum): Specifies the HyperV Source type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "scvmm_params":'scvmmParams',
        "standalone_cluster_params":'standaloneClusterParams',
        "standalone_host_params":'standaloneHostParams',
        "mtype":'type'
    }

    def __init__(self,
                 scvmm_params=None,
                 standalone_cluster_params=None,
                 standalone_host_params=None,
                 mtype=None):
        """Constructor for the HyperVSourceRegistrationParams class"""

        # Initialize members of the class
        self.scvmm_params = scvmm_params
        self.standalone_cluster_params = standalone_cluster_params
        self.standalone_host_params = standalone_host_params
        self.mtype = mtype


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
        scvmm_params = cohesity_management_sdk.models_v2.register_hyper_v_scvmm_request_parameters.HyperVSCVMMrequestparameters.from_dictionary(dictionary.get('scvmmParams')) if dictionary.get('scvmmParams') else None
        standalone_cluster_params = cohesity_management_sdk.models_v2.register_hyper_v_failover_cluster_request_parameters.RegisterHyperVfailoverclusterrequestparameters.from_dictionary(
            dictionary.get('standaloneClusterParams')) if dictionary.get('standaloneClusterParams') else None
        standalone_host_params = cohesity_management_sdk.models_v2.register_standalone_hyper_v_host_request_parameters.RegisterStandaloneHyperVhostrequestparameters.from_dictionary(
            dictionary.get('standaloneHostParams')) if dictionary.get('standaloneHostParams') else None
        mtype = dictionary.get('type')

        # Return an object of this model
        return cls(scvmm_params,
                   standalone_cluster_params,
                   standalone_host_params,
                   mtype)