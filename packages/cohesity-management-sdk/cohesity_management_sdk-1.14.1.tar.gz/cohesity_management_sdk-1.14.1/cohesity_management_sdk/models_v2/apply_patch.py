# -*- coding: utf-8 -*-


class ApplyPatch(object):

    """Implementation of the 'Apply patch.' model.

    Specifies the request to apply a patch.

    Attributes:
        service (string): Specifies the name of the service whose patch should
            be applied.
        all (bool): Specifies all the available patches should be applied.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "service":'service',
        "all":'all'
    }

    def __init__(self,
                 service=None,
                 all=None):
        """Constructor for the ApplyPatch class"""

        # Initialize members of the class
        self.service = service
        self.all = all


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
        service = dictionary.get('service')
        all = dictionary.get('all')

        # Return an object of this model
        return cls(service,
                   all)


