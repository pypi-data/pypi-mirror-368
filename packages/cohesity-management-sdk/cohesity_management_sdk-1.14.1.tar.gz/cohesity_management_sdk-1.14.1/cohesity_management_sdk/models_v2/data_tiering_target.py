# -*- coding: utf-8 -*-


class DataTieringTarget(object):

    """Implementation of the 'DataTieringTarget' model.

    Specifies the target data tiering details.

    Attributes:
        view_name (string): Specifies the view name.
        mount_path (string): Specifies the mount path inside the view.
        storage_domain_id (long|int): Specifies the Storage Domain ID where
            the view will be kept.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "view_name":'viewName',
        "storage_domain_id":'storageDomainId',
        "mount_path":'mountPath'
    }

    def __init__(self,
                 view_name=None,
                 storage_domain_id=None,
                 mount_path=None):
        """Constructor for the DataTieringTarget class"""

        # Initialize members of the class
        self.view_name = view_name
        self.mount_path = mount_path
        self.storage_domain_id = storage_domain_id


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
        view_name = dictionary.get('viewName')
        storage_domain_id = dictionary.get('storageDomainId')
        mount_path = dictionary.get('mountPath')

        # Return an object of this model
        return cls(view_name,
                   storage_domain_id,
                   mount_path)


