# -*- coding: utf-8 -*-


class CassandraSpecificPortInfo(object):

    """Implementation of the 'Cassandra specific port info.' model.

    Contains info about specific cassandra ports.

    Attributes:
        native_transport_port (int): Port for the CQL native transport.
        rpc_port (int): Remote Procedure Call (RPC) port for general mechanism
            for client-server applications.
        storage_port (int): TCP port for data. Internally used by Cassandra
            bulk loader.
        ssl_storage_port (int): SSL port for encrypted communication.
            Internally used by the Cassandra bulk loader.
        jmx_port (int): Cassandra management port.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "native_transport_port":'nativeTransportPort',
        "rpc_port":'rpcPort',
        "storage_port":'storagePort',
        "ssl_storage_port":'sslStoragePort',
        "jmx_port":'jmxPort'
    }

    def __init__(self,
                 native_transport_port=None,
                 rpc_port=None,
                 storage_port=None,
                 ssl_storage_port=None,
                 jmx_port=None):
        """Constructor for the CassandraSpecificPortInfo class"""

        # Initialize members of the class
        self.native_transport_port = native_transport_port
        self.rpc_port = rpc_port
        self.storage_port = storage_port
        self.ssl_storage_port = ssl_storage_port
        self.jmx_port = jmx_port


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
        native_transport_port = dictionary.get('nativeTransportPort')
        rpc_port = dictionary.get('rpcPort')
        storage_port = dictionary.get('storagePort')
        ssl_storage_port = dictionary.get('sslStoragePort')
        jmx_port = dictionary.get('jmxPort')

        # Return an object of this model
        return cls(native_transport_port,
                   rpc_port,
                   storage_port,
                   ssl_storage_port,
                   jmx_port)


