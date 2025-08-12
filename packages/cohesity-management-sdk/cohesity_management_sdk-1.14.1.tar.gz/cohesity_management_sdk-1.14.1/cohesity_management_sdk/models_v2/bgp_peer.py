# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.bgp_timers

class BgpPeer(object):

    """Implementation of the 'BgpPeer' model.

    BGP peer information.

    Attributes:
        address_or_tag (string): IP Address.
        description (string): Peer's description.
        remote_as (int): Remote AS.
        timers (BgpTimers): BGP protocol timers.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "address_or_tag":'addressOrTag',
        "description":'description',
        "remote_as":'remoteAS',
        "timers":'timers'
    }

    def __init__(self,
                 address_or_tag=None,
                 description=None,
                 remote_as=None,
                 timers=None):
        """Constructor for the BgpPeer class"""

        # Initialize members of the class
        self.address_or_tag = address_or_tag
        self.description = description
        self.remote_as = remote_as
        self.timers = timers


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
        address_or_tag = dictionary.get('addressOrTag')
        description = dictionary.get('description')
        remote_as = dictionary.get('remoteAS')
        timers = cohesity_management_sdk.models_v2.bgp_timers.BgpTimers.from_dictionary(dictionary.get('timers')) if dictionary.get('timers') else None

        # Return an object of this model
        return cls(address_or_tag,
                   description,
                   remote_as,
                   timers)


