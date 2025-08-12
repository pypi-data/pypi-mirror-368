# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.bug_fix

class AvailablePatch(object):

    """Implementation of the 'Available Patch.' model.

    Specifies the description of an available patch.

    Attributes:
        service (string): Specifies the name of the service.
        component (string): Specifies the description of the service.
        version (string): Specifies the version of the patch.
        bug_fixes (list of BugFix): Specifies the details of the fixes in the
            patch.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "service":'service',
        "component":'component',
        "version":'version',
        "bug_fixes":'bugFixes'
    }

    def __init__(self,
                 service=None,
                 component=None,
                 version=None,
                 bug_fixes=None):
        """Constructor for the AvailablePatch class"""

        # Initialize members of the class
        self.service = service
        self.component = component
        self.version = version
        self.bug_fixes = bug_fixes


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
        bug_fixes = None
        if dictionary.get("bugFixes") is not None:
            bug_fixes = list()
            for structure in dictionary.get('bugFixes'):
                bug_fixes.append(cohesity_management_sdk.models_v2.bug_fix.BugFix.from_dictionary(structure))

        # Return an object of this model
        return cls(service,
                   component,
                   version,
                   bug_fixes)


