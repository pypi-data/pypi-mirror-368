# -*- coding: utf-8 -*-

class Type3Enum(object):

    """Implementation of the 'Type3' enum.

    Type of protocol.
    Specifies the supported Protocols for the View.
      'NFS' enables protocol access to NFS v3.
      'NFS4' enables protocol access to NFS v4.1.
      'SMB' enables protocol access to SMB.
      'S3' enables protocol access to S3.
      'Swift' enables protocol access to Swift.

    Attributes:
        NFS: TODO: type description here.
        SMB: TODO: type description here.
        S3: TODO: type description here.
        SWIFT: TODO: type description here.

    """

    NFS = 'NFS'

    SMB = 'SMB'

    S3 = 'S3'

    SWIFT = 'Swift'

