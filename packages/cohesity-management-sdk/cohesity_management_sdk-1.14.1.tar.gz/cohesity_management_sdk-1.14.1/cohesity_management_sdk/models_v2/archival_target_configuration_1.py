# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.retention

class ArchivalTargetConfiguration1(object):

    """Implementation of the 'Archival Target Configuration1' model.

    Specifies settings for copying Snapshots External Targets (such as AWS or
    Tape). This also specifies the retention policy that should be applied to
    Snapshots after they have been copied to the specified target.

    Attributes:
        copy_only_fully_successful (bool): Specifies if Snapshots are copied from a fully successful Protection
          Group Run or a partially successful Protection Group Run. If false, Snapshots
          are copied the Protection Group Run, even if the Run was not fully successful
          i.e. Snapshots were not captured for all Objects in the Protection Group.
          If true, Snapshots are copied only when the run is fully successful.
        id (long|int): Specifies the Archival target to copy the Snapshots
            to.
        on_legal_hold (bool): Specifies if the Run is on legal hold.
        archival_target_type (ArchivalTargetTypeEnum): Specifies the
            snapshot's archival target type from which recovery has been
            performed.
        retention (Retention): Specifies the retention of a backup.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "copy_only_fully_successful":'copyOnlyFullySuccessful',
        "id":'id',
        "on_legal_hold":'onLegalHold',
        "archival_target_type":'archivalTargetType',
        "retention":'retention'
    }

    def __init__(self,
                 copy_only_fully_successful=None,
                 id=None,
                 on_legal_hold=None,
                 archival_target_type=None,
                 retention=None):
        """Constructor for the ArchivalTargetConfiguration1 class"""

        # Initialize members of the class
        self.copy_only_fully_successful = copy_only_fully_successful
        self.id = id
        self.on_legal_hold = on_legal_hold
        self.archival_target_type = archival_target_type
        self.retention = retention


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
        copy_only_fully_successful = dictionary.get('copyOnlyFullySuccessful')
        id = dictionary.get('id')
        on_legal_hold = dictionary.get('onLegalHold')
        archival_target_type = dictionary.get('archivalTargetType')
        retention = cohesity_management_sdk.models_v2.retention.Retention.from_dictionary(dictionary.get('retention')) if dictionary.get('retention') else None

        # Return an object of this model
        return cls(copy_only_fully_successful,
                   id,
                   on_legal_hold,
                   archival_target_type,
                   retention)