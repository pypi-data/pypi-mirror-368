# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.failover_replication

class Failover(object):

    """Implementation of the 'Failover' model.

    Specifies the details of a failover.

    Attributes:
        id (string): Specifies the failover id.
        mtype (Type24Enum): Specifies the failover type.
        status (Status22Enum): Specifies the failover status.
        error_message (string): Specifies the error details if failover status
            is 'Failed'.
        start_time_usecs (long|int): Specifies the failover start time in
            micro seconds.
        end_time_usecs (long|int): Specifies the failover complete time in
            micro seconds.
        replications (list of FailoverReplication): Specifies a list of
            replications in this failover.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "mtype":'type',
        "status":'status',
        "error_message":'errorMessage',
        "start_time_usecs":'startTimeUsecs',
        "end_time_usecs":'endTimeUsecs',
        "replications":'replications'
    }

    def __init__(self,
                 id=None,
                 mtype=None,
                 status=None,
                 error_message=None,
                 start_time_usecs=None,
                 end_time_usecs=None,
                 replications=None):
        """Constructor for the Failover class"""

        # Initialize members of the class
        self.id = id
        self.mtype = mtype
        self.status = status
        self.error_message = error_message
        self.start_time_usecs = start_time_usecs
        self.end_time_usecs = end_time_usecs
        self.replications = replications


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
        mtype = dictionary.get('type')
        status = dictionary.get('status')
        error_message = dictionary.get('errorMessage')
        start_time_usecs = dictionary.get('startTimeUsecs')
        end_time_usecs = dictionary.get('endTimeUsecs')
        replications = None
        if dictionary.get("replications") is not None:
            replications = list()
            for structure in dictionary.get('replications'):
                replications.append(cohesity_management_sdk.models_v2.failover_replication.FailoverReplication.from_dictionary(structure))

        # Return an object of this model
        return cls(id,
                   mtype,
                   status,
                   error_message,
                   start_time_usecs,
                   end_time_usecs,
                   replications)


