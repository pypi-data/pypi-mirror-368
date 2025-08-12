# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class ViewProtocol(object):

    """Implementation of the 'ViewProtocol' model.

    TODO: type description here.


    Attributes:

        mode (string): Mode of protocol access.
          'ReadOnly'
          'ReadWrite'
          Enum: [ReadOnly ReadWrite]
        mtype (string): Type of protocol.
          Specifies the supported Protocols for the View.
          'NFS' enables protocol access to NFS v3.
          'NFS4' enables protocol access to NFS v4.1.
          'SMB' enables protocol access to SMB.
          'S3' enables protocol access to S3.
          'Swift' enables protocol access to Swift.
          Enum: [NFS NFS4 SMB S3 Swift]
    """


    # Create a mapping from Model property names to API property names
    _names = {
        "mode":'mode',
        "mtype":'type'
    }
    def __init__(self,
                 mode=None,
                 mtype=None
            ):

        """Constructor for the ViewProtocol class"""

        # Initialize members of the class
        self.mode = mode
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
        mode = dictionary.get('mode')
        mtype = dictionary.get('type')

        # Return an object of this model
        return cls(
            mode,
            mtype
)