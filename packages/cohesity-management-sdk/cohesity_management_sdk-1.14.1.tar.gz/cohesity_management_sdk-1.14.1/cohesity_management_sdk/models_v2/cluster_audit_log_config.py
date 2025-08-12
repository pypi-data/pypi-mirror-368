# -*- coding: utf-8 -*-


class ClusterAuditLogConfig(object):

    """Implementation of the 'ClusterAuditLogConfig' model.

    Specifies the Cluster audit log configuration.

    Attributes:
        enabled (bool): Specifies if audit log is enabled.
        retention_period_days (long|int): Specifies the audit log retention period in days. Audit logs
          generated before the period of time specified by retentionPeriodDays are
          removed from the Cohesity Cluster.
        verbose_audit (bool): Specifies the Cluster audit log configuration.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "enabled":'enabled',
        "retention_period_days":'retentionPeriodDays',
        "verbose_audit":'verboseAudit'
    }

    def __init__(self,
                 enabled=None,
                 retention_period_days=None,
                 verbose_audit=None):
        """Constructor for the ClusterAuditLogConfig class"""

        # Initialize members of the class
        self.enabled = enabled
        self.retention_period_days = retention_period_days
        self.verbose_audit = verbose_audit


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
        enabled = dictionary.get('enabled')
        retention_period_days = dictionary.get('retentionPeriodDays')
        verbose_audit = dictionary.get('verboseAudit')

        # Return an object of this model
        return cls(enabled,
                   retention_period_days,
                   verbose_audit)