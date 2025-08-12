# -*- coding: utf-8 -*-


class FailoverObjects(object):

    """Implementation of the 'Failover Objects' model.

    Specifies the details about the objects being failed over.

    Attributes:
        object_id (long|int): Specifies the object Id involved in failover
            operation.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object_id":'objectId'
    }

    def __init__(self,
                 object_id=None):
        """Constructor for the FailoverObjects class"""

        # Initialize members of the class
        self.object_id = object_id


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
        object_id = dictionary.get('objectId')

        # Return an object of this model
        return cls(object_id)


