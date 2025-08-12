# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.original_target_config
import cohesity_management_sdk.models_v2.new_target_config
import cohesity_management_sdk.models_v2.vlan_config

class AcropolisTargetParamsForRecoverFiles(object):

    """Implementation of the 'Acropolis Target Params for Recover Files' model.

    Specifies the parameters for an Acropolis files and folders recovery
    target.

    Attributes:
        recover_to_original_target (bool): Specifies whether to recover to the
            original target. If true, originalTargetConfig must be specified.
            If false, newTargetConfig must be specified.
        original_target_config (OriginalTargetConfig): Specifies the
            configuration for recovering to the original target.
        new_target_config (NewTargetConfig): Specifies the configuration for
            recovering to a new target.
        overwrite_existing (bool): Specifies whether to overwrite the existing
            files. Default is true.
        preserve_attributes (bool): Specifies whether to preserve original
            file/folder attributes. Default is true.
        continue_on_error (bool): Specifies whether to continue recovering
            other files if one of the objects encounters an error. Default is
            false.
        vlan_config (VlanConfig): Specifies VLAN Params associated with the
            recovered files and folders. If this is not specified, then the
            VLAN settings will be automatically selected from one of the below
            options: a. If VLANs are configured on Cohesity, then the VLAN
            host/VIP will be automatically based on the client's (e.g. ESXI
            host) IP address. b. If VLANs are not configured on Cohesity, then
            the partition hostname or VIPs will be used for Recovery.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recover_to_original_target":'recoverToOriginalTarget',
        "original_target_config":'originalTargetConfig',
        "new_target_config":'newTargetConfig',
        "overwrite_existing":'overwriteExisting',
        "preserve_attributes":'preserveAttributes',
        "continue_on_error":'continueOnError',
        "vlan_config":'vlanConfig'
    }

    def __init__(self,
                 recover_to_original_target=None,
                 original_target_config=None,
                 new_target_config=None,
                 overwrite_existing=None,
                 preserve_attributes=None,
                 continue_on_error=None,
                 vlan_config=None):
        """Constructor for the AcropolisTargetParamsForRecoverFiles class"""

        # Initialize members of the class
        self.recover_to_original_target = recover_to_original_target
        self.original_target_config = original_target_config
        self.new_target_config = new_target_config
        self.overwrite_existing = overwrite_existing
        self.preserve_attributes = preserve_attributes
        self.continue_on_error = continue_on_error
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
        recover_to_original_target = dictionary.get('recoverToOriginalTarget')
        original_target_config = cohesity_management_sdk.models_v2.original_target_config.OriginalTargetConfig.from_dictionary(dictionary.get('originalTargetConfig')) if dictionary.get('originalTargetConfig') else None
        new_target_config = cohesity_management_sdk.models_v2.new_target_config.NewTargetConfig.from_dictionary(dictionary.get('newTargetConfig')) if dictionary.get('newTargetConfig') else None
        overwrite_existing = dictionary.get('overwriteExisting')
        preserve_attributes = dictionary.get('preserveAttributes')
        continue_on_error = dictionary.get('continueOnError')
        vlan_config = cohesity_management_sdk.models_v2.vlan_config.VlanConfig.from_dictionary(dictionary.get('vlanConfig')) if dictionary.get('vlanConfig') else None

        # Return an object of this model
        return cls(recover_to_original_target,
                   original_target_config,
                   new_target_config,
                   overwrite_existing,
                   preserve_attributes,
                   continue_on_error,
                   vlan_config)


