# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.nas_qos_policy
import cohesity_management_sdk.models_v2.recovery_vlan_config

class ViewTargetParams(object):

    """Implementation of the 'ViewTargetParams' model.

    Specifies the params for a Cohesity view recovery target.

    Attributes:
        view_name (string): Specifies the name of the view.
        qos_policy (NasQosPolicy): Specifies the QoS policy, which defines the
            principal and priority of a NAS recovery.
        vlan_config (RecoveryVLANConfig): Specifies the VLAN configuration for
            Recovery.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "view_name":'viewName',
        "qos_policy":'qosPolicy',
        "vlan_config":'vlanConfig'
    }

    def __init__(self,
                 view_name=None,
                 qos_policy=None,
                 vlan_config=None):
        """Constructor for the ViewTargetParams class"""

        # Initialize members of the class
        self.view_name = view_name
        self.qos_policy = qos_policy
        self.vlan_config = vlan_config


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
        view_name = dictionary.get('viewName')
        qos_policy = cohesity_management_sdk.models_v2.nas_qos_policy.NasQosPolicy.from_dictionary(dictionary.get('qosPolicy')) if dictionary.get('qosPolicy') else None
        vlan_config = cohesity_management_sdk.models_v2.recovery_vlan_config.RecoveryVLANConfig.from_dictionary(dictionary.get('vlanConfig')) if dictionary.get('vlanConfig') else None

        # Return an object of this model
        return cls(view_name,
                   qos_policy,
                   vlan_config)


