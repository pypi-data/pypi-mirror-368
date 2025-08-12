# -*- coding: utf-8 -*-


import cohesity_management_sdk.models_v2.recover_sql_db_params

class RecoverSqlEnvironmentParams(object):

    """Implementation of the 'Recover Sql environment params.' model.

    Specifies the recovery options specific to Sql environment.

    Attributes:
        vlan_config (VlanConfig1): Specifies VLAN Params associated with the recovered. If this
          is not specified, then the VLAN settings will be automatically selected
          from one of the below options: a. If VLANs are configured on Cohesity, then
          the VLAN host/VIP will be automatically based on the client''s (e.g. ESXI
          host) IP address. b. If VLANs are not configured on Cohesity, then the partition
          hostname or VIPs will be used for Recovery.
        recovery_action (string): Specifies the type of recover action to be
            performed.
        recover_app_params (RecoverSqlDBParams): Specifies the parameters to
            recover Sql databases.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "vlan_config":'vlanConfig',
        "recovery_action":'recoveryAction',
        "recover_app_params":'recoverAppParams'
    }

    def __init__(self,
                 vlan_config=None,
                 recovery_action='RecoverApps',
                 recover_app_params=None):
        """Constructor for the RecoverSqlEnvironmentParams class"""

        # Initialize members of the class
        self.vlan_config = vlan_config
        self.recovery_action = recovery_action
        self.recover_app_params = recover_app_params


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
        vlan_config = cohesity_management_sdk.models_v2.vlan_config_1.VlanConfig1.from_dictionary(dictionary.get('vlanConfig')) if dictionary.get('vlanConfig') else None
        recovery_action = dictionary.get("recoveryAction") if dictionary.get("recoveryAction") else 'RecoverApps'
        recover_app_params = cohesity_management_sdk.models_v2.recover_sql_db_params.RecoverSqlDBParams.from_dictionary(dictionary.get('recoverAppParams')) if dictionary.get('recoverAppParams') else None

        # Return an object of this model
        return cls(vlan_config,
                   recovery_action,
                   recover_app_params)