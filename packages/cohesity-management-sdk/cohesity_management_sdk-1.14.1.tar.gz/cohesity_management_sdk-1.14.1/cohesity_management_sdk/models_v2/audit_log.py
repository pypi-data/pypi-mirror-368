# -*- coding: utf-8 -*-


class AuditLog(object):

    """Implementation of the 'AuditLog' model.

    Specifies an audit log message.

    Attributes:
        details (string): Specifies the change details of this audit log.
        username (string): Specifies the username who made this audit log.
        domain (string): Specifies the domain of user who made this audit
            log.
        entity_name (string): Specifies the entity name.
        entity_type (string): Specifies the entity type.
        action (string): Specifies the action type of this audit log.
        timestamp_usecs (long|int): Specifies a unix timestamp in micro
            seconds when the audit log was taken.
        ip (string): Specifies the ip of user who made this audit log.
        is_impersonation (bool): Specifies if the action is made through
            impersonation.
        tenant_id (string): Specifies the tenant id who made this audit log.
        tenant_name (string): Specifies the tenant name who made this audit
            log.
        original_tenant_id (string): Specifies the original tenant id who made
            this audit log.
        original_tenant_name (string): Specifies the original tenant name who
            made this audit log.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "details":'details',
        "username":'username',
        "domain":'domain',
        "entity_name":'entityName',
        "entity_type":'entityType',
        "action":'action',
        "timestamp_usecs":'timestampUsecs',
        "ip":'ip',
        "is_impersonation":'isImpersonation',
        "tenant_id":'tenantId',
        "tenant_name":'tenantName',
        "original_tenant_id":'originalTenantId',
        "original_tenant_name":'originalTenantName'
    }

    def __init__(self,
                 details=None,
                 username=None,
                 domain=None,
                 entity_name=None,
                 entity_type=None,
                 action=None,
                 timestamp_usecs=None,
                 ip=None,
                 is_impersonation=None,
                 tenant_id=None,
                 tenant_name=None,
                 original_tenant_id=None,
                 original_tenant_name=None):
        """Constructor for the AuditLog class"""

        # Initialize members of the class
        self.details = details
        self.username = username
        self.domain = domain
        self.entity_name = entity_name
        self.entity_type = entity_type
        self.action = action
        self.timestamp_usecs = timestamp_usecs
        self.ip = ip
        self.is_impersonation = is_impersonation
        self.tenant_id = tenant_id
        self.tenant_name = tenant_name
        self.original_tenant_id = original_tenant_id
        self.original_tenant_name = original_tenant_name


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
        details = dictionary.get('details')
        username = dictionary.get('username')
        domain = dictionary.get('domain')
        entity_name = dictionary.get('entityName')
        entity_type = dictionary.get('entityType')
        action = dictionary.get('action')
        timestamp_usecs = dictionary.get('timestampUsecs')
        ip = dictionary.get('ip')
        is_impersonation = dictionary.get('isImpersonation')
        tenant_id = dictionary.get('tenantId')
        tenant_name = dictionary.get('tenantName')
        original_tenant_id = dictionary.get('originalTenantId')
        original_tenant_name = dictionary.get('originalTenantName')

        # Return an object of this model
        return cls(details,
                   username,
                   domain,
                   entity_name,
                   entity_type,
                   action,
                   timestamp_usecs,
                   ip,
                   is_impersonation,
                   tenant_id,
                   tenant_name,
                   original_tenant_id,
                   original_tenant_name)


