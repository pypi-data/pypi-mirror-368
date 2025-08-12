# -*- coding: utf-8 -*-


class DiskStatus2(object):

    """Implementation of the 'Disk status.2' model.

    Status of local disk.

    Attributes:
        status (Status26Enum): Specifies status of the local disk.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "status":'status'
    }

    def __init__(self,
                 status=None):
        """Constructor for the DiskStatus2 class"""

        # Initialize members of the class
        self.status = status


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
        status = dictionary.get('status')

        # Return an object of this model
        return cls(status)


