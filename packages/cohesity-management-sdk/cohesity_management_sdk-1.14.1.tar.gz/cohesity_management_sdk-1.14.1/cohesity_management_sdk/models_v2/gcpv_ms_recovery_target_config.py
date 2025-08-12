# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.new_source_config_8

class GCPVMsRecoveryTargetConfig(object):

    """Implementation of the 'GCP VMs Recovery Target Config.' model.

    Specifies the target object parameters to recover GCP vms.

    Attributes:
        recover_to_new_source (bool): Specifies the parameter whether the
            recovery should be performed to a new or an existing Source
            Target.
        new_source_config (NewSourceConfig8): Specifies the new destination
            Source configuration parameters where the VMs will be recovered.
            This is mandatory if recoverToNewSource is set to true.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recover_to_new_source":'recoverToNewSource',
        "new_source_config":'newSourceConfig'
    }

    def __init__(self,
                 recover_to_new_source=None,
                 new_source_config=None):
        """Constructor for the GCPVMsRecoveryTargetConfig class"""

        # Initialize members of the class
        self.recover_to_new_source = recover_to_new_source
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
        new_source_config = cohesity_management_sdk.models_v2.new_source_config_8.NewSourceConfig8.from_dictionary(dictionary.get('newSourceConfig')) if dictionary.get('newSourceConfig') else None

        # Return an object of this model
        return cls(recover_to_new_source,
                   new_source_config)


