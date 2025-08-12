# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.disk_details

class ListOfDisks(object):

    """Implementation of the 'List of Disks' model.

    Specifies the list of disks that belong to node.

    Attributes:
        disks_list (list of DiskDetails): Specifies the list of disks.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "disks_list":'disksList'
    }

    def __init__(self,
                 disks_list=None):
        """Constructor for the ListOfDisks class"""

        # Initialize members of the class
        self.disks_list = disks_list


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
        disks_list = None
        if dictionary.get("disksList") is not None:
            disks_list = list()
            for structure in dictionary.get('disksList'):
                disks_list.append(cohesity_management_sdk.models_v2.disk_details.DiskDetails.from_dictionary(structure))

        # Return an object of this model
        return cls(disks_list)


