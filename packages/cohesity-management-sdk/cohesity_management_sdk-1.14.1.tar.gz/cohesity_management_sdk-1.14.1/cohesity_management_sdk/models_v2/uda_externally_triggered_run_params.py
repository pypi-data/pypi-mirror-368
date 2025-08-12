# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.key_value_pair

class UdaExternallyTriggeredRunParams(object):

    """Implementation of the 'UdaExternallyTriggeredRunParams' model.

    Specifies the parameters for an externally triggered run.

    Attributes:
        backup_args (list of KeyValuePair): Specifies a map of custom arguments to be supplied to the plugin.
        control_node (string): Specifies the IP or FQDN of the source host where this backup
          will run.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "backup_args":'backupArgs',
        "control_node":'controlNode'
    }

    def __init__(self,
                 backup_args=None,
                 control_node=None):
        """Constructor for the UdaExternallyTriggeredRunParams class"""

        # Initialize members of the class
        self.backup_args = backup_args
        self.control_node = control_node

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
        backup_args =None
        if dictionary.get('backupArgs') is not None:
            backup_args = list()
            for structure in dictionary.get('backupArgs'):
                backup_args.append(cohesity_management_sdk.models_v2.key_value_pair.KeyValuePair.from_dictionary(structure))
        control_node = dictionary.get('controlNode')

        # Return an object of this model
        return cls(backup_args,
                   control_node)