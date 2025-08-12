# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.new_source_config_13
import cohesity_management_sdk.models_v2.original_source_config_7

class ElastifileTargetParams9(object):

    """Implementation of the 'ElastifileTargetParams9' model.

    Specifies the params for a Elastifile recovery target.

    Attributes:
        recover_to_new_source (bool): Specifies the parameter whether the
            recovery should be performed to a new or the original Elastifile
            target.
        new_source_config (NewSourceConfig13): Specifies the new destination
            Source configuration parameters where the files will be recovered.
            This is mandatory if recoverToNewSource is set to true.
        original_source_config (OriginalSourceConfig7): Specifies the Source
            configuration if files are being recovered to original Source. If
            not specified, all the configuration parameters will be retained.

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
        """Constructor for the ElastifileTargetParams9 class"""

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
        new_source_config = cohesity_management_sdk.models_v2.new_source_config_13.NewSourceConfig13.from_dictionary(dictionary.get('newSourceConfig')) if dictionary.get('newSourceConfig') else None
        original_source_config = cohesity_management_sdk.models_v2.original_source_config_7.OriginalSourceConfig7.from_dictionary(dictionary.get('originalSourceConfig')) if dictionary.get('originalSourceConfig') else None

        # Return an object of this model
        return cls(recover_to_new_source,
                   new_source_config,
                   original_source_config)


