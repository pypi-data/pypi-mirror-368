# -*- coding: utf-8 -*-


class DiskTiers(object):

    """Implementation of the 'Disk Tiers' model.

    Disk Tiers

    Attributes:
        disk_tiers (DiskTiers1Enum): Disk Tiers

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "disk_tiers":'diskTiers'
    }

    def __init__(self,
                 disk_tiers=None):
        """Constructor for the DiskTiers class"""

        # Initialize members of the class
        self.disk_tiers = disk_tiers


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
        disk_tiers = dictionary.get('diskTiers')

        # Return an object of this model
        return cls(disk_tiers)


