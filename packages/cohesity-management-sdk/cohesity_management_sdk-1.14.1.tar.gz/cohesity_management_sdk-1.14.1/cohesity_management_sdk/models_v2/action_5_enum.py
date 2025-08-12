# -*- coding: utf-8 -*-

class Action5Enum(object):

    """Implementation of the 'Action5' enum.

    Specifies the action to be performed on all the specfied Protection
    Groups. 'kActivate' specifies that Protection Group should be activated.
    'kDeactivate' sepcifies that Protection Group should be deactivated.
    'kPause' specifies that Protection Group should be paused. 'kResume'
    specifies that Protection Group should be resumed.

    Attributes:
        KPAUSE: TODO: type description here.
        KRESUME: TODO: type description here.
        KACTIVATE: TODO: type description here.
        KDEACTIVATE: TODO: type description here.

    """

    KPAUSE = 'kPause'

    KRESUME = 'kResume'

    KACTIVATE = 'kActivate'

    KDEACTIVATE = 'kDeactivate'