# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.ibm_flash_system_protection_group_object_params
import cohesity_management_sdk.models_v2.host_based_backup_script_params

class IbmFlashSystemProtectionGroupParams(object):

    """Implementation of the 'IbmFlashSystemProtectionGroupParams' model.

     Specifies the parameters which are specific to IBM Flash System related
      Protection Groups.

    Attributes:
        is_safe_guarded_copy_snapshot (bool): Specifies whether the safeguarded copy snapshots are allowed
          or not
        objects (list of IbmFlashSystemProtectionGroupObjectParams): Specifies the objects to be included in the Protection Group.
        pre_post_script (HostBasedBackupScriptParams): Specifies the pre script and post script to run before and after
          the protection group.
        source_id (long|int): Specifies the id of the parent of the objects.
        source_name (string): Specifies the name of the parent of the objects.
    """
    # Create a mapping from Model property names to API property names
    _names = {
             "is_safe_guarded_copy_snapshot":'isSafeGuardedCopySnapshot',
             "objects":'objects',
             "pre_post_script":'prePostScript',
             "source_id":'sourceId',
             "source_name":'sourceName'
    }

    def __init__(self,
                 is_safe_guarded_copy_snapshot=None,
                 objects=None,
                 pre_post_script=None,
                 source_id=None,
                 source_name=None
                 ):
        """Constructor for the IbmFlashSystemProtectionGroupParams class"""

        # Initialize members of the class
        self.is_safe_guarded_copy_snapshot = is_safe_guarded_copy_snapshot
        self.objects = objects
        self.pre_post_script = pre_post_script
        self.source_id = source_id
        self.source_name = source_name



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
        is_safe_guarded_copy_snapshot = dictionary.get('isSafeGuardedCopySnapshot')
        objects = None
        if dictionary.get("objects") is not None:
            for structure in dictionary.get('objects'):
                objects = list()
                for structure in dictionary.get('objects'):
                    objects.append(cohesity_management_sdk.models_v2.ibm_flash_system_protection_group_object_params.IbmFlashSystemProtectionGroupParams.from_dictionary(structure))
        pre_post_script = cohesity_management_sdk.models_v2.host_based_backup_script_params.HostBasedBackupScriptParams.from_dictionary(dictionary.get('prePostScript')) if dictionary.get('prePostScript') else None
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')

        # Return an object of this model
        return cls(is_safe_guarded_copy_snapshot,
                   objects,
                   pre_post_script,
                   source_id,
                   source_name)