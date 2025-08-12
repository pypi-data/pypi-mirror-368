# -*- coding: utf-8 -*-


class EnumerationOfAllTheHadoopAuthenticationTypes(object):

    """Implementation of the 'Enumeration of all the Hadoop Authentication types.' model.

    Enumeration of all the Hadoop Authentication types.

    Attributes:
        hadoop_auth_type (HadoopAuthTypeEnum): Enumeration of all the Hadoop
            Authentication types.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "hadoop_auth_type":'HadoopAuthType'
    }

    def __init__(self,
                 hadoop_auth_type=None):
        """Constructor for the EnumerationOfAllTheHadoopAuthenticationTypes class"""

        # Initialize members of the class
        self.hadoop_auth_type = hadoop_auth_type


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
        hadoop_auth_type = dictionary.get('HadoopAuthType')

        # Return an object of this model
        return cls(hadoop_auth_type)


