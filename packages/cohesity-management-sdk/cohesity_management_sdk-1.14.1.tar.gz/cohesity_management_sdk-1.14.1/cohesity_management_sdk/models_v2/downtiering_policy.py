# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.indexing_policy
import cohesity_management_sdk.models_v2.retention
import cohesity_management_sdk.models_v2.downtiering_file_age_policy
import cohesity_management_sdk.models_v2.file_size_policy
import cohesity_management_sdk.models_v2.file_filtering_policy

class DowntieringPolicy(object):

    """Implementation of the 'DowntieringPolicy' model.

    Specifies the data downtiering policy.

    Attributes:
        qos_policy (QosPolicy3Enum): Specifies whether the data tiering task
            will be written to HDD or SSD.
        indexing_policy (IndexingPolicy): Specifies settings for indexing
            files found in an Object (such as a VM) so these files can be
            searched and recovered. This also specifies inclusion and
            exclusion rules that determine the directories to index.
        retention (Retention): Specifies the retention of a backup.
        skip_back_symlink (bool): Specifies whether to create a symlink for
            the migrated data from source to target.
        auto_orphan_data_cleanup (bool): Specifies whether to remove the
            orphan data from the target if the symlink is removed from the
            source.
        tiering_goal (long|int): Specifies the maximum amount of data that
            should be present on source after downtiering.
        file_age (DowntieringFileAgePolicy): Specifies the file's selection
            rule by file age for down tiering data tiering task eg. 1. select
            files older than 10 days. 2. select files last accessed 2 weeks
            ago. 3. select files last modified 1 month ago.
        enable_audit_logging (bool): Specifies whether to audit log the file
            tiering activity.
        file_size (FileSizePolicy): Specifies the file's selection rule by
            file size eg. 1. select files greather than 10 Bytes. 2. select
            files less than 20 TiB. 3. select files greather than 5 MiB. type:
            object
        file_path (FileFilteringPolicy): Specifies a set of filters for a file
            based Protection Group. These values are strings which can
            represent a prefix or suffix. Example: '/tmp' or '*.mp4'. For file
            based Protection Groups, all files under prefixes specified by the
            'includeFilters' list will be protected unless they are explicitly
            excluded by the 'excludeFilters' list.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "qos_policy":'qosPolicy',
        "indexing_policy":'indexingPolicy',
        "retention":'retention',
        "skip_back_symlink":'skipBackSymlink',
        "auto_orphan_data_cleanup":'autoOrphanDataCleanup',
        "tiering_goal":'tieringGoal',
        "file_age":'fileAge',
        "enable_audit_logging":'enableAuditLogging',
        "file_size":'fileSize',
        "file_path":'filePath'
    }

    def __init__(self,
                 qos_policy=None,
                 indexing_policy=None,
                 retention=None,
                 skip_back_symlink=True,
                 auto_orphan_data_cleanup=True,
                 tiering_goal=None,
                 file_age=None,
                 enable_audit_logging=False,
                 file_size=None,
                 file_path=None):
        """Constructor for the DowntieringPolicy class"""

        # Initialize members of the class
        self.qos_policy = qos_policy
        self.indexing_policy = indexing_policy
        self.retention = retention
        self.skip_back_symlink = skip_back_symlink
        self.auto_orphan_data_cleanup = auto_orphan_data_cleanup
        self.tiering_goal = tiering_goal
        self.file_age = file_age
        self.enable_audit_logging = enable_audit_logging
        self.file_size = file_size
        self.file_path = file_path


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
        qos_policy = dictionary.get('qosPolicy')
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None
        retention = cohesity_management_sdk.models_v2.retention.Retention.from_dictionary(dictionary.get('retention')) if dictionary.get('retention') else None
        skip_back_symlink = dictionary.get("skipBackSymlink") if dictionary.get("skipBackSymlink") else True
        auto_orphan_data_cleanup = dictionary.get("autoOrphanDataCleanup") if dictionary.get("autoOrphanDataCleanup") else True
        tiering_goal = dictionary.get('tieringGoal')
        file_age = cohesity_management_sdk.models_v2.downtiering_file_age_policy.DowntieringFileAgePolicy.from_dictionary(dictionary.get('fileAge')) if dictionary.get('fileAge') else None
        enable_audit_logging = dictionary.get("enableAuditLogging") if dictionary.get("enableAuditLogging") else False
        file_size = cohesity_management_sdk.models_v2.file_size_policy.FileSizePolicy.from_dictionary(dictionary.get('fileSize')) if dictionary.get('fileSize') else None
        file_path = cohesity_management_sdk.models_v2.file_filtering_policy.FileFilteringPolicy.from_dictionary(dictionary.get('filePath')) if dictionary.get('filePath') else None

        # Return an object of this model
        return cls(qos_policy,
                   indexing_policy,
                   retention,
                   skip_back_symlink,
                   auto_orphan_data_cleanup,
                   tiering_goal,
                   file_age,
                   enable_audit_logging,
                   file_size,
                   file_path)


