# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class OracleRangeMetaInfo(object):
    """Implementation of the 'OracleRangeMetaInfo' model.

    Specifies Range related information for an oracle db

    Attributes:
        end_of_range (long|int): Specifies ending value of the range in time (usecs), SCN or sequence no.
        incarnation_id (long|int): Specifies incarnation id associated with the oracle db for which the restore range belongs. Only applicable for ranges of type SCN and sequence no.
        protection_group_id (string): Specifies id of the Protection Group corresponding to this oracle range
        reset_log_id (long|int): Specifies resetlogs identifier associated with the oracle range. Only applicable for ranges of type SCN and sequence no.
        start_of_range (long|int): Specifies starting value of the range in time (usecs), SCN or sequence no.
        thread_id (long|int): Specifies thread id associated with the oracle db for which the restore range belongs. Only applicable for ranges of type sequence no.
    """

    _names = {
        "end_of_range":"endOfRange",
        "incarnation_id":"incarnationId",
        "protection_group_id":"protectionGroupId",
        "reset_log_id":"resetLogId",
        "start_of_range":"startOfRange",
        "thread_id":"threadId",
    }

    def __init__(self,
                 end_of_range=None,
                 incarnation_id=None,
                 protection_group_id=None,
                 reset_log_id=None,
                 start_of_range=None,
                 thread_id=None):
        """Constructor for the OracleRangeMetaInfo class"""

        self.end_of_range = end_of_range
        self.incarnation_id = incarnation_id
        self.protection_group_id = protection_group_id
        self.reset_log_id = reset_log_id
        self.start_of_range = start_of_range
        self.thread_id = thread_id


    @classmethod
    def from_dictionary(cls, dictionary):
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

        end_of_range = dictionary.get('endOfRange')
        incarnation_id = dictionary.get('incarnationId')
        protection_group_id = dictionary.get('protectionGroupId')
        reset_log_id = dictionary.get('resetLogId')
        start_of_range = dictionary.get('startOfRange')
        thread_id = dictionary.get('threadId')

        return cls(
            end_of_range,
            incarnation_id,
            protection_group_id,
            reset_log_id,
            start_of_range,
            thread_id
        )