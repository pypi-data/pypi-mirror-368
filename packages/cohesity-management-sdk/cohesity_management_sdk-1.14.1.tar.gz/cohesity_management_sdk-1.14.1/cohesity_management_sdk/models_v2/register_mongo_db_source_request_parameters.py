# -*- coding: utf-8 -*-


class RegisterMongoDBSourceRequestParameters(object):

    """Implementation of the 'Register MongoDB source request parameters.' model.

    Specifies parameters to register MongoDB source.

    Attributes:
        hosts (list of string): Specify the MongoS hosts for a sharded cluster
            and the MongoD hosts for a non-sharded cluster. You can specify a
            sub-set of the hosts.
        auth_type (AuthType3Enum): MongoDB authentication type.
        username (string): Specifies the username of the MongoDB cluster.
            Should be set if 'authType' is 'LDAP' or 'SCRAM'.
        password (string): Specifies the password for the MongoDB cluster.
            Should be set if 'authType' is 'LDAP' or 'SCRAM'.
        authenticating_database (string): Authenticating Database for this
            cluster. Should be set if 'authType' is 'LDAP' or 'SCRAM'.
        is_ssl_required (bool): Set to true if connection to MongoDB has to be
            over SSL.
        use_secondary_for_backup (bool): Set this to true if you want the
            system to peform backups from secondary nodes.
        secondary_node_tag (string): MongoDB Secondary node tag. Required only
            if 'useSecondaryForBackup' is true.The system will use this to
            identify the secondary nodes for reading backup data.
        principal (string): Specifies the principal name of the MongoDB cluster. Should be
          set if 'authType' is 'KERBEROS'.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "hosts":'hosts',
        "auth_type":'authType',
        "is_ssl_required":'isSslRequired',
        "use_secondary_for_backup":'useSecondaryForBackup',
        "username":'username',
        "password":'password',
        "authenticating_database":'authenticatingDatabase',
        "secondary_node_tag":'secondaryNodeTag',
        "principal":'principal'
    }

    def __init__(self,
                 hosts=None,
                 auth_type=None,
                 is_ssl_required=None,
                 use_secondary_for_backup=None,
                 username=None,
                 password=None,
                 authenticating_database=None,
                 secondary_node_tag=None,
                 principal=None):
        """Constructor for the RegisterMongoDBSourceRequestParameters class"""

        # Initialize members of the class
        self.hosts = hosts
        self.auth_type = auth_type
        self.username = username
        self.password = password
        self.authenticating_database = authenticating_database
        self.is_ssl_required = is_ssl_required
        self.use_secondary_for_backup = use_secondary_for_backup
        self.secondary_node_tag = secondary_node_tag
        self.principal = principal


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
        hosts = dictionary.get('hosts')
        auth_type = dictionary.get('authType')
        is_ssl_required = dictionary.get('isSslRequired')
        use_secondary_for_backup = dictionary.get('useSecondaryForBackup')
        username = dictionary.get('username')
        password = dictionary.get('password')
        authenticating_database = dictionary.get('authenticatingDatabase')
        secondary_node_tag = dictionary.get('secondaryNodeTag')
        principal = dictionary.get('principal')

        # Return an object of this model
        return cls(hosts,
                   auth_type,
                   is_ssl_required,
                   use_secondary_for_backup,
                   username,
                   password,
                   authenticating_database,
                   secondary_node_tag,
                   principal)