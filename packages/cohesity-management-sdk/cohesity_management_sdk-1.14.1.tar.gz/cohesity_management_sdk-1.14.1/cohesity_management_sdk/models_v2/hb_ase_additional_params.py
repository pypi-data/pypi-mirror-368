# -*- coding: utf-8 -*-


class HBAseAdditionalParams(object):

    """Implementation of the 'HBAse Additional Params.' model.

    Additional params for HBase protection source.

    Attributes:
        zookeeper_quorum (list of string): The 'Zookeeper Quorum' for this
            HBase.
        data_root_directory (string): The 'Data root directory' for this
            HBase.
        auth_type (AuthTypeEnum): Authentication type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "zookeeper_quorum":'zookeeperQuorum',
        "data_root_directory":'dataRootDirectory',
        "auth_type":'authType'
    }

    def __init__(self,
                 zookeeper_quorum=None,
                 data_root_directory=None,
                 auth_type=None):
        """Constructor for the HBAseAdditionalParams class"""

        # Initialize members of the class
        self.zookeeper_quorum = zookeeper_quorum
        self.data_root_directory = data_root_directory
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
        zookeeper_quorum = dictionary.get('zookeeperQuorum')
        data_root_directory = dictionary.get('dataRootDirectory')
        auth_type = dictionary.get('authType')

        # Return an object of this model
        return cls(zookeeper_quorum,
                   data_root_directory,
                   auth_type)


