# -*- coding: utf-8 -*-


class CloudSpinDataStatistics(object):

    """Implementation of the 'Cloud Spin data statistics.' model.

    Specifies statistics about Cloud Spin data.

    Attributes:
        physical_bytes_transferred (long|int): Specifies the physical bytes
            transferred.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "physical_bytes_transferred":'physicalBytesTransferred'
    }

    def __init__(self,
                 physical_bytes_transferred=None):
        """Constructor for the CloudSpinDataStatistics class"""

        # Initialize members of the class
        self.physical_bytes_transferred = physical_bytes_transferred


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
        physical_bytes_transferred = dictionary.get('physicalBytesTransferred')

        # Return an object of this model
        return cls(physical_bytes_transferred)


