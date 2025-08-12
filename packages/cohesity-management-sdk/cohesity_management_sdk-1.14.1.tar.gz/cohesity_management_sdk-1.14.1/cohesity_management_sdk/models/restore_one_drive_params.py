# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.restore_one_drive_params_drive_owner
import cohesity_management_sdk.models.entity_proto

class RestoreOneDriveParams(object):

    """Implementation of the 'RestoreOneDriveParams' model.

    NOTE: Per object/entity params should be put into
    O365OneDriveRestoreEntityParams going forward. Eventually
    RestoreOneDriveParams should only contain task/job level params that
    apply to all entities/users/objects in the task/job.

    Attributes:
        drive_owner_vec (list of RestoreOneDriveParamsDriveOwner): The list of
            users/groups whose drives are being restored.
        phl_folder_prefix (sring): When the drive type is
            kPreservationHoldLibrary, this folder prefix is pre-pended to the
            PHL restore path as either a folder (in the case of
            in place restore) or a folder name prefix (for alternate restore).
            If a drive with type kPreservationHoldLibrary is being restored, this
            prefix must be set as it is required for the restore.
        restore_to_original (bool): Whether or not all drive items are
            restored to original location.
        target_drive_id (string): The id of the drive in which items will be
            restored.
        target_folder_path (string): All drives part of various users listed
            in drive_owner_vec will be restored to the drive belonging to
            target_user having id target_drive_id. Let's say drive_owner_vec
            is A and B; drive_vec of A and B is 111 and 222 respectively;
            target_user is C; target_drive_id is 333. The final
            folder-hierarchy after restore job is finished will look like this
            : C:333: {target_folder_path}/| |A/111/{whatever is there in
            restore_item_vec of 111} |B/222/{whatever is there in
            restore_item_vec of 222}
        target_user (EntityProto): Specifies the attributes and the latest
            statistics about an entity.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "drive_owner_vec":'driveOwnerVec',
        "phl_folder_prefix": 'phlFolderPrefix',
        "restore_to_original":'restoreToOriginal',
        "target_drive_id":'targetDriveId',
        "target_folder_path":'targetFolderPath',
        "target_user":'targetUser'
    }

    def __init__(self,
                 drive_owner_vec=None,
                 phl_folder_prefix=None,
                 restore_to_original=None,
                 target_drive_id=None,
                 target_folder_path=None,
                 target_user=None):
        """Constructor for the RestoreOneDriveParams class"""

        # Initialize members of the class
        self.drive_owner_vec = drive_owner_vec
        self.phl_folder_prefix = phl_folder_prefix
        self.restore_to_original = restore_to_original
        self.target_drive_id = target_drive_id
        self.target_folder_path = target_folder_path
        self.target_user = target_user


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
        phl_folder_prefix = dictionary.get('phlFolderPrefix')
        drive_owner_vec = None
        if dictionary.get("driveOwnerVec") is not None:
            drive_owner_vec = list()
            for structure in dictionary.get('driveOwnerVec'):
                drive_owner_vec.append(cohesity_management_sdk.models.restore_one_drive_params_drive_owner.RestoreOneDriveParamsDriveOwner.from_dictionary(structure))
        restore_to_original = dictionary.get('restoreToOriginal')
        target_drive_id = dictionary.get('targetDriveId')
        target_folder_path = dictionary.get('targetFolderPath')
        target_user = cohesity_management_sdk.models.entity_proto.EntityProto.from_dictionary(dictionary.get('targetUser')) if dictionary.get('targetUser') else None

        # Return an object of this model
        return cls(drive_owner_vec,
                   phl_folder_prefix,
                   restore_to_original,
                   target_drive_id,
                   target_folder_path,
                   target_user)


