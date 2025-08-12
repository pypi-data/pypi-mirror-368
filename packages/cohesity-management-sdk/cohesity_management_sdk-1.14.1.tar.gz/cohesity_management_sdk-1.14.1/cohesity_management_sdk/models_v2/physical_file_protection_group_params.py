# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.physical_file_protection_group_object_params
import cohesity_management_sdk.models_v2.indexing_policy
import cohesity_management_sdk.models_v2.pre_and_post_script_params
import cohesity_management_sdk.models_v2.cancellation_timeout_params

class PhysicalFileProtectionGroupParams(object):

    """Implementation of the 'PhysicalFileProtectionGroupParams' model.

    Specifies the parameters which are specific to Physical related Protection
    Groups.

    Attributes:
        allow_parallel_runs (bool): If this field is set to true, then we will
            allow parallel runs for the job for the adapters which support
            parallel runs.
        cobmr_backup (bool): Specifies whether to take CoBMR backup.
        continue_on_error (bool): Specifies if physical file based backup should be continued or
          failed immediately on encountering an error.
        objects (list of PhysicalFileProtectionGroupObjectParams): Specifies
            the list of objects protected by this Protection Group.
        indexing_policy (IndexingPolicy): Specifies settings for indexing
            files found in an Object (such as a VM) so these files can be
            searched and recovered. This also specifies inclusion and
            exclusion rules that determine the directories to index.
        perform_source_side_deduplication (bool): Specifies whether or not to
            perform source side deduplication on this Protection Group.
        quiesce (bool): Specifies Whether to take app-consistent snapshots by
            quiescing apps and the filesystem before taking a backup.
        continue_on_quiesce_failure (bool): Specifies whether to continue
            backing up on quiesce failure.
        excluded_vss_writers (list of string): Specifies writer names which should be excluded from physical
          file based backups.
        global_exclude_fs (list of string): Specifies global exclude filesystems which are applied to all
          sources in a job.
        perform_brick_based_deduplication (bool): Specifies whether or not to perform brick based deduplication
          on this Protection Group.
        pre_post_script (PreAndPostScriptParams): Specifies the params for pre
            and post scripts.
        dedup_exclusion_source_ids (list of long|int): Specifies ids of
            sources for which deduplication has to be disabled.
        global_exclude_paths (list of string): Specifies global exclude
            filters which are applied to all sources in a job.
        ignorable_errors (IgnorableErrorsEnum): Specifies the Errors to be
            ignored in error db.
        task_timeouts (list of CancellationTimeoutParams): Specifies the timeouts for all the objects inside this Protection
          Group, for both full and incremental backups.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "allow_parallel_runs":'allowParallelRuns',
        "cobmr_backup":'cobmrBackup',
        "continue_on_error":'continueOnError',
        "objects":'objects',
        "indexing_policy":'indexingPolicy',
        "perform_source_side_deduplication":'performSourceSideDeduplication',
        "quiesce":'quiesce',
        "continue_on_quiesce_failure":'continueOnQuiesceFailure',
        "excluded_vss_writers":'excludedVssWriters',
        "global_exclude_fs":'globalExcludeFS',
        "perform_brick_based_deduplication":'performBrickBasedDeduplication',
        "pre_post_script":'prePostScript',
        "dedup_exclusion_source_ids":'dedupExclusionSourceIds',
        "global_exclude_paths":'globalExcludePaths',
        "ignorable_errors": 'ignorableErrors',
        "task_timeouts": 'taskTimeouts'
    }

    def __init__(self,
                 allow_parallel_runs=None,
                 cobmr_backup=None,
                 continue_on_error=None,
                 objects=None,
                 indexing_policy=None,
                 perform_source_side_deduplication=None,
                 quiesce=None,
                 continue_on_quiesce_failure=None,
                 excluded_vss_writers=None,
                 global_exclude_fs=None,
                 perform_brick_based_deduplication=None,
                 pre_post_script=None,
                 dedup_exclusion_source_ids=None,
                 global_exclude_paths=None,
                 ignorable_errors=None,
                 task_timeouts=None):
        """Constructor for the PhysicalFileProtectionGroupParams class"""

        # Initialize members of the class
        self.allow_parallel_runs = allow_parallel_runs
        self.cobmr_backup = cobmr_backup
        self.continue_on_error = continue_on_error
        self.objects = objects
        self.indexing_policy = indexing_policy
        self.perform_source_side_deduplication = perform_source_side_deduplication
        self.quiesce = quiesce
        self.continue_on_quiesce_failure = continue_on_quiesce_failure
        self.excluded_vss_writers = excluded_vss_writers
        self.global_exclude_fs = global_exclude_fs
        self.perform_brick_based_deduplication = perform_brick_based_deduplication
        self.pre_post_script = pre_post_script
        self.dedup_exclusion_source_ids = dedup_exclusion_source_ids
        self.global_exclude_paths = global_exclude_paths
        self.ignorable_errors = ignorable_errors
        self.task_timeouts = task_timeouts


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
        allow_parallel_runs = dictionary.get('allowParallelRuns')
        cobmr_backup = dictionary.get('cobmrBackup')
        continue_on_error = dictionary.get('continueOnError')
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.physical_file_protection_group_object_params.PhysicalFileProtectionGroupObjectParams.from_dictionary(structure))
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None
        perform_source_side_deduplication = dictionary.get('performSourceSideDeduplication')
        quiesce = dictionary.get('quiesce')
        continue_on_quiesce_failure = dictionary.get('continueOnQuiesceFailure')
        excluded_vss_writers = dictionary.get('excludedVssWriters')
        global_exclude_fs = dictionary.get('globalExcludeFS')
        perform_brick_based_deduplication = dictionary.get('performBrickBasedDeduplication')
        pre_post_script = cohesity_management_sdk.models_v2.pre_and_post_script_params.PreAndPostScriptParams.from_dictionary(dictionary.get('prePostScript')) if dictionary.get('prePostScript') else None
        dedup_exclusion_source_ids = dictionary.get('dedupExclusionSourceIds')
        global_exclude_paths = dictionary.get('globalExcludePaths')
        ignorable_errors = dictionary.get('ignorableErrors')
        task_timeouts =  None
        if dictionary.get("taskTimeouts") is not None:
            task_timeouts = list()
            for structure in dictionary.get('taskTimeouts'):
                task_timeouts.append(cohesity_management_sdk.models_v2.cancellation_timeout_params.CancellationTimeoutParams.from_dictionary(structure))

        # Return an object of this model
        return cls(allow_parallel_runs,
                   cobmr_backup,
                   continue_on_error,
                   objects,
                   indexing_policy,
                   perform_source_side_deduplication,
                   quiesce,
                   continue_on_quiesce_failure,
                   excluded_vss_writers,
                   global_exclude_fs,
                   perform_brick_based_deduplication,
                   pre_post_script,
                   dedup_exclusion_source_ids,
                   global_exclude_paths,
                   ignorable_errors,
                   task_timeouts)