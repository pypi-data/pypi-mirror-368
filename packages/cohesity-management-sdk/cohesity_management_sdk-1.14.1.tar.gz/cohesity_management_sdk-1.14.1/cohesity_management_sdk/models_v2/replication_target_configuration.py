# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.retention

class ReplicationTargetConfiguration(object):

    """Implementation of the 'Replication Target Configuration' model.

    Specifies settings for copying Snapshots to Remote Clusters. This also
    specifies the retention policy that should be applied to Snapshots after
    they have been copied to the specified target.

    Attributes:
        id (long|int): Specifies id of Remote Cluster to copy the Snapshots
            to.
        on_legal_hold (bool): Specifies if the Run is on legal hold.
        retention (Retention): Specifies the retention of a backup.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "on_legal_hold":'onLegalHold',
        "retention":'retention'
    }

    def __init__(self,
                 id=None,
                 on_legal_hold=None,
                 retention=None):
        """Constructor for the ReplicationTargetConfiguration class"""

        # Initialize members of the class
        self.id = id
        self.on_legal_hold = on_legal_hold
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
        id = dictionary.get('id')
        on_legal_hold = dictionary.get('onLegalHold')
        retention = cohesity_management_sdk.models_v2.retention.Retention.from_dictionary(dictionary.get('retention')) if dictionary.get('retention') else None

        # Return an object of this model
        return cls(id,
                   on_legal_hold,
                   retention)