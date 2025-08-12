# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.tenant_network


class Tenant(object):

    """Implementation of the 'Tenant' model.

    Specifies a tenant object.

    Attributes:
        created_at_time_msecs (long|int): Epoch time when tenant was created.
        deleted_at_time_msecs (long|int): Epoch time when tenant was last updated.
        description (string): Description about the tenant.
        id (string): Specifies the id of the tenant.
        is_managed_on_helios (bool): Flag to indicate if tenant is managed on helios
        last_updated_at_time_msecs (long|int): Epoch time when tenant was last updated.
        name (string): Specifies the name of the tenant.
        network (TenantNetwork): TODO: type description here
        status (status31Enum): Current Status of the Tenant.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "created_at_time_msecs":'createdAtTimeMsecs',
        "deleted_at_time_msecs":'deletedAtTimeMsecs',
        "description":'description',
        "id":'id',
        "is_managed_on_helios":'isManagedOnHelios',
        "last_updated_at_time_msecs":'lastUpdatedAtTimeMsecs',
        "name":'name',
        "network":'network',
        "status":'status'
    }

    def __init__(self,
                 created_at_time_msecs=None,
                 deleted_at_time_msecs=None,
                 description=None,
                 id=None,
                 is_managed_on_helios=None,
                 last_updated_at_time_msecs=None,
                 name=None,
                 network=None,
                 status=None):
        """Constructor for the Tenant class"""

        # Initialize members of the class
        self.created_at_time_msecs = created_at_time_msecs
        self.deleted_at_time_msecs = deleted_at_time_msecs
        self.description = description
        self.id = id
        self.is_managed_on_helios = is_managed_on_helios
        self.last_updated_at_time_msecs = last_updated_at_time_msecs
        self.name = name
        self.network = network
        self.status = status


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
        created_at_time_msecs = dictionary.get('createdAtTimeMsecs')
        deleted_at_time_msecs = dictionary.get('deletedAtTimeMsecs')
        description = dictionary.get('description')
        id = dictionary.get('id')
        is_managed_on_helios = dictionary.get('isManagedOnHelios')
        last_updated_at_time_msecs = dictionary.get('lastUpdatedAtTimeMsecs')
        name = dictionary.get('name')
        network = cohesity_management_sdk.models_v2.tenant_network.TenantNetwork.from_dictionary(dictionary.get('network')) if dictionary.get('network') else None
        status = dictionary.get('status')

        # Return an object of this model
        return cls(created_at_time_msecs,
                   deleted_at_time_msecs,
                   description,
                   id,
                   is_managed_on_helios,
                   last_updated_at_time_msecs,
                   name,
                   network,
                   status)