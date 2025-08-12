# -*- coding: utf-8 -*-


class AzureObjectProtectionAndRecoverySQLPackageOption(object):

    """Implementation of the 'AzureSqlPackageOptions' model.

    Specifies the SQL package parameters which are specific to Azure
      related Object Protection & Recovery.

    Attributes:
        compression (CompressionEnum): Specifies the compression option supported by SQL package export
          command during Azure SQL backup.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "compression":'compression'
    }

    def __init__(self,
                 compression=None):
        """Constructor for the AzureObjectProtection&RecoverySQLPackageOptions class"""

        # Initialize members of the class
        self.compression = compression


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
        compression = dictionary.get('compression')

        # Return an object of this model
        return cls(compression)