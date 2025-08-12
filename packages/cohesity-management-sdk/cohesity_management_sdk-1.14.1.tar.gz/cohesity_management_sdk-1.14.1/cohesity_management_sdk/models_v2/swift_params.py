# -*- coding: utf-8 -*-


class SwiftParams(object):

    """Implementation of the 'SwiftParams' model.

    Specifies the parameters to update a Swift configuration.

    Attributes:
        tenant_id (string): Specifies the tenant Id who will use this Swift
            configuration.
        keystone_id (long|int): Specifies the associated Keystone
            configuration Id.
        operator_roles (list of string): Specifies a list of roles that can
            operate on Cohesity Swift service.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "tenant_id":'tenantId',
        "keystone_id":'keystoneId',
        "operator_roles":'operatorRoles'
    }

    def __init__(self,
                 tenant_id=None,
                 keystone_id=None,
                 operator_roles=None):
        """Constructor for the SwiftParams class"""

        # Initialize members of the class
        self.tenant_id = tenant_id
        self.keystone_id = keystone_id
        self.operator_roles = operator_roles


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
        tenant_id = dictionary.get('tenantId')
        keystone_id = dictionary.get('keystoneId')
        operator_roles = dictionary.get('operatorRoles')

        # Return an object of this model
        return cls(tenant_id,
                   keystone_id,
                   operator_roles)


