# -*- coding: utf-8 -*-

class Type2Enum(object):

    """Implementation of the 'Type2' enum.

    Specifies the type of permission.
    'Allow' indicates access is allowed.
    'Deny' indicates access is denied.
    'SpecialType' indicates a type defined in the Access Control Entry (ACE)
    does not map to 'Allow' or 'Deny'.

    Attributes:
        ALLOW: TODO: type description here.
        DENY: TODO: type description here.
        SPECIALTYPE: TODO: type description here.

    """

    ALLOW = 'Allow'

    DENY = 'Deny'

    SPECIALTYPE = 'SpecialType'

