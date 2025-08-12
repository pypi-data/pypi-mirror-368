# -*- coding: utf-8 -*-


class PublicTaskStatus(object):

    """Implementation of the 'PublicTaskStatus' model.

    Public Task Status

    Attributes:
        public_task_status (PublicTaskStatus1Enum): Specifies the public task
            status.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "public_task_status":'publicTaskStatus'
    }

    def __init__(self,
                 public_task_status=None):
        """Constructor for the PublicTaskStatus class"""

        # Initialize members of the class
        self.public_task_status = public_task_status


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
        public_task_status = dictionary.get('publicTaskStatus')

        # Return an object of this model
        return cls(public_task_status)


