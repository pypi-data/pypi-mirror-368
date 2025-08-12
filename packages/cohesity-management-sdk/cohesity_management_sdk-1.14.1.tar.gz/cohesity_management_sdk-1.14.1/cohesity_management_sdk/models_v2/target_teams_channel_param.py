# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.recovery_object_identifier

class TargetTeamsChannelParam(object):

    """Implementation of the 'TargetTeamsChannelParam' model.

    Specifies the target Site to recover to.

    Attributes:
        id (string): Specifies the id of the target channel.
        name (string): Specifies the name of the target channel.
        create_new_channel (bool): Specifies whether we should create a new channel. If this is
          true name must not be empty
        channel_type (ChannelTypeEnum): Specifies the prefix for the target doc lib.
        channel_owners (list of RecoveryObjectIdentifier): List of owners for the private channel. At least one owner is
          needed to create a private channel
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "create_new_channel":'createNewChannel',
        "channel_type":'channelType',
        "channel_owners":'channelOwners'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 create_new_channel=None,
                 channel_type=None,
                 channel_owners=None
                 ):
        """Constructor for the TargetTeamsChannelParam class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.create_new_channel = create_new_channel
        self.channel_type = channel_type
        self.channel_owners = channel_owners


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
        id = dictionary.get('id')
        name = dictionary.get('name')
        create_new_channel = dictionary.get('createNewChannel')
        channel_type = dictionary.get('channelType')
        channel_owners = None
        if dictionary.get('channelOwners') is not None:
            channel_owners = list()
            for structure in dictionary.get('channelOwners'):
                channel_owners.append(cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(structure))


        # Return an object of this model
        return cls(id,
                   name,
                   create_new_channel,
                   channel_type,
                   channel_owners
                   )