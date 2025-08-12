# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.bgp_peer
import cohesity_management_sdk.models_v2.bgp_timers

class BgpInstance(object):

    """Implementation of the 'bgpInstance' model.

    BGP instance.

    Attributes:
        local_as (int): Local AS.
        peers (list of BgpPeer): List of bgp peer groups.
        timers (BgpTimers): BGP protocol timers.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "local_as":'localAS',
        "peers":'peers',
        "timers":'timers'
    }

    def __init__(self,
                 local_as=None,
                 peers=None,
                 timers=None):
        """Constructor for the BgpInstance class"""

        # Initialize members of the class
        self.local_as = local_as
        self.peers = peers
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
        local_as = dictionary.get('localAS')
        peers = None
        if dictionary.get("peers") is not None:
            peers = list()
            for structure in dictionary.get('peers'):
                peers.append(cohesity_management_sdk.models_v2.bgp_peer.BgpPeer.from_dictionary(structure))
        timers = cohesity_management_sdk.models_v2.bgp_timers.BgpTimers.from_dictionary(dictionary.get('timers')) if dictionary.get('timers') else None

        # Return an object of this model
        return cls(local_as,
                   peers,
                   timers)


