# -*- coding: utf-8 -*-


class AuthenticationDetailsForDSESolr(object):

    """Implementation of the 'Authentication details for DSE solr.' model.

    Contains details about DSE Solr.

    Attributes:
        solr_nodes (list of string): Solr node IP Addresses
        solr_port (int): Solr node Port.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "solr_nodes":'solrNodes',
        "solr_port":'solrPort'
    }

    def __init__(self,
                 solr_nodes=None,
                 solr_port=None):
        """Constructor for the AuthenticationDetailsForDSESolr class"""

        # Initialize members of the class
        self.solr_nodes = solr_nodes
        self.solr_port = solr_port


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
        solr_nodes = dictionary.get('solrNodes')
        solr_port = dictionary.get('solrPort')

        # Return an object of this model
        return cls(solr_nodes,
                   solr_port)


