# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.pure_protection_group_object_params
import cohesity_management_sdk.models_v2.host_based_backup_script_params

class PureProtectionGroupParams(object):

    """Implementation of the 'PureProtectionGroupParams' model.

    Specifies the parameters which are specific to Pure related Protection
    Groups.

    Attributes:
        objects (list of PureProtectionGroupObjectParams): Specifies the
            objects to be included in the Protection Group.
        max_snapshots_on_primary (long|int): Specifies the number of snapshots
            to retain on the primary environment. If not specified, then
            snapshots will not be deleted from the primary environment.
        source_id (long|int): Specifies the id of the parent of the objects.
        source_name (string): Specifies the name of the parent of the
            objects.
        pre_post_script (HostBasedBackupScriptParams): Specifies params of a
            pre/post scripts to be executed before and after a backup run.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "max_snapshots_on_primary":'maxSnapshotsOnPrimary',
        "source_id":'sourceId',
        "source_name":'sourceName',
        "pre_post_script":'prePostScript'
    }

    def __init__(self,
                 objects=None,
                 max_snapshots_on_primary=None,
                 source_id=None,
                 source_name=None,
                 pre_post_script=None):
        """Constructor for the PureProtectionGroupParams class"""

        # Initialize members of the class
        self.objects = objects
        self.max_snapshots_on_primary = max_snapshots_on_primary
        self.source_id = source_id
        self.source_name = source_name
        self.pre_post_script = pre_post_script


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
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.pure_protection_group_object_params.PureProtectionGroupObjectParams.from_dictionary(structure))
        max_snapshots_on_primary = dictionary.get('maxSnapshotsOnPrimary')
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        pre_post_script = cohesity_management_sdk.models_v2.host_based_backup_script_params.HostBasedBackupScriptParams.from_dictionary(dictionary.get('prePostScript')) if dictionary.get('prePostScript') else None

        # Return an object of this model
        return cls(objects,
                   max_snapshots_on_primary,
                   source_id,
                   source_name,
                   pre_post_script)


