# -*- coding: utf-8 -*-

class IndexingStatusEnum(object):

    """Implementation of the 'IndexingStatus' enum.

    Specifies the indexing status of objects in this snapshot.<br>
    'InProgress' indicates the indexing is in progress.<br> 'Done' indicates
    indexing is done.<br> 'NoIndex' indicates indexing is not applicable.<br>
    'Error' indicates indexing failed with error.

    Attributes:
        INPROGRESS: TODO: type description here.
        DONE: TODO: type description here.
        NOINDEX: TODO: type description here.
        ERROR: TODO: type description here.

    """

    INPROGRESS = 'InProgress'

    DONE = 'Done'

    NOINDEX = 'NoIndex'

    ERROR = 'Error'

