# -*- coding: utf-8 -*-


class SyslogAuditTag(object):

    """Implementation of the 'SyslogAuditTag' model.

    Cohesity audit tag name.

    Attributes:
        cluster_audit (string): Cluster audit tagging name.
        filer_audit (string): Filer audit tagging name.
        data_protection_events_audit (string): Data protection events audit
            tagging name.
        alert_audit (string): Alert audit tagging name.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cluster_audit":'clusterAudit',
        "filer_audit":'filerAudit',
        "data_protection_events_audit":'dataProtectionEventsAudit',
        "alert_audit":'alertAudit'
    }

    def __init__(self,
                 cluster_audit=None,
                 filer_audit=None,
                 data_protection_events_audit=None,
                 alert_audit=None):
        """Constructor for the SyslogAuditTag class"""

        # Initialize members of the class
        self.cluster_audit = cluster_audit
        self.filer_audit = filer_audit
        self.data_protection_events_audit = data_protection_events_audit
        self.alert_audit = alert_audit


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
        cluster_audit = dictionary.get('clusterAudit')
        filer_audit = dictionary.get('filerAudit')
        data_protection_events_audit = dictionary.get('dataProtectionEventsAudit')
        alert_audit = dictionary.get('alertAudit')

        # Return an object of this model
        return cls(cluster_audit,
                   filer_audit,
                   data_protection_events_audit,
                   alert_audit)


