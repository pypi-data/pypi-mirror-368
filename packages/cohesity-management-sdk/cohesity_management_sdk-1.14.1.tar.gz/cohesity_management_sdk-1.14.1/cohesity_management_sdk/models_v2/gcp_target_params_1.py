# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.gcp_recover_files_new_target_config
import cohesity_management_sdk.models_v2.gcp_recover_files_original_target_config
import cohesity_management_sdk.models_v2.vlan_config

class GcpTargetParams1(object):

    """Implementation of the 'GcpTargetParams1' model.

    Specifies the parameters to recover to a GCP target.

    Attributes:
        overwrite_existing (bool): Specifies whether to override the existing files. Default is
          true.
        new_target_config (GCPRecoverFilesNewTargetConfig): Specifies the configuration for recovering to a new target.
        original_target_config (GCPRecoverFilesOriginalTargetConfig): Specifies the configuration for recovering to the original target.
        recover_to_original_target (bool): Specifies whether to recover files
            to original places.
        preserve_attributes (bool): Specifies whether to preserve original
            attributes. Default is true.
        continue_on_error (bool): Specifies whether to continue recovering
            other files if one of files or folders failed to recover. Default
            value is false.
        vlan_config (VlanConfig): Specifies VLAN Params associated with the
            recovered files and folders. If this is not specified, then the
            VLAN settings will be automatically selected from one of the below
            options: a. If VLANs are configured on Cohesity, then the VLAN
            host/VIP will be automatically based on the client's (e.g. ESXI
            host) IP address. b. If VLANs are not configured on Cohesity, then
            the partition hostname or VIPs will be used for Recovery.
        recover_to_original_target (bool): Specifies whether to recover to the original target. If true,
          originalTargetConfig must be specified. If false, newTargetConfig must be
          specified.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "overwrite_existing":'overwriteExisting',
        "new_target_config":'newTargetConfig',
        "original_target_config":'originalTargetConfig',
        "preserve_attributes":'preserveAttributes',
        "continue_on_error":'continueOnError',
        "vlan_config":'vlanConfig',
        "recover_to_original_target":'recoverToOriginalTarget'
    }

    def __init__(self,
                 overwrite_existing=None,
                 new_target_config=None,
                 original_target_config=None,
                 preserve_attributes=None,
                 continue_on_error=None,
                 vlan_config=None,
                 recover_to_original_target=None):
        """Constructor for the GcpTargetParams1 class"""

        # Initialize members of the class
        self.overwrite_existing = overwrite_existing
        self.new_target_config = new_target_config
        self.original_target_config = original_target_config
        self.preserve_attributes = preserve_attributes
        self.continue_on_error = continue_on_error
        self.vlan_config = vlan_config
        self.recover_to_original_target = recover_to_original_target


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
        overwrite_existing = dictionary.get('overwriteExisting')
        new_target_config = cohesity_management_sdk.models_v2.gcp_recover_files_new_target_config.GCPRecoverFilesNewTargetConfig.from_dictionary(dictionary.get('newTargetConfig')) if dictionary.get('newTargetConfig') else None
        original_target_config = cohesity_management_sdk.models_v2.gcp_recover_files_original_target_config.GCPRecoverFilesOriginalTargetConfig.from_dictionary(dictionary.get('originalTargetConfig')) if dictionary.get('originalTargetConfig') else None
        preserve_attributes = dictionary.get('preserveAttributes')
        continue_on_error = dictionary.get('continueOnError')
        vlan_config = cohesity_management_sdk.models_v2.vlan_config.VlanConfig.from_dictionary(dictionary.get('vlanConfig')) if dictionary.get('vlanConfig') else None
        recover_to_original_target = dictionary.get('recoverToOriginalTarget')

        # Return an object of this model
        return cls(overwrite_existing,
                   new_target_config,
                   original_target_config,
                   preserve_attributes,
                   continue_on_error,
                   vlan_config,
                   recover_to_original_target)