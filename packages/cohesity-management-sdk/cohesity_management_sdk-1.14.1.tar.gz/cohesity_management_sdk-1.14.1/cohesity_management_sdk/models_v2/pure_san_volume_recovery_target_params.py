# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_pure_volume_new_source_config
import cohesity_management_sdk.models_v2.recover_pure_volume_original_source_network_configuration

class PureSANVolumeRecoveryTargetParams(object):

    """Implementation of the 'Pure SAN Volume Recovery Target Params.' model.

    Specifies the target object parameters to recover the Pure San Volume.

    Attributes:
        recover_to_new_source (bool): Specifies whether to recover to a new
            source.
        new_source_config (RecoverPureVolumeNewSourceConfig): Specifies the new destination
            Source configuration parameters where the Pure volume will be
            recovered. This is mandatory if recoverToNewSource is set to
            true.
        original_source_config (RecoverPureVolumeOriginalSourceNetworkConfiguration): Specifies the Source
            configuration if Pure volume is being recovered to Original
            Source. If not specified, all the configuration parameters will be
            retained.
        use_thin_clone (bool): Specifies whether to use thin clone to restore storage array
          snapshots.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recover_to_new_source":'recoverToNewSource',
        "new_source_config":'newSourceConfig',
        "original_source_config":'originalSourceConfig',
        "use_thin_clone":'useThinClone'
    }

    def __init__(self,
                 recover_to_new_source=None,
                 new_source_config=None,
                 original_source_config=None,
                 use_thin_clone=None):
        """Constructor for the PureSANVolumeRecoveryTargetParams class"""

        # Initialize members of the class
        self.recover_to_new_source = recover_to_new_source
        self.new_source_config = new_source_config
        self.original_source_config = original_source_config
        self.use_thin_clone = use_thin_clone


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
        new_source_config = cohesity_management_sdk.models_v2.recover_pure_volume_new_source_config.RecoverPureVolumeNewSourceConfig.from_dictionary(dictionary.get('newSourceConfig')) if dictionary.get('newSourceConfig') else None
        original_source_config = cohesity_management_sdk.models_v2.recover_pure_volume_original_source_network_configuration.RecoverPureVolumeOriginalSourceNetworkConfiguration.from_dictionary(dictionary.get('originalSourceConfig')) if dictionary.get('originalSourceConfig') else None
        use_thin_clone = dictionary.get('useThinClone')

        # Return an object of this model
        return cls(recover_to_new_source,
                   new_source_config,
                   original_source_config,
                   use_thin_clone)