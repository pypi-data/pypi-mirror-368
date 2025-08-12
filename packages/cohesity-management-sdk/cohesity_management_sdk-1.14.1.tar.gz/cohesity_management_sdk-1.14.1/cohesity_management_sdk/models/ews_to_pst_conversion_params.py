# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class EwsToPstConversionParams(object):

    """Implementation of the 'EwsToPstConversionParams' model.

    Attributes:
        create_pst (bool): Create Msg files or Pst.
            false value indicates only create msg files.
            Default value is true.
        encrypted_pst_password (string): Encrypted version of the pst_password
            above. The plain password should be cleared and the encrypted form
            should be persisted in the restore task
            state proto.
        option_flags (int): ConvertEwsToPst flags of pstSizeThreshold
            ConvertEwsToPSTOptionFlags.
        pst_name_prefix (string): Name prefix for generated PST files.
        pst_password (string): Optional password to be set for the output PSTs.
        pst_size_threshold (long|int): PST rotation size in bytes.
        separate_download_files (bool): Whether there should be a separate PST file created per snapshot
          or not.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "create_pst":'createPst',
        "encrypted_pst_password": 'encryptedPstPassword',
        "option_flags":'optionFlags',
        "pst_name_prefix":'pstNamePrefix',
        "pst_password":'pstPassword',
        "pst_size_threshold":'pstSizeThreshold',
        "separate_download_files":'separateDownloadFiles'
    }

    def __init__(self,
                 create_pst=None,
                 encrypted_pst_password=None,
                 option_flags=None,
                 pst_name_prefix=None,
                 pst_password=None,
                 pst_size_threshold=None,
                 separate_download_files=None):
        """Constructor for the EwsToPstConversionParams class"""

        # Initialize members of the class
        self.create_pst = create_pst
        self.encrypted_pst_password = encrypted_pst_password
        self.option_flags = option_flags
        self.pst_name_prefix = pst_name_prefix
        self.pst_password = pst_password
        self.pst_size_threshold = pst_size_threshold
        self.separate_download_files = separate_download_files


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
        create_pst = dictionary.get('createPst')
        encrypted_pst_password = dictionary.get('encryptedPstPassword')
        option_flags = dictionary.get('optionFlags')
        pst_name_prefix = dictionary.get('pstNamePrefix')
        pst_size_threshold = dictionary.get('pstSizeThreshold')
        pst_password = dictionary.get('pstPassword')
        separate_download_files = dictionary.get('separateDownloadFiles')


        # Return an object of this model
        return cls(create_pst,
                   encrypted_pst_password,
                   option_flags,
                   pst_name_prefix,
                   pst_password,
                   pst_size_threshold,
                   separate_download_files)