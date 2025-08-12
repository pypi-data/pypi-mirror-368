# -*- coding: utf-8 -*-

class MongoDBCdpJobInfo(object):

    """Implementation of the 'MongoDBCdpJobInfo' model.

    Specifies the CDP related information for a given MongoDB protection
      group. This will only be populated when the protection group is configured with
      a CDP policy.

    Attributes:
        latest_recovery_point_in_time_usecs (long|int): Specifies the latest available recovery point timestamp (in microseconds
          from epoch)
    """

    # Create a mapping from Model property names to API property names
    _names = {
       "latest_recovery_point_in_time_usecs":'latestRecoveryPointInTimeUsecs'
    }

    def __init__(self,
                 latest_recovery_point_in_time_usecs=None):
        """Constructor for the MongoDBCdpJobInfo class"""

        # Initialize members of the class
        self.latest_recovery_point_in_time_usecs = latest_recovery_point_in_time_usecs


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
        latest_recovery_point_in_time_usecs = dictionary.get('latestRecoveryPointInTimeUsecs')

        # Return an object of this model
        return cls(latest_recovery_point_in_time_usecs)