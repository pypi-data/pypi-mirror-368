# -*- coding: utf-8 -*-


class HdfsAdditionalParams(object):

    """Implementation of the 'Hdfs Additional Params.' model.

    Additional params for Hdfs protection source.

    Attributes:
        namenode_address (string): The HDFS Namenode IP or hostname.
        webhdfs_port (int): The HDFS WebHDFS port.
        auth_type (AuthTypeEnum): Authentication type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "namenode_address":'namenodeAddress',
        "webhdfs_port":'webhdfsPort',
        "auth_type":'authType'
    }

    def __init__(self,
                 namenode_address=None,
                 webhdfs_port=None,
                 auth_type=None):
        """Constructor for the HdfsAdditionalParams class"""

        # Initialize members of the class
        self.namenode_address = namenode_address
        self.webhdfs_port = webhdfs_port
        self.auth_type = auth_type


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
        namenode_address = dictionary.get('namenodeAddress')
        webhdfs_port = dictionary.get('webhdfsPort')
        auth_type = dictionary.get('authType')

        # Return an object of this model
        return cls(namenode_address,
                   webhdfs_port,
                   auth_type)


