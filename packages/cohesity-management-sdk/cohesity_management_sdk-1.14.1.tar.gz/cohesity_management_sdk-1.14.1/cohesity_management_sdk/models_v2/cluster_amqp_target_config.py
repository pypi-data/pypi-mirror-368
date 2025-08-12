# -*- coding: utf-8 -*-


class ClusterAMQPTargetConfig(object):

    """Implementation of the 'ClusterAMQPTargetConfig' model.

    Specifies the AMQP target config.

    Attributes:
        server_ip (string): Specifies the server ip.
        username (string): Specifies the username.
        password (string): Specifies the password.
        virtual_host (string): Specifies the virtual host.
        exchange (string): Specifies the exchange.
        filer_id (long|int): Specifies the filer id.
        certificate (string): Specifies the certificate.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "server_ip":'serverIp',
        "username":'username',
        "password":'password',
        "virtual_host":'virtualHost',
        "exchange":'exchange',
        "filer_id":'filerId',
        "certificate":'certificate'
    }

    def __init__(self,
                 server_ip=None,
                 username=None,
                 password=None,
                 virtual_host=None,
                 exchange=None,
                 filer_id=None,
                 certificate=None):
        """Constructor for the ClusterAMQPTargetConfig class"""

        # Initialize members of the class
        self.server_ip = server_ip
        self.username = username
        self.password = password
        self.virtual_host = virtual_host
        self.exchange = exchange
        self.filer_id = filer_id
        self.certificate = certificate


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
        server_ip = dictionary.get('serverIp')
        username = dictionary.get('username')
        password = dictionary.get('password')
        virtual_host = dictionary.get('virtualHost')
        exchange = dictionary.get('exchange')
        filer_id = dictionary.get('filerId')
        certificate = dictionary.get('certificate')

        # Return an object of this model
        return cls(server_ip,
                   username,
                   password,
                   virtual_host,
                   exchange,
                   filer_id,
                   certificate)


