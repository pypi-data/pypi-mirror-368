# -*- coding: utf-8 -*-


class MultiStageRestoreOptions(object):

    """Implementation of the 'Multi Stage Restore Options' model.

    Specifies the parameters related to multi stage Sql restore.

    Attributes:
        enable_multi_stage_restore (bool): Set this to true if you are
            creating a multi-stage Sql restore task needed for features such
            as Hot-Standby.
        enable_auto_sync (bool): Set this to true if you want to enable auto
            sync for multi stage restore.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "enable_multi_stage_restore":'enableMultiStageRestore',
        "enable_auto_sync":'enableAutoSync'
    }

    def __init__(self,
                 enable_multi_stage_restore=None,
                 enable_auto_sync=None):
        """Constructor for the MultiStageRestoreOptions class"""

        # Initialize members of the class
        self.enable_multi_stage_restore = enable_multi_stage_restore
        self.enable_auto_sync = enable_auto_sync


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
        enable_multi_stage_restore = dictionary.get('enableMultiStageRestore')
        enable_auto_sync = dictionary.get('enableAutoSync')

        # Return an object of this model
        return cls(enable_multi_stage_restore,
                   enable_auto_sync)


