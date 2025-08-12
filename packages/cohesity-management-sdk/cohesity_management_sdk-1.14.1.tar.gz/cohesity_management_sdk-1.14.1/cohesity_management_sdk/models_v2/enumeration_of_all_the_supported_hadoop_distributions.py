# -*- coding: utf-8 -*-


class EnumerationOfAllTheSupportedHadoopDistributions(object):

    """Implementation of the 'Enumeration of all the supported Hadoop distributions.' model.

    Enumeration of all the supported Hadoop distributions.

    Attributes:
        supported_hadoop_distributions (SupportedHadoopDistributionsEnum):
            Enumeration of all the supported Hadoop distributions.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "supported_hadoop_distributions":'SupportedHadoopDistributions'
    }

    def __init__(self,
                 supported_hadoop_distributions=None):
        """Constructor for the EnumerationOfAllTheSupportedHadoopDistributions class"""

        # Initialize members of the class
        self.supported_hadoop_distributions = supported_hadoop_distributions


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
        supported_hadoop_distributions = dictionary.get('SupportedHadoopDistributions')

        # Return an object of this model
        return cls(supported_hadoop_distributions)


