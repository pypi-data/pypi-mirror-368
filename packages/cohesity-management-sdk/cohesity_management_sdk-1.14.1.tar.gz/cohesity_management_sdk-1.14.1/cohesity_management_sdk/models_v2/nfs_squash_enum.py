# -*- coding: utf-8 -*-

class NfsSquashEnum(object):

    """Implementation of the 'NfsSquash' enum.

    Specifies which nfsSquash Mounted.
    'kNone' mounts none.
    'kRootSquash' mounts nfsRootSquash. Whether clients from this subnet can
    mount as root on NFS.
    'kAllSquash' mounts nfsAllSquash. Whether all clients from this subnet
    can
    map view with view_all_squash_uid/view_all_squash_gid configured in
    the view.

    Attributes:
        KNONE: TODO: type description here.
        KROOTSQUASH: TODO: type description here.
        KALLSQUASH: TODO: type description here.

    """

    KNONE = 'kNone'

    KROOTSQUASH = 'kRootSquash'

    KALLSQUASH = 'kAllSquash'

