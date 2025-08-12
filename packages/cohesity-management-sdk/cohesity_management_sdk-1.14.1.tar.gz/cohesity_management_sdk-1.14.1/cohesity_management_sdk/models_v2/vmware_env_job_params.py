# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.disk_information

class VmwareEnvJobParams(object):

    """Implementation of the 'VmwareEnvJobParams' model.

    Specifies job parameters applicable for all 'kVMware' Environment
      type Protection Sources in a Protection Job.

    Attributes:
        excluded_disks (DiskInformation): Specifies the alerting policy
        fallback_to_crash_consistent (bool): If true, takes a crash-consistent snapshot when app-consistent
          snapshot fails. Otherwise, the snapshot attempt is marked failed.
        indexing_policy (IndexingPolicy): Specifies settings for indexing files found in an Object so these
          files can be searched and recovered. This also specifies inclusion and exclusion
          rules that determine the directories to index.
        skip_physical_rdm_disks (bool): If true, skip physical RDM disks when backing up VMs. Otherwise,
          backup of VMs having physical RDM will fail.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "excluded_disks":'excludedDisks',
        "fallback_to_crash_consistent":'fallbackToCrashConsistent',
        "skip_physical_rdm_disks":'skipPhysicalRdmDisks'
    }

    def __init__(self,
                 excluded_disks=None,
                 fallback_to_crash_consistent=None,
                 skip_physical_rdm_disks=None):
        """Constructor for the VmwareEnvJobParams class"""

        # Initialize members of the class
        self.excluded_disks = excluded_disks
        self.fallback_to_crash_consistent = fallback_to_crash_consistent
        self.skip_physical_rdm_disks = skip_physical_rdm_disks


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
        excluded_disks = None
        if dictionary.get('excludedDisks') is not  None:
            excluded_disks = list()
            for structure in dictionary.get('excludedDisks'):
                excluded_disks.append(cohesity_management_sdk.models_v2.disk_information.DiskInformation.from_dictionary(structure))
        fallback_to_crash_consistent = dictionary.get('fallbackToCrashConsistent')
        skip_physical_rdm_disks = dictionary.get('skipPhysicalRdmDisks')

        # Return an object of this model
        return cls(excluded_disks,
                   fallback_to_crash_consistent,
                   skip_physical_rdm_disks)