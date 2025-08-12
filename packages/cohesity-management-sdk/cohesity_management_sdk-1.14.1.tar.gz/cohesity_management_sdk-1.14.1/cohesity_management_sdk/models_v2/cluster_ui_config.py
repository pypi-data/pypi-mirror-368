# -*- coding: utf-8 -*-


class ClusterUiConfig(object):

    """Implementation of the 'ClusterUiConfig' model.

    Specifies the params to update UI config.

    Attributes:
        ui_config (string): Specifies the customized UI config.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "ui_config":'uiConfig'
    }

    def __init__(self,
                 ui_config=None):
        """Constructor for the ClusterUiConfig class"""

        # Initialize members of the class
        self.ui_config = ui_config


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
        ui_config = dictionary.get('uiConfig')

        # Return an object of this model
        return cls(ui_config)


