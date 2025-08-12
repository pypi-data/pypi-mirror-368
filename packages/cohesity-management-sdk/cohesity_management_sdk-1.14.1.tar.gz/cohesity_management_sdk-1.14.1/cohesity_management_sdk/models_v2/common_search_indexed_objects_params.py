# -*- coding: utf-8 -*-


class CommonSearchIndexedObjectsParams(object):

    """Implementation of the 'Common Search Indexed Objects Params' model.

    Specifies the common params to search for indexed objects.

    Attributes:
        protection_group_ids (list of string): Specifies a list of Protection
            Group ids to filter the indexed objects. If specified, the objects
            indexed by specified Protection Group ids will be returned.
        storage_domain_ids (list of long|int): Specifies the Storage Domain
            ids to filter indexed objects for which Protection Groups are
            writing data to Cohesity Views on the specified Storage Domains.
        tenant_id (string): TenantId contains id of the tenant for which
            objects are to be returned.
        include_tenants (bool): If true, the response will include objects
            which belongs to all tenants which the current user has permission
            to see. Default value is false.
        tags (list of string): Specifies a list of tags. Only files containing
            specified tags will be returned.
        snapshot_tags (list of string): Specifies a list of snapshot tags.
            Only files containing specified snapshot tags will be returned.
        pagination_cookie (string): Specifies the pagination cookie with which
            subsequent parts of the response can be fetched.
        count (int): Specifies the number of indexed obejcts to be fetched for
            the specified pagination cookie.
        object_type (ObjectType1Enum): Specifies the object type to be
            searched for.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object_type":'objectType',
        "protection_group_ids":'protectionGroupIds',
        "storage_domain_ids":'storageDomainIds',
        "tenant_id":'tenantId',
        "include_tenants":'includeTenants',
        "tags":'tags',
        "snapshot_tags":'snapshotTags',
        "pagination_cookie":'paginationCookie',
        "count":'count'
    }

    def __init__(self,
                 object_type=None,
                 protection_group_ids=None,
                 storage_domain_ids=None,
                 tenant_id=None,
                 include_tenants=False,
                 tags=None,
                 snapshot_tags=None,
                 pagination_cookie=None,
                 count=None):
        """Constructor for the CommonSearchIndexedObjectsParams class"""

        # Initialize members of the class
        self.protection_group_ids = protection_group_ids
        self.storage_domain_ids = storage_domain_ids
        self.tenant_id = tenant_id
        self.include_tenants = include_tenants
        self.tags = tags
        self.snapshot_tags = snapshot_tags
        self.pagination_cookie = pagination_cookie
        self.count = count
        self.object_type = object_type


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
        object_type = dictionary.get('objectType')
        protection_group_ids = dictionary.get('protectionGroupIds')
        storage_domain_ids = dictionary.get('storageDomainIds')
        tenant_id = dictionary.get('tenantId')
        include_tenants = dictionary.get("includeTenants") if dictionary.get("includeTenants") else False
        tags = dictionary.get('tags')
        snapshot_tags = dictionary.get('snapshotTags')
        pagination_cookie = dictionary.get('paginationCookie')
        count = dictionary.get('count')

        # Return an object of this model
        return cls(object_type,
                   protection_group_ids,
                   storage_domain_ids,
                   tenant_id,
                   include_tenants,
                   tags,
                   snapshot_tags,
                   pagination_cookie,
                   count)


