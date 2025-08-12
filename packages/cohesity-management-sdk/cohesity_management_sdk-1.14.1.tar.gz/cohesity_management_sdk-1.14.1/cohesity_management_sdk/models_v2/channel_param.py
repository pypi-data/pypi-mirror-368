# -*- coding: utf-8 -*-


class ChannelParam(object):

    """Implementation of the 'ChannelParam' model.

    Specifies the parameters to recover a Microsoft 365 Teams Channel.

    Attributes:
        document_library_params (list of OneDriveParam): Specifies the list of doclibs of the Channel to recover. It is
          populated iff recoverEntireChannel is false.
        id (string): Specifies the Channel id.
        name (string): Specifies the Channel name.
        recover_entire_channel (bool): Specifies whether to recover the whole Microsoft 365 Channel.
        type (Type76Enum): Specifies the type of channel public or private


    """

    # Create a mapping from Model property names to API property names
    _names = {
        "document_library_params":'documentLibraryParams',
        "id":'id',
        "name":'name',
        "recover_entire_channel":'recoverEntireChannel',
        "mtype":'type'
    }

    def __init__(self,
                 document_library_params=None,
                 id=None,
                 name=None,
                 recover_entire_channel=None,
                 mtype=None):
        """Constructor for the ChannelParam class"""

        # Initialize members of the class
        self.document_library_params = document_library_params
        self.id = id
        self.name = name
        self.recover_entire_channel = recover_entire_channel
        self.mtype = mtype

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
        document_library_params = dictionary.get('documentLibraryParams')
        id = dictionary.get('id')
        name = dictionary.get('name')
        recover_entire_channel = dictionary.get('recoverEntireChannel')
        mtype = dictionary.get('type')

        # Return an object of this model
        return cls(document_library_params,
                   id,
                   name,
                   recover_entire_channel,
                   mtype)