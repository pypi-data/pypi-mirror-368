# -*- coding: utf-8 -*-


class ViewParams(object):

    """Implementation of the 'ViewParams' model.

    Specifies optional configuration parameters for the mounted view.

    Attributes:
        mount_dir (string): Specifes the absolute path on the host where the
            view will be mounted.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mount_dir":'mountDir'
    }

    def __init__(self,
                 mount_dir=None):
        """Constructor for the ViewParams class"""

        # Initialize members of the class
        self.mount_dir = mount_dir


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
        mount_dir = dictionary.get('mountDir')

        # Return an object of this model
        return cls(mount_dir)


