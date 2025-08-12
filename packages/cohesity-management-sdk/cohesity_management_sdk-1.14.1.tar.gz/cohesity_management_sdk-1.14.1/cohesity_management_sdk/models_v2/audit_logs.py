# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.audit_log

class AuditLogs(object):

    """Implementation of the 'AuditLogs' model.

    Sepcifies the audit logs.

    Attributes:
        audit_logs (list of AuditLog): Specifies a list of audit logs.
        count (long|int): Specifies the total number of audit logs that match
            the filter and search criteria. Use this value to determine how
            many additional requests are required to get the full result.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "audit_logs":'auditLogs',
        "count":'count'
    }

    def __init__(self,
                 audit_logs=None,
                 count=None):
        """Constructor for the AuditLogs class"""

        # Initialize members of the class
        self.audit_logs = audit_logs
        self.count = count


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
        audit_logs = None
        if dictionary.get("auditLogs") is not None:
            audit_logs = list()
            for structure in dictionary.get('auditLogs'):
                audit_logs.append(cohesity_management_sdk.models_v2.audit_log.AuditLog.from_dictionary(structure))
        count = dictionary.get('count')

        # Return an object of this model
        return cls(audit_logs,
                   count)


