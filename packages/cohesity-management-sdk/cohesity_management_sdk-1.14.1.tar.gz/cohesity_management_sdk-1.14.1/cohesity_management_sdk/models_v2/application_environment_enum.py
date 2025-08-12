# -*- coding: utf-8 -*-

class ApplicationEnvironmentEnum(object):

    """Implementation of the 'ApplicationEnvironment' enum.

    Specifies the type of application enviornment needed for filtering to be
    applied on. This is needed because in case of applications like SQL,
    Oracle, a single source can contain multiple application enviornments.

    Attributes:
        KSQL: TODO: type description here.

    """

    KSQL = 'kSQL'

