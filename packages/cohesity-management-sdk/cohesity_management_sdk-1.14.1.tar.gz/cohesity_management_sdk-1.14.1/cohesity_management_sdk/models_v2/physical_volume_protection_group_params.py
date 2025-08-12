# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.physical_volume_protection_group_object_params
import cohesity_management_sdk.models_v2.indexing_policy
import cohesity_management_sdk.models_v2.pre_and_post_script_params

class PhysicalVolumeProtectionGroupParams(object):

    """Implementation of the 'PhysicalVolumeProtectionGroupParams' model.

    Specifies the parameters which are specific to Volume based physical
    Protection Groups.

    Attributes:
        cobmr_backup (bool): Specifies whether to take a CoBMR backup.
        excluded_vss_writers (string): Specifies writer names which should be excluded from physical
          volume based backups.
        objects (list of PhysicalVolumeProtectionGroupObjectParams): TODO:
            type description here.
        indexing_policy (IndexingPolicy): Specifies settings for indexing
            files found in an Object (such as a VM) so these files can be
            searched and recovered. This also specifies inclusion and
            exclusion rules that determine the directories to index.
        perform_source_side_deduplication (bool): Specifies whether or not to
            perform source side deduplication on this Protection Group.
        quiesce (bool): Specifies Whether to take app-consistent snapshots by
            quiescing apps and the filesystem before taking a backup
        continue_on_quiesce_failure (bool): Specifies whether to continue
            backing up on quiesce failure
        incremental_backup_after_restart (bool): Specifies whether or not to
            perform an incremental backup after the server restarts. This is
            applicable to windows environments.
        pre_post_script (PreAndPostScriptParams): Specifies the params for pre
            and post scripts.
        dedup_exclusion_source_ids (list of long|int): Specifies ids of
            sources for which deduplication has to be disabled.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cobmr_backup":'cobmrBackup',
        "excluded_vss_writers":'excludedVssWriters',
        "objects":'objects',
        "indexing_policy":'indexingPolicy',
        "perform_source_side_deduplication":'performSourceSideDeduplication',
        "quiesce":'quiesce',
        "continue_on_quiesce_failure":'continueOnQuiesceFailure',
        "incremental_backup_after_restart":'incrementalBackupAfterRestart',
        "pre_post_script":'prePostScript',
        "dedup_exclusion_source_ids":'dedupExclusionSourceIds'
    }

    def __init__(self,
                 cobmr_backup=None,
                 excluded_vss_writers=None,
                 objects=None,
                 indexing_policy=None,
                 perform_source_side_deduplication=None,
                 quiesce=None,
                 continue_on_quiesce_failure=None,
                 incremental_backup_after_restart=None,
                 pre_post_script=None,
                 dedup_exclusion_source_ids=None):
        """Constructor for the PhysicalVolumeProtectionGroupParams class"""

        # Initialize members of the class
        self.cobmr_backup = cobmr_backup
        self.excluded_vss_writers = excluded_vss_writers
        self.objects = objects
        self.indexing_policy = indexing_policy
        self.perform_source_side_deduplication = perform_source_side_deduplication
        self.quiesce = quiesce
        self.continue_on_quiesce_failure = continue_on_quiesce_failure
        self.incremental_backup_after_restart = incremental_backup_after_restart
        self.pre_post_script = pre_post_script
        self.dedup_exclusion_source_ids = dedup_exclusion_source_ids


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
        cobmr_backup = dictionary.get('cobmrBackup')
        excluded_vss_writers = dictionary.get('excludedVssWriters')
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.physical_volume_protection_group_object_params.PhysicalVolumeProtectionGroupObjectParams.from_dictionary(structure))
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None
        perform_source_side_deduplication = dictionary.get('performSourceSideDeduplication')
        quiesce = dictionary.get('quiesce')
        continue_on_quiesce_failure = dictionary.get('continueOnQuiesceFailure')
        incremental_backup_after_restart = dictionary.get('incrementalBackupAfterRestart')
        pre_post_script = cohesity_management_sdk.models_v2.pre_and_post_script_params.PreAndPostScriptParams.from_dictionary(dictionary.get('prePostScript')) if dictionary.get('prePostScript') else None
        dedup_exclusion_source_ids = dictionary.get('dedupExclusionSourceIds')

        # Return an object of this model
        return cls(cobmr_backup,
                   excluded_vss_writers,
                   objects,
                   indexing_policy,
                   perform_source_side_deduplication,
                   quiesce,
                   continue_on_quiesce_failure,
                   incremental_backup_after_restart,
                   pre_post_script,
                   dedup_exclusion_source_ids)