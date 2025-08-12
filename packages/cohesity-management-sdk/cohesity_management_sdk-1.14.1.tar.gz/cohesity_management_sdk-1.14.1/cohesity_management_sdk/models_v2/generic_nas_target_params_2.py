# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_to_generic_nas_volume_target_params
import cohesity_management_sdk.models_v2.recover_to_original_generic_nas_volume_target_params

class GenericNasTargetParams2(object):

    """Implementation of the 'GenericNasTargetParams2' model.

    Specifies the params for a Generic NAS recovery target.

    Attributes:
        recover_to_new_source (bool): Specifies the parameter whether the
            recovery should be performed to a new or the original Generic NAS
            target.
        new_source_config (RecoverToGenericNASVolumeTargetParams): Specifies the new destination
            Source configuration parameters where the volumes will be
            recovered. This is mandatory if recoverToNewSource is set to
            true.
        original_source_config (RecoverToOriginalGenericNASVolumeTargetParams): Specifies the Source
            configuration if volumes are being recovered to original Source.
            If not specified, all the configuration parameters will be
            retained.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recover_to_new_source":'recoverToNewSource',
        "new_source_config":'newSourceConfig',
        "original_source_config":'originalSourceConfig'
    }

    def __init__(self,
                 recover_to_new_source=None,
                 new_source_config=None,
                 original_source_config=None):
        """Constructor for the GenericNasTargetParams2 class"""

        # Initialize members of the class
        self.recover_to_new_source = recover_to_new_source
        self.new_source_config = new_source_config
        self.original_source_config = original_source_config


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
        new_source_config = cohesity_management_sdk.models_v2.recover_to_generic_nas_volume_target_params.RecoverToGenericNASVolumeTargetParams.from_dictionary(dictionary.get('newSourceConfig')) if dictionary.get('newSourceConfig') else None
        original_source_config = cohesity_management_sdk.models_v2.recover_to_original_generic_nas_volume_target_params.RecoverToOriginalGenericNASVolumeTargetParams.from_dictionary(dictionary.get('originalSourceConfig')) if dictionary.get('originalSourceConfig') else None

        # Return an object of this model
        return cls(recover_to_new_source,
                   new_source_config,
                   original_source_config)