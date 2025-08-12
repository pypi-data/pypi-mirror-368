# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.continuous_snapshot_params

class IsilonObjectProtectionParams(object):

    """Implementation of the 'IsilonObjectProtectionParams' model.

    Specifies the parameters which are specific to Isilon object protection.

    Attributes:
        protocol (Protocol4Enum): Specifies the protocol of the NAS device
            being backed up.
        continuous_snapshots (ContinuousSnapshotParams): Specifies the source
            snapshots to be taken even if there is a pending run in a
            protection group.
        use_changelist (bool): Specify whether to use the Isilon Changelist
            API to directly discover changed files/directories for faster
            incremental backup. Cohesity will keep an extra snapshot which
            will be deleted by the next successful backup.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protocol":'protocol',
        "continuous_snapshots":'continuousSnapshots',
        "use_changelist":'useChangelist'
    }

    def __init__(self,
                 protocol=None,
                 continuous_snapshots=None,
                 use_changelist=None):
        """Constructor for the IsilonObjectProtectionParams class"""

        # Initialize members of the class
        self.protocol = protocol
        self.continuous_snapshots = continuous_snapshots
        self.use_changelist = use_changelist


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
        protocol = dictionary.get('protocol')
        continuous_snapshots = cohesity_management_sdk.models_v2.continuous_snapshot_params.ContinuousSnapshotParams.from_dictionary(dictionary.get('continuousSnapshots')) if dictionary.get('continuousSnapshots') else None
        use_changelist = dictionary.get('useChangelist')

        # Return an object of this model
        return cls(protocol,
                   continuous_snapshots,
                   use_changelist)


