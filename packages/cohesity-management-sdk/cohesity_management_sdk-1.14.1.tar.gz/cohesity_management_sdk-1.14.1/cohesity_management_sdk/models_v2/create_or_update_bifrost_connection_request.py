# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.connection_subnet

class CreateOrUpdateBifrostConnectionRequest(object):

    """Implementation of the 'Create Or Update Bifrost Connection Request.' model.

    Specify the params to create or update a connection of Bifrost.

    Attributes:
        tenant_id (string): Specifies the id of the tenant which the
            connection belongs to.
        name (string): Specifies the name of the connection.
        subnet (ConnectionSubnet): Specify the subnet used in connection.
        certificate_version (long|int): Specifies the version of the
            connection's certificate. The version is used to revoke/renew
            connection's certificates.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "tenant_id":'tenantId',
        "subnet":'subnet',
        "name":'name',
        "certificate_version":'certificateVersion'
    }

    def __init__(self,
                 tenant_id=None,
                 subnet=None,
                 name=None,
                 certificate_version=None):
        """Constructor for the CreateOrUpdateBifrostConnectionRequest class"""

        # Initialize members of the class
        self.tenant_id = tenant_id
        self.name = name
        self.subnet = subnet
        self.certificate_version = certificate_version


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
        subnet = cohesity_management_sdk.models_v2.connection_subnet.ConnectionSubnet.from_dictionary(dictionary.get('subnet')) if dictionary.get('subnet') else None
        name = dictionary.get('name')
        certificate_version = dictionary.get('certificateVersion')

        # Return an object of this model
        return cls(tenant_id,
                   subnet,
                   name,
                   certificate_version)


