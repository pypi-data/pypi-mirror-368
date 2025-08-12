# -*- coding: utf-8 -*-

class RemovalStateEnum(object):

    """Implementation of the 'RemovalState' enum.

    Specifies the current removal state of the Storage Domain. 'DontRemove'
          means the state of object is functional and it is not being removed. 'MarkedForRemoval'
          means the object is being removed. 'OkToRemove' means the object has been
          removed on the Cohesity Cluster and if the object is physical, it can be
          removed from the Cohesity Cluster.

    Attributes:
        DONTREMOVE: TODO: type description here.
        MARKEDFORREMOVAL: TODO: type description here.
        OKTOREMOVE: TODO: type description here.

    """

    DONTREMOVE = 'DontRemove'

    MARKEDFORREMOVAL = 'MarkedForRemoval'

    OKTOREMOVE = 'OkToRemove'