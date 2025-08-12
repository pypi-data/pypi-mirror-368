# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.new_source_config_10
import cohesity_management_sdk.models_v2.original_source_config_6

class RecoverNetappToNetappVolumeTargetParams(object):

    """Implementation of the 'Recover Netapp To Netapp Volume Target Params.' model.

    Specifies the params of the Netapp recovery target.

    Attributes:
        recover_to_new_source (bool): Specifies the parameter whether the
            recovery should be performed to a new or the original Netapp
            target.
        new_source_config (NewSourceConfig10): Specifies the new destination
            Source configuration parameters where the volumes will be
            recovered. This is mandatory if recoverToNewSource is set to
            true.
        original_source_config (OriginalSourceConfig6): Specifies the Source
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
        """Constructor for the RecoverNetappToNetappVolumeTargetParams class"""

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
        new_source_config = cohesity_management_sdk.models_v2.new_source_config_10.NewSourceConfig10.from_dictionary(dictionary.get('newSourceConfig')) if dictionary.get('newSourceConfig') else None
        original_source_config = cohesity_management_sdk.models_v2.original_source_config_6.OriginalSourceConfig6.from_dictionary(dictionary.get('originalSourceConfig')) if dictionary.get('originalSourceConfig') else None

        # Return an object of this model
        return cls(recover_to_new_source,
                   new_source_config,
                   original_source_config)


