# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_oracle_app_snapshot_params
import cohesity_management_sdk.models_v2.vlan_config_1

class RecoverOracleDBParams(object):

    """Implementation of the 'Recover Oracle DB params.' model.

    Specifies the parameters to recover Oracle databases.

    Attributes:
        target_environment (string): Specifies the environment of the recovery
            target. The corresponding params below must be filled out.
        oracle_target_params (RecoverOracleAppSnapshotParams): Specifies the
            params for recovering to a oracle host. Provided oracle backup
            should be recovered to same type of target host. For Example: If
            you have oracle backup taken from a physical host then that should
            be recovered to physical host only.
        vlan_config (VlanConfig1): Specifies VLAN Params associated with the
            recovered. If this is not specified, then the VLAN settings will
            be automatically selected from one of the below options: a. If
            VLANs are configured on Cohesity, then the VLAN host/VIP will be
            automatically based on the client's (e.g. ESXI host) IP address.
            b. If VLANs are not configured on Cohesity, then the partition
            hostname or VIPs will be used for Recovery.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "target_environment":'targetEnvironment',
        "oracle_target_params":'oracleTargetParams',
        "vlan_config":'vlanConfig'
    }

    def __init__(self,
                 target_environment='kOracle',
                 oracle_target_params=None,
                 vlan_config=None):
        """Constructor for the RecoverOracleDBParams class"""

        # Initialize members of the class
        self.target_environment = target_environment
        self.oracle_target_params = oracle_target_params
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
        target_environment = dictionary.get("targetEnvironment") if dictionary.get("targetEnvironment") else 'kOracle'
        oracle_target_params = cohesity_management_sdk.models_v2.recover_oracle_app_snapshot_params.RecoverOracleAppSnapshotParams.from_dictionary(dictionary.get('oracleTargetParams')) if dictionary.get('oracleTargetParams') else None
        vlan_config = cohesity_management_sdk.models_v2.vlan_config_1.VlanConfig1.from_dictionary(dictionary.get('vlanConfig')) if dictionary.get('vlanConfig') else None

        # Return an object of this model
        return cls(target_environment,
                   oracle_target_params,
                   vlan_config)


