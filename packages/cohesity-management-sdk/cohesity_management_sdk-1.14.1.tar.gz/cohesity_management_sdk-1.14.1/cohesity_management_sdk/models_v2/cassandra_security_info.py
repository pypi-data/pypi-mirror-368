# -*- coding: utf-8 -*-


class CassandraSecurityInfo(object):

    """Implementation of the 'Cassandra security info.' model.

    Cassandra security related info.

    Attributes:
        cassandra_authorizer (string): Cassandra Authenticator/Authorizer.
        cassandra_auth_required (bool): Is Cassandra authentication required
            ?
        cassandra_auth_type (CassandraAuthType1Enum): Cassandra Authentication
            type.
        dse_authorization (bool): Is DSE Authorization enabled for this
            cluster ?
        client_encryption (bool): Is Client Encryption enabled for this
            cluster ?
        server_internode_encryption_type (string): 'Server internal node
            Encryption' type.
        server_encryption_req_client_auth (bool): Is 'Server encryption
            request client authentication' enabled for this cluster ?

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cassandra_authorizer":'cassandraAuthorizer',
        "cassandra_auth_required":'cassandraAuthRequired',
        "cassandra_auth_type":'cassandraAuthType',
        "dse_authorization":'dseAuthorization',
        "client_encryption":'clientEncryption',
        "server_internode_encryption_type":'serverInternodeEncryptionType',
        "server_encryption_req_client_auth":'serverEncryptionReqClientAuth'
    }

    def __init__(self,
                 cassandra_authorizer=None,
                 cassandra_auth_required=None,
                 cassandra_auth_type=None,
                 dse_authorization=None,
                 client_encryption=None,
                 server_internode_encryption_type=None,
                 server_encryption_req_client_auth=None):
        """Constructor for the CassandraSecurityInfo class"""

        # Initialize members of the class
        self.cassandra_authorizer = cassandra_authorizer
        self.cassandra_auth_required = cassandra_auth_required
        self.cassandra_auth_type = cassandra_auth_type
        self.dse_authorization = dse_authorization
        self.client_encryption = client_encryption
        self.server_internode_encryption_type = server_internode_encryption_type
        self.server_encryption_req_client_auth = server_encryption_req_client_auth


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
        cassandra_authorizer = dictionary.get('cassandraAuthorizer')
        cassandra_auth_required = dictionary.get('cassandraAuthRequired')
        cassandra_auth_type = dictionary.get('cassandraAuthType')
        dse_authorization = dictionary.get('dseAuthorization')
        client_encryption = dictionary.get('clientEncryption')
        server_internode_encryption_type = dictionary.get('serverInternodeEncryptionType')
        server_encryption_req_client_auth = dictionary.get('serverEncryptionReqClientAuth')

        # Return an object of this model
        return cls(cassandra_authorizer,
                   cassandra_auth_required,
                   cassandra_auth_type,
                   dse_authorization,
                   client_encryption,
                   server_internode_encryption_type,
                   server_encryption_req_client_auth)


