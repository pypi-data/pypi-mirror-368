# -*- coding: utf-8 -*-


class PatchDetail(object):

    """Implementation of the 'PatchDetail' model.

    Detail of a patch. It gives the service and version information of the the
    patch.

    Attributes:
        service (string): Specifies the name of the service.
        component (string): Specifies the user friendly name of the service.
        version (string): Specifies the existing version of the service. This
            is the available service patch version if exists. If there is no
            patch available, then it is the applied patch version if applied.
            If both don't exist, it is the base version of the service.
        import_version (string): Specifies the version of the imported service
            patch.
        status (string): Specifies the status of the patch whether it is
            accepted or rejected. A patch is rejected if it is older than the
            version available or applied on the cluster.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "service":'service',
        "component":'component',
        "version":'version',
        "import_version":'import_version',
        "status":'status'
    }

    def __init__(self,
                 service=None,
                 component=None,
                 version=None,
                 import_version=None,
                 status=None):
        """Constructor for the PatchDetail class"""

        # Initialize members of the class
        self.service = service
        self.component = component
        self.version = version
        self.import_version = import_version
        self.status = status


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
        component = dictionary.get('component')
        version = dictionary.get('version')
        import_version = dictionary.get('import_version')
        status = dictionary.get('status')

        # Return an object of this model
        return cls(service,
                   component,
                   version,
                   import_version,
                   status)


