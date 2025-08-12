# -*- coding: utf-8 -*-


class EnumerationOfAllTheMongoDBAuthenticationTypes(object):

    """Implementation of the 'Enumeration of all the MongoDB Authentication types.' model.

    Enumeration of all the MongoDB Authentication types.

    Attributes:
        mongo_db_auth_type (MongoDBAuthTypeEnum): Enumeration of all the
            MongoDB Authentication.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mongo_db_auth_type":'MongoDBAuthType'
    }

    def __init__(self,
                 mongo_db_auth_type=None):
        """Constructor for the EnumerationOfAllTheMongoDBAuthenticationTypes class"""

        # Initialize members of the class
        self.mongo_db_auth_type = mongo_db_auth_type


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
        mongo_db_auth_type = dictionary.get('MongoDBAuthType')

        # Return an object of this model
        return cls(mongo_db_auth_type)


