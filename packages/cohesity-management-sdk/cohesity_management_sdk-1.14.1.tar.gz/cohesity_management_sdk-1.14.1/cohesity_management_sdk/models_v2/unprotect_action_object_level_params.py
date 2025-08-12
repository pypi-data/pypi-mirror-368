# -*- coding: utf-8 -*-


class UnprotectActionObjectLevelParams(object):

    """Implementation of the 'UnprotectActionObjectLevelParams' model.

    Specifies the request parameters for Unprotect action on a Protected
    object.

    Attributes:
        id (long|int): Specifies the ID of the object.
        name (string): Specifies the name of the object.
        delete_all_snapshots (bool): Specifies whether to delete all snapshots
            along with unprotecting object protection. If set to true, all
            snapshots will be deleted and no more recoverable.
        force_unprotect (bool): If specified as true then it will cancel the
            ongoing runs and immediatly unprotect.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "delete_all_snapshots":'deleteAllSnapshots',
        "force_unprotect":'forceUnprotect'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 delete_all_snapshots=None,
                 force_unprotect=None):
        """Constructor for the UnprotectActionObjectLevelParams class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.delete_all_snapshots = delete_all_snapshots
        self.force_unprotect = force_unprotect


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
        id = dictionary.get('id')
        name = dictionary.get('name')
        delete_all_snapshots = dictionary.get('deleteAllSnapshots')
        force_unprotect = dictionary.get('forceUnprotect')

        # Return an object of this model
        return cls(id,
                   name,
                   delete_all_snapshots,
                   force_unprotect)


