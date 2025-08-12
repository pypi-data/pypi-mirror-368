# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_hdfs_params

class RecoverHDFSEnvironmentParams(object):

    """Implementation of the 'Recover HDFS environment params.' model.

    Specifies the recovery options specific to HDFS environment.

    Attributes:
        recovery_action (string): Specifies the type of recover action to be
            performed.
        recover_hdfs_params (RecoverHDFSParams): Specifies the parameters to
            recover HDFS objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recovery_action":'recoveryAction',
        "recover_hdfs_params":'recoverHdfsParams'
    }

    def __init__(self,
                 recovery_action='RecoverObjects',
                 recover_hdfs_params=None):
        """Constructor for the RecoverHDFSEnvironmentParams class"""

        # Initialize members of the class
        self.recovery_action = recovery_action
        self.recover_hdfs_params = recover_hdfs_params


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
        recovery_action = dictionary.get("recoveryAction") if dictionary.get("recoveryAction") else 'RecoverObjects'
        recover_hdfs_params = cohesity_management_sdk.models_v2.recover_hdfs_params.RecoverHDFSParams.from_dictionary(dictionary.get('recoverHdfsParams')) if dictionary.get('recoverHdfsParams') else None

        # Return an object of this model
        return cls(recovery_action,
                   recover_hdfs_params)


