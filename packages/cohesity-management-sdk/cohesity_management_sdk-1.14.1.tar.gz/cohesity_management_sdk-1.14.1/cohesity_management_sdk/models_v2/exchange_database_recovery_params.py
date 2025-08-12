# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.database_source
import cohesity_management_sdk.models_v2.recovery_target_config_10
import cohesity_management_sdk.models_v2.view_options

class ExchangeDatabaseRecoveryParams(object):

    """Implementation of the 'Exchange database Recovery params.' model.

    Specifies the parameters to recover an Exchange database. database.

    Attributes:
        database_source (DatabaseSource): Specifies the source id of Exchange
            database which has to be recovered.
        recover_to_new_source (bool): Specifies the parameter whether the
            recovery should be performed to a new or an existing Source
            Target.
        recovery_target_config (RecoveryTargetConfig10): Specifies the
            recovery target configuration if recovery has to be done to a
            different location which is different from original source.
        restore_type (string): Specifies the type of exchange restore.
        view_options (ViewOptions): Specifies the parameters related to the
            Exchange restore of type view. All the files related to one
            database are cloned to a view and the view can be used by third
            party tools like Kroll, etc. to restore exchange databases.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "database_source":'databaseSource',
        "recover_to_new_source":'recoverToNewSource',
        "restore_type":'restoreType',
        "recovery_target_config":'recoveryTargetConfig',
        "view_options":'viewOptions'
    }

    def __init__(self,
                 database_source=None,
                 recover_to_new_source=None,
                 restore_type='RestoreView',
                 recovery_target_config=None,
                 view_options=None):
        """Constructor for the ExchangeDatabaseRecoveryParams class"""

        # Initialize members of the class
        self.database_source = database_source
        self.recover_to_new_source = recover_to_new_source
        self.recovery_target_config = recovery_target_config
        self.restore_type = restore_type
        self.view_options = view_options


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
        database_source = cohesity_management_sdk.models_v2.database_source.DatabaseSource.from_dictionary(dictionary.get('databaseSource')) if dictionary.get('databaseSource') else None
        recover_to_new_source = dictionary.get('recoverToNewSource')
        restore_type = dictionary.get("restoreType") if dictionary.get("restoreType") else 'RestoreView'
        recovery_target_config = cohesity_management_sdk.models_v2.recovery_target_config_10.RecoveryTargetConfig10.from_dictionary(dictionary.get('recoveryTargetConfig')) if dictionary.get('recoveryTargetConfig') else None
        view_options = cohesity_management_sdk.models_v2.view_options.ViewOptions.from_dictionary(dictionary.get('viewOptions')) if dictionary.get('viewOptions') else None

        # Return an object of this model
        return cls(database_source,
                   recover_to_new_source,
                   restore_type,
                   recovery_target_config,
                   view_options)


