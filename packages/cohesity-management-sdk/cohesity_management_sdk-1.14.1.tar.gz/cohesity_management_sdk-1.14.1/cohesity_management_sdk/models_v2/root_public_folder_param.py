# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_recover_object_snapshot_params
import cohesity_management_sdk.models_v2.public_folder

class RootPublicFolderParam(object):

    """Implementation of the 'RootPublicFolderParam' model.

    Specifies parameters to recover a RootPublicFolder.

    Attributes:
        recover_object (CommonRecoverObjectSnapshotParams): Specifies the RootPublicFolder recover
            Object info.
        recover_entire_root_public_folder (bool): Specifies whether to recover
            the whole RootPublicFolder.
        recover_folders (list of PublicFolder): Specifies a list of Public
            Folders to recover. This field is applicable only if
            'recoverEntireRootPublicFolder' is false.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recover_object":'recoverObject',
        "recover_entire_root_public_folder":'recoverEntireRootPublicFolder',
        "recover_folders":'recoverFolders'
    }

    def __init__(self,
                 recover_object=None,
                 recover_entire_root_public_folder=None,
                 recover_folders=None):
        """Constructor for the RootPublicFolderParam class"""

        # Initialize members of the class
        self.recover_object = recover_object
        self.recover_entire_root_public_folder = recover_entire_root_public_folder
        self.recover_folders = recover_folders


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
        recover_object = cohesity_management_sdk.models_v2.common_recover_object_snapshot_params.CommonRecoverObjectSnapshotParams.from_dictionary(dictionary.get('recoverObject')) if dictionary.get('recoverObject') else None
        recover_entire_root_public_folder = dictionary.get('recoverEntireRootPublicFolder')
        recover_folders = None
        if dictionary.get("recoverFolders") is not None:
            recover_folders = list()
            for structure in dictionary.get('recoverFolders'):
                recover_folders.append(cohesity_management_sdk.models_v2.public_folder.PublicFolder.from_dictionary(structure))

        # Return an object of this model
        return cls(recover_object,
                   recover_entire_root_public_folder,
                   recover_folders)