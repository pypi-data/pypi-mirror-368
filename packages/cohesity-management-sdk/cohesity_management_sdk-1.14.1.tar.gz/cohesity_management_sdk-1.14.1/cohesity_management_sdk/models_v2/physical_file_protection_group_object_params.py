# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.physical_file_backup_path_params

class PhysicalFileProtectionGroupObjectParams(object):

    """Implementation of the 'PhysicalFileProtectionGroupObjectParams' model.

    TODO: type model description here.

    Attributes:
        id (long|int): Specifies the ID of the object protected.
        name (string): Specifies the name of the object protected.
        file_paths (list of PhysicalFileBackupPathParams): Specifies a list of
            file paths to be protected by this Protection Group.
        excluded_vss_writers (list of string): Specifies writer names which should be excluded from physical
          file based backups.
        uses_path_level_skip_nested_volume_setting (bool): Specifies whether
            path level or object level skip nested volume setting will be
            used.
        nested_volume_types_to_skip (list of string): Specifies mount types of
            nested volumes to be skipped.
        follow_nas_symlink_target (bool): Specifies whether to follow NAS
            target pointed by symlink for windows sources.
        metadata_file_path (string): Specifies the path of metadatafile on
            source. This file contains absolute paths of files that needs to
            be backed up on the same source.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "file_paths":'filePaths',
        "excluded_vss_writers":'excludedVssWriters',
        "uses_path_level_skip_nested_volume_setting":'usesPathLevelSkipNestedVolumeSetting',
        "nested_volume_types_to_skip":'nestedVolumeTypesToSkip',
        "follow_nas_symlink_target":'followNasSymlinkTarget',
        "metadata_file_path":'metadataFilePath'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 file_paths=None,
                 excluded_vss_writers=None,
                 uses_path_level_skip_nested_volume_setting=None,
                 nested_volume_types_to_skip=None,
                 follow_nas_symlink_target=None,
                 metadata_file_path=None):
        """Constructor for the PhysicalFileProtectionGroupObjectParams class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.file_paths = file_paths
        self.excluded_vss_writers = excluded_vss_writers
        self.uses_path_level_skip_nested_volume_setting = uses_path_level_skip_nested_volume_setting
        self.nested_volume_types_to_skip = nested_volume_types_to_skip
        self.follow_nas_symlink_target = follow_nas_symlink_target
        self.metadata_file_path = metadata_file_path


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
        id = dictionary.get('id')
        name = dictionary.get('name')
        file_paths = None
        if dictionary.get("filePaths") is not None:
            file_paths = list()
            for structure in dictionary.get('filePaths'):
                file_paths.append(cohesity_management_sdk.models_v2.physical_file_backup_path_params.PhysicalFileBackupPathParams.from_dictionary(structure))
        excluded_vss_writers = dictionary.get('excludedVssWriters')
        uses_path_level_skip_nested_volume_setting = dictionary.get('usesPathLevelSkipNestedVolumeSetting')
        nested_volume_types_to_skip = dictionary.get('nestedVolumeTypesToSkip')
        follow_nas_symlink_target = dictionary.get('followNasSymlinkTarget')
        metadata_file_path = dictionary.get('metadataFilePath')

        # Return an object of this model
        return cls(id,
                   name,
                   file_paths,
                   excluded_vss_writers,
                   uses_path_level_skip_nested_volume_setting,
                   nested_volume_types_to_skip,
                   follow_nas_symlink_target,
                   metadata_file_path)