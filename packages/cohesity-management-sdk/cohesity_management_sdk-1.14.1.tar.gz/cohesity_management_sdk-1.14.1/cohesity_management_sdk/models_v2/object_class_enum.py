# -*- coding: utf-8 -*-

class ObjectClassEnum(object):

    """Implementation of the 'ObjectClass' enum.

    Specifies the object class of the security principal.

    Attributes:
        USER: TODO: type description here.
        GROUP: TODO: type description here.
        COMPUTER: TODO: type description here.
        WELLKNOWNPRINCIPAL: TODO: type description here.
        SERVICEACCOUNT: TODO: type description here.

    """

    USER = 'User'

    GROUP = 'Group'

    COMPUTER = 'Computer'

    WELLKNOWNPRINCIPAL = 'WellKnownPrincipal'

    SERVICEACCOUNT = 'ServiceAccount'