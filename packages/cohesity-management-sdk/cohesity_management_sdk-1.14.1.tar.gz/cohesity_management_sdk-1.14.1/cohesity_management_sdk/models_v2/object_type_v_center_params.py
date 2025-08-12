# -*- coding: utf-8 -*-


class ObjectTypeVCenterParams(object):

    """Implementation of the 'Object Type VCenter Params' model.

    TODO: type model description here.

    Attributes:
        is_cloud_env (bool): Specifies that registered vCenter source is a VMC
            (VMware Cloud) environment or not.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "is_cloud_env":'isCloudEnv'
    }

    def __init__(self,
                 is_cloud_env=None):
        """Constructor for the ObjectTypeVCenterParams class"""

        # Initialize members of the class
        self.is_cloud_env = is_cloud_env


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
        is_cloud_env = dictionary.get('isCloudEnv')

        # Return an object of this model
        return cls(is_cloud_env)


