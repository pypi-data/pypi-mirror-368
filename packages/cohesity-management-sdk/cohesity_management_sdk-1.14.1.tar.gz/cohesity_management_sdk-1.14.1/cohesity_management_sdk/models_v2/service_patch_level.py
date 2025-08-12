# -*- coding: utf-8 -*-


class ServicePatchLevel(object):

    """Implementation of the 'ServicePatchLevel' model.

    Patch level of a service. It is the number of patches applied for the
    service on the cluster. If a service is never patched the patch level is
    0. If two patches were applied, patch level is 2.

    Attributes:
        service (string): Specifies the name of the service.
        patch_level (long|int): Specifies patch level of the service.
        patch_version (string): Specifies the version of the service patch
            after the patch operation.
        start_level (long|int): Specifies patch level of the service before the
            patch operation.
        start_version (string): Specifies the version of the service running on
            the cluster before the patch operation.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "service":'service',
        "patch_level":'patchLevel',
        "patch_version":'patchVersion',
        "start_level":'startLevel',
        "start_version":'startVersion'
    }

    def __init__(self,
                 service=None,
                 patch_level=None,
                 patch_version=None,
                 start_level=None,
                 start_version=None):
        """Constructor for the ServicePatchLevel class"""

        # Initialize members of the class
        self.service = service
        self.patch_level = patch_level
        self.patch_version = patch_version
        self.start_level = start_level
        self.start_version = start_version


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
        service = dictionary.get('service')
        patch_level = dictionary.get('patchLevel')
        patch_version = dictionary.get('patchVersion')
        start_level = dictionary.get('startLevel')
        start_version = dictionary.get('startVersion')

        # Return an object of this model
        return cls(service,
                   patch_level,
                   patch_version,
                   start_level,
                   start_version)


