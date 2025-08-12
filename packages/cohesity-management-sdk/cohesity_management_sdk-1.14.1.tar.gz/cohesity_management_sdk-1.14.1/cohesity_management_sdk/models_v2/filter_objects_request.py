# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.filter

class FilterObjectsRequest(object):

    """Implementation of the 'FilterObjectsRequest' model.

    Specifies the filter details.

    Attributes:
        filter_type (string): Specifies the type of filtering user wants to
            perform. Currently, we only support exclude type of filter.
        filters (list of Filter): Specifies the list of filters that need to
            be applied on given list of discovered objects.
        object_ids (list of long|int): Specifies a list of non leaf object ids
            to filter the leaf level objects. Non leaf object such host
            (physical or vm) or database instance can be specified.
        application_environment (ApplicationEnvironmentEnum): Specifies the
            type of application enviornment needed for filtering to be applied
            on. This is needed because in case of applications like SQL,
            Oracle, a single source can contain multiple application
            enviornments.
        tenant_ids (list of string): TenantIds contains list of the tenant for
            which objects are to be returned.
        include_tenants (bool): If true, the response will include objects
            which belongs to all tenants which the current user has permission
            to see. Default value is false.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "filter_type":'filterType',
        "filters":'filters',
        "object_ids":'objectIds',
        "application_environment":'applicationEnvironment',
        "tenant_ids":'tenantIds',
        "include_tenants":'includeTenants'
    }

    def __init__(self,
                 filter_type='exclude',
                 filters=None,
                 object_ids=None,
                 application_environment=None,
                 tenant_ids=None,
                 include_tenants=False):
        """Constructor for the FilterObjectsRequest class"""

        # Initialize members of the class
        self.filter_type = filter_type
        self.filters = filters
        self.object_ids = object_ids
        self.application_environment = application_environment
        self.tenant_ids = tenant_ids
        self.include_tenants = include_tenants


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
        filter_type = dictionary.get("filterType") if dictionary.get("filterType") else 'exclude'
        filters = None
        if dictionary.get("filters") is not None:
            filters = list()
            for structure in dictionary.get('filters'):
                filters.append(cohesity_management_sdk.models_v2.filter.Filter.from_dictionary(structure))
        object_ids = dictionary.get('objectIds')
        application_environment = dictionary.get('applicationEnvironment')
        tenant_ids = dictionary.get('tenantIds')
        include_tenants = dictionary.get("includeTenants") if dictionary.get("includeTenants") else False

        # Return an object of this model
        return cls(filter_type,
                   filters,
                   object_ids,
                   application_environment,
                   tenant_ids,
                   include_tenants)


