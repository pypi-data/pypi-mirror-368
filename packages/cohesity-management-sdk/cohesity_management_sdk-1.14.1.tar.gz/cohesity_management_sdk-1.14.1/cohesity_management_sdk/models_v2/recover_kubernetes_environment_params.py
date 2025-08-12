# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_kubernetes_namespace_params

class RecoverKubernetesEnvironmentParams(object):

    """Implementation of the 'Recover Kubernetes environment params.' model.

    Specifies the recovery options specific to Kubernetes environment.

    Attributes:
        recovery_action (string): Specifies the type of recover action to be
            performed.
        recover_namespace_params (RecoverKubernetesNamespaceParams): Specifies
            the parameters to recover Kubernetes Namespaces.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recovery_action":'recoveryAction',
        "recover_namespace_params":'recoverNamespaceParams'
    }

    def __init__(self,
                 recovery_action='RecoverNamespaces',
                 recover_namespace_params=None):
        """Constructor for the RecoverKubernetesEnvironmentParams class"""

        # Initialize members of the class
        self.recovery_action = recovery_action
        self.recover_namespace_params = recover_namespace_params


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
        recovery_action = dictionary.get("recoveryAction") if dictionary.get("recoveryAction") else 'RecoverNamespaces'
        recover_namespace_params = cohesity_management_sdk.models_v2.recover_kubernetes_namespace_params.RecoverKubernetesNamespaceParams.from_dictionary(dictionary.get('recoverNamespaceParams')) if dictionary.get('recoverNamespaceParams') else None

        # Return an object of this model
        return cls(recovery_action,
                   recover_namespace_params)


