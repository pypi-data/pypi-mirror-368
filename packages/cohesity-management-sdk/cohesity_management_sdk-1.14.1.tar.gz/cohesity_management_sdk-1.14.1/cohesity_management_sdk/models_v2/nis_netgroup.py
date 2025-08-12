# -*- coding: utf-8 -*-


class NisNetgroup(object):

    """Implementation of the 'NisNetgroup' model.

    Specifies an NIS netgroup.

    Attributes:
        name (string): Specifies the netgroup name.
        domain (string): Specifies the domain name for the netgroup.
        nfs_access (NfsAccess1Enum): Specifies NFS protocol acess level for
            clients from the netgroup.
        nfs_squash (NfsSquashEnum): Specifies which nfsSquash Mounted. 'kNone'
            mounts none. 'kRootSquash' mounts nfsRootSquash. Whether clients
            from this subnet can mount as root on NFS. 'kAllSquash' mounts
            nfsAllSquash. Whether all clients from this subnet can map view
            with view_all_squash_uid/view_all_squash_gid configured in the
            view.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "domain":'domain',
        "nfs_access":'nfsAccess',
        "nfs_squash":'nfsSquash'
    }

    def __init__(self,
                 name=None,
                 domain=None,
                 nfs_access=None,
                 nfs_squash=None):
        """Constructor for the NisNetgroup class"""

        # Initialize members of the class
        self.name = name
        self.domain = domain
        self.nfs_access = nfs_access
        self.nfs_squash = nfs_squash


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
        name = dictionary.get('name')
        domain = dictionary.get('domain')
        nfs_access = dictionary.get('nfsAccess')
        nfs_squash = dictionary.get('nfsSquash')

        # Return an object of this model
        return cls(name,
                   domain,
                   nfs_access,
                   nfs_squash)


