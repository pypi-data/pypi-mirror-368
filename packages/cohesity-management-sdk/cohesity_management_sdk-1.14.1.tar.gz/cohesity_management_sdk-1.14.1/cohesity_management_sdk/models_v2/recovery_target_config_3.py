# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.new_source_config_3
import cohesity_management_sdk.models_v2.recover_azure_v_ms_original_source_config

class RecoveryTargetConfig3(object):

    """Implementation of the 'RecoveryTargetConfig3' model.

    Specifies the recovery target configuration if recovery has to be done to
    a different location which is different from original source or to
    original Source with different configuration. If not specified, then the
    recovery of the vms will be performed to original location with all
    configuration parameters retained.

    Attributes:
        recover_to_new_source (bool): Specifies the parameter whether the
            recovery should be performed to a new or an existing Source
            Target.
            original_source_config (RecoverAzureVMsOriginalSourceConfig): Specifies the Source configuration if VM's are being recovered
          to Original Source.
        new_source_config (NewSourceConfig3): Specifies the new destination
            Source configuration parameters where the VMs will be recovered.
            This is mandatory if recoverToNewSource is set to true.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recover_to_new_source":'recoverToNewSource',
        "original_source_config":'originalSourceConfig',
        "new_source_config":'newSourceConfig'
    }

    def __init__(self,
                 recover_to_new_source=None,
                 original_source_config=None,
                 new_source_config=None):
        """Constructor for the RecoveryTargetConfig3 class"""

        # Initialize members of the class
        self.recover_to_new_source = recover_to_new_source
        self.original_source_config = original_source_config
        self.new_source_config = new_source_config


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
        recover_to_new_source = dictionary.get('recoverToNewSource')
        original_source_config = cohesity_management_sdk.models_v2.recover_azure_v_ms_original_source_config.RecoverAzureVMsOriginalSourceConfig.from_dictionary(
            dictionary.get('originalSourceConfig')) if dictionary.get('originalSourceConfig') else None
        new_source_config = cohesity_management_sdk.models_v2.new_source_config_3.NewSourceConfig3.from_dictionary(dictionary.get('newSourceConfig')) if dictionary.get('newSourceConfig') else None

        # Return an object of this model
        return cls(recover_to_new_source,
                   original_source_config,
                   new_source_config)