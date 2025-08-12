# -*- coding: utf-8 -*-


class UpdateObjectSnapshotRequest(object):

    """Implementation of the 'Update Object Snapshot Request.' model.

    Specifies the parameters to update an object snapshot.

    Attributes:
        set_legal_hold (bool): Whether to set the snapshot on legal hold. If
            set to true, the run cannot be deleted during the retention
            period.
        data_lock_type (DataLockTypeEnum): Specifies the snapshot data lock
            type.
        expiry_time_secs (int): Specifies the expiry time of the snapshot in
            Unix timestamp epoch in seconds.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "set_legal_hold":'setLegalHold',
        "data_lock_type":'dataLockType',
        "expiry_time_secs":'expiryTimeSecs'
    }

    def __init__(self,
                 set_legal_hold=None,
                 data_lock_type=None,
                 expiry_time_secs=None):
        """Constructor for the UpdateObjectSnapshotRequest class"""

        # Initialize members of the class
        self.set_legal_hold = set_legal_hold
        self.data_lock_type = data_lock_type
        self.expiry_time_secs = expiry_time_secs


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
        set_legal_hold = dictionary.get('setLegalHold')
        data_lock_type = dictionary.get('dataLockType')
        expiry_time_secs = dictionary.get('expiryTimeSecs')

        # Return an object of this model
        return cls(set_legal_hold,
                   data_lock_type,
                   expiry_time_secs)


