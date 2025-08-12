# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.vmware_object_protection_request
import cohesity_management_sdk.models_v2.disk_information
import cohesity_management_sdk.models_v2.indexing_policy
import cohesity_management_sdk.models_v2.pre_and_post_script_params

class VmwareObjectProtectionRequestParams(object):

    """Implementation of the 'VmwareObjectProtectionRequestParams' model.

    Specifies the parameters which are specific to VMware object protection.

    Attributes:
        objects (list of VmwareObjectProtectionRequest): Specifies the objects
            to include in the backup.
        global_exclude_disks (list of DiskInformation): Specifies a list of
            disks to exclude from the backup.
        app_consistent_snapshot (bool): Specifies whether or not to quiesce
            apps and the file system in order to take app consistent
            snapshots.
        fallback_to_crash_consistent_snapshot (bool): Specifies whether or not
            to fallback to a crash consistent snapshot in the event that an
            app consistent snapshot fails. This parameter defaults to true and
            only changes the behavior of the operation if
            'appConsistentSnapshot' is set to 'true'.
        skip_physical_rdm_disks (bool): Specifies whether or not to skip
            backing up physical RDM disks. Physical RDM disks cannot be backed
            up, so if you attempt to backup a VM with physical RDM disks and
            this value is set to 'false', then those VM backups will fail.
        indexing_policy (IndexingPolicy): Specifies settings for indexing
            files found in an Object (such as a VM) so these files can be
            searched and recovered. This also specifies inclusion and
            exclusion rules that determine the directories to index.
        pre_post_script (PreAndPostScriptParams): Specifies the params for pre
            and post scripts.
        leverage_san_transport (bool): If this field is set to true, then the
            backup for the objects will be performed using dedicated storage
            area network (SAN) instead of LAN or managment network.
        enable_nbdssl_fallback (bool): If this field is set to true and SAN
            transport backup fails, then backup will fallback to use NBDSSL
            transport. This field only applies if 'leverageSanTransport' is
            set to true.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "global_exclude_disks":'globalExcludeDisks',
        "app_consistent_snapshot":'appConsistentSnapshot',
        "fallback_to_crash_consistent_snapshot":'fallbackToCrashConsistentSnapshot',
        "skip_physical_rdm_disks":'skipPhysicalRDMDisks',
        "indexing_policy":'indexingPolicy',
        "pre_post_script":'prePostScript',
        "leverage_san_transport":'leverageSanTransport',
        "enable_nbdssl_fallback":'enableNBDSSLFallback'
    }

    def __init__(self,
                 objects=None,
                 global_exclude_disks=None,
                 app_consistent_snapshot=None,
                 fallback_to_crash_consistent_snapshot=None,
                 skip_physical_rdm_disks=None,
                 indexing_policy=None,
                 pre_post_script=None,
                 leverage_san_transport=None,
                 enable_nbdssl_fallback=None):
        """Constructor for the VmwareObjectProtectionRequestParams class"""

        # Initialize members of the class
        self.objects = objects
        self.global_exclude_disks = global_exclude_disks
        self.app_consistent_snapshot = app_consistent_snapshot
        self.fallback_to_crash_consistent_snapshot = fallback_to_crash_consistent_snapshot
        self.skip_physical_rdm_disks = skip_physical_rdm_disks
        self.indexing_policy = indexing_policy
        self.pre_post_script = pre_post_script
        self.leverage_san_transport = leverage_san_transport
        self.enable_nbdssl_fallback = enable_nbdssl_fallback


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
                objects.append(cohesity_management_sdk.models_v2.vmware_object_protection_request.VmwareObjectProtectionRequest.from_dictionary(structure))
        global_exclude_disks = None
        if dictionary.get("globalExcludeDisks") is not None:
            global_exclude_disks = list()
            for structure in dictionary.get('globalExcludeDisks'):
                global_exclude_disks.append(cohesity_management_sdk.models_v2.disk_information.DiskInformation.from_dictionary(structure))
        app_consistent_snapshot = dictionary.get('appConsistentSnapshot')
        fallback_to_crash_consistent_snapshot = dictionary.get('fallbackToCrashConsistentSnapshot')
        skip_physical_rdm_disks = dictionary.get('skipPhysicalRDMDisks')
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None
        pre_post_script = cohesity_management_sdk.models_v2.pre_and_post_script_params.PreAndPostScriptParams.from_dictionary(dictionary.get('prePostScript')) if dictionary.get('prePostScript') else None
        leverage_san_transport = dictionary.get('leverageSanTransport')
        enable_nbdssl_fallback = dictionary.get('enableNBDSSLFallback')

        # Return an object of this model
        return cls(objects,
                   global_exclude_disks,
                   app_consistent_snapshot,
                   fallback_to_crash_consistent_snapshot,
                   skip_physical_rdm_disks,
                   indexing_policy,
                   pre_post_script,
                   leverage_san_transport,
                   enable_nbdssl_fallback)


