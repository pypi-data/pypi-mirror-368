# -*- coding: utf-8 -*-


class CDPFilterStatus(object):

    """Implementation of the 'CDP Filter Status' model.

    CDP Filter Status

    Attributes:
        cdp_filter_status (CdpFilterStatus1Enum): Specifies the CDP filter
            status.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cdp_filter_status":'cdpFilterStatus'
    }

    def __init__(self,
                 cdp_filter_status=None):
        """Constructor for the CDPFilterStatus class"""

        # Initialize members of the class
        self.cdp_filter_status = cdp_filter_status


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
        cdp_filter_status = dictionary.get('cdpFilterStatus')

        # Return an object of this model
        return cls(cdp_filter_status)


