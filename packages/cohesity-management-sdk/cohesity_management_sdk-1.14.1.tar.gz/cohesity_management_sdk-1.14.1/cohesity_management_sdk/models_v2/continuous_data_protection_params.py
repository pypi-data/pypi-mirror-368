# -*- coding: utf-8 -*-


class ContinuousDataProtectionParams(object):

    """Implementation of the 'Continuous Data Protection Params.' model.

    Specifies the params for Continuous Data Protection.

    Attributes:
        enable_cdp_sync_replication (bool): Specifies whether synchronous
            replication is enabled for CDP Protection Group when replication
            target is specified in attached policy.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "enable_cdp_sync_replication":'enableCdpSyncReplication'
    }

    def __init__(self,
                 enable_cdp_sync_replication=None):
        """Constructor for the ContinuousDataProtectionParams class"""

        # Initialize members of the class
        self.enable_cdp_sync_replication = enable_cdp_sync_replication


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
        enable_cdp_sync_replication = dictionary.get('enableCdpSyncReplication')

        # Return an object of this model
        return cls(enable_cdp_sync_replication)


