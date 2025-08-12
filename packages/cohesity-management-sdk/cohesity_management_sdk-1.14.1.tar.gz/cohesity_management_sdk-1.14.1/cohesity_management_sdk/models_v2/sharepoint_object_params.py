# -*- coding: utf-8 -*-


class SharepointObjectParams(object):

    """Implementation of the 'SharepointObjectParams' model.

    Specifies the common parameters for Sharepoint site objects.

    Attributes:
        site_web_url (string): Specifies the web url for the Sharepoint site.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "site_web_url":'siteWebUrl'
    }

    def __init__(self,
                 site_web_url=None):
        """Constructor for the SharepointObjectParams class"""

        # Initialize members of the class
        self.site_web_url = site_web_url


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
        site_web_url = dictionary.get('siteWebUrl')

        # Return an object of this model
        return cls(site_web_url)


