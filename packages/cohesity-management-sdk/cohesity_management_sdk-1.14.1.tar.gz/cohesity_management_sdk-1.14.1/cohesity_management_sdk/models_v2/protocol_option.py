# -*- coding: utf-8 -*-


class ProtocolOption(object):

    """Implementation of the 'Protocol Option' model.

    Specifies the protocol options for view.

    Attributes:
        mtype (Type3Enum): Type of protocol. Specifies the supported Protocols
            for the View.   'NFS' enables protocol access to NFS v3.   'NFS4'
            enables protocol access to NFS v4.1.   'SMB' enables protocol
            access to SMB.   'S3' enables protocol access to S3.   'Swift'
            enables protocol access to Swift.
        mode (Mode4Enum): Mode of protocol access.   'ReadOnly'   'ReadWrite'

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mtype":'type',
        "mode":'mode'
    }

    def __init__(self,
                 mtype=None,
                 mode=None):
        """Constructor for the ProtocolOption class"""

        # Initialize members of the class
        self.mtype = mtype
        self.mode = mode


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
        mtype = dictionary.get('type')
        mode = dictionary.get('mode')

        # Return an object of this model
        return cls(mtype,
                   mode)


