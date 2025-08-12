# -*- coding: utf-8 -*-


class RegisterCouchbaseSourceRequestParameters(object):

    """Implementation of the 'Register Couchbase source request parameters.' model.

    Specifies parameters to register Couchbase source.

    Attributes:
        seeds (list of string): Specifies the IP Addresses or hostnames of the
            Couchbase cluster seed nodes.
        is_ssl_required (bool): Set to true if connection to couchbase has to
            be using SSL.
        http_port (int): HTTP direct or HTTP SSL port.
        carrier_port (int): Carrier direct or Carrier SSL port.
        username (string): Specifies the username to access target entity.
        password (string): Specifies the password to access target entity.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "seeds":'seeds',
        "is_ssl_required":'isSslRequired',
        "http_port":'httpPort',
        "carrier_port":'carrierPort',
        "username":'username',
        "password":'password'
    }

    def __init__(self,
                 seeds=None,
                 is_ssl_required=None,
                 http_port=None,
                 carrier_port=None,
                 username=None,
                 password=None):
        """Constructor for the RegisterCouchbaseSourceRequestParameters class"""

        # Initialize members of the class
        self.seeds = seeds
        self.is_ssl_required = is_ssl_required
        self.http_port = http_port
        self.carrier_port = carrier_port
        self.username = username
        self.password = password


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
        seeds = dictionary.get('seeds')
        is_ssl_required = dictionary.get('isSslRequired')
        http_port = dictionary.get('httpPort')
        carrier_port = dictionary.get('carrierPort')
        username = dictionary.get('username')
        password = dictionary.get('password')

        # Return an object of this model
        return cls(seeds,
                   is_ssl_required,
                   http_port,
                   carrier_port,
                   username,
                   password)


