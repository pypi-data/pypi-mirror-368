# -*- coding: utf-8 -*-


class DataLockConstraints(object):

    """Implementation of the 'DataLock Constraints' model.

    Specifies the dataLock constraints for local or target snapshot.

    Attributes:
        mode (Mode2Enum): Specifies the type of WORM retention type. 
            'Compliance' implies WORM retention is set for compliance reason. 
            'Administrative' implies WORM retention is set for administrative
            purposes.
        expiry_time_usecs (long|int): Specifies the expiry time of attempt in
            Unix epoch Timestamp (in microseconds).

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mode":'mode',
        "expiry_time_usecs":'expiryTimeUsecs'
    }

    def __init__(self,
                 mode=None,
                 expiry_time_usecs=None):
        """Constructor for the DataLockConstraints class"""

        # Initialize members of the class
        self.mode = mode
        self.expiry_time_usecs = expiry_time_usecs


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
        mode = dictionary.get('mode')
        expiry_time_usecs = dictionary.get('expiryTimeUsecs')

        # Return an object of this model
        return cls(mode,
                   expiry_time_usecs)


