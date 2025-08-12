# -*- coding: utf-8 -*-


class PatchOperation(object):

    """Implementation of the 'Patch Operation.' model.

    Specifies a patch operation.

    Attributes:
        service (string): Specifies the name of the service.
        component (string): Specifies the description of the service.
        version (string): Specifies the version of the patch.
        version_replaced (string): Specifies the version it replaced.
        operation (string): Specifies what patch management operation was
            performed
        operation_time_msecs (long|int): Specifies the time when the patch
            operation was done in Unix epoch in milliseconds.
        user (string): Specifies the user who performed the operation.
        domain (string): Specifies the domain of the user.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "service":'service',
        "component":'component',
        "version":'version',
        "version_replaced":'versionReplaced',
        "operation":'operation',
        "operation_time_msecs":'operationTimeMsecs',
        "user":'user',
        "domain":'domain'
    }

    def __init__(self,
                 service=None,
                 component=None,
                 version=None,
                 version_replaced=None,
                 operation=None,
                 operation_time_msecs=None,
                 user=None,
                 domain=None):
        """Constructor for the PatchOperation class"""

        # Initialize members of the class
        self.service = service
        self.component = component
        self.version = version
        self.version_replaced = version_replaced
        self.operation = operation
        self.operation_time_msecs = operation_time_msecs
        self.user = user
        self.domain = domain


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
        version_replaced = dictionary.get('versionReplaced')
        operation = dictionary.get('operation')
        operation_time_msecs = dictionary.get('operationTimeMsecs')
        user = dictionary.get('user')
        domain = dictionary.get('domain')

        # Return an object of this model
        return cls(service,
                   component,
                   version,
                   version_replaced,
                   operation,
                   operation_time_msecs,
                   user,
                   domain)


