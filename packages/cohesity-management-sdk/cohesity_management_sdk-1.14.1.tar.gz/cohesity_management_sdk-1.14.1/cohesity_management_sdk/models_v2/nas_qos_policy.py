# -*- coding: utf-8 -*-


class NasQosPolicy(object):

    """Implementation of the 'NasQosPolicy' model.

    Specifies the QoS policy, which defines the principal and priority of a
    NAS recovery.

    Attributes:
        id (long|int): Specifies the ID of the QoS Policy.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id'
    }

    def __init__(self,
                 id=None):
        """Constructor for the NasQosPolicy class"""

        # Initialize members of the class
        self.id = id


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
        id = dictionary.get('id')

        # Return an object of this model
        return cls(id)


