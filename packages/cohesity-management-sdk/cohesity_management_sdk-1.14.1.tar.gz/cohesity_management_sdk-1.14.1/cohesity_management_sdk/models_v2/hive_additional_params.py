# -*- coding: utf-8 -*-


class HiveAdditionalParams(object):

    """Implementation of the 'Hive Additional Params.' model.

    Additional params for Hive protection source.

    Attributes:
        metastore_address (string): The MetastoreAddress for this Hive.
        metastore_port (int): The MetastorePort for this Hive.
        auth_type (AuthTypeEnum): Authentication type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "metastore_address":'metastoreAddress',
        "metastore_port":'metastorePort',
        "auth_type":'authType'
    }

    def __init__(self,
                 metastore_address=None,
                 metastore_port=None,
                 auth_type=None):
        """Constructor for the HiveAdditionalParams class"""

        # Initialize members of the class
        self.metastore_address = metastore_address
        self.metastore_port = metastore_port
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
        metastore_address = dictionary.get('metastoreAddress')
        metastore_port = dictionary.get('metastorePort')
        auth_type = dictionary.get('authType')

        # Return an object of this model
        return cls(metastore_address,
                   metastore_port,
                   auth_type)


