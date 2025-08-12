# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.fixed_issue

class AppliedPatch(object):

    """Implementation of the 'Applied Patch.' model.

    Specifies the description of an applied patch.

    Attributes:
        service (string): Specifies the name of the service.
        component (string): Specifies the description of the service.
        version (string): Specifies the version of the patch.
        version_replaced (string): Specifies the version it replaced.
        patch_level (long|int): Specifies the number of patches applied so far
            for this service.
        applied_time_msecs (long|int): Specifies the time when the patch was
            applied in Unix epoch in milliseconds.
        count (long|int): Specifies the number of fixed issues.
        dependencies (list fo string): Specifies the services for which their
            patches were applied together.
            They will also be reverted together.
        fixed_issues (list of FixedIssue): Specifies the details of the fixes in the
            patch.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "service":'service',
        "component":'component',
        "version":'version',
        "version_replaced":'versionReplaced',
        "patch_level":'patchLevel',
        "applied_time_msecs":'appliedTimeMsecs',
        "count":'count',
        "dependencies":'dependencies',
        "fixed_issues":'fixedIssues'
    }

    def __init__(self,
                 service=None,
                 component=None,
                 version=None,
                 version_replaced=None,
                 patch_level=None,
                 applied_time_msecs=None,
                 count=None,
                 dependencies=None,
                 fixed_issues=None):
        """Constructor for the AppliedPatch class"""

        # Initialize members of the class
        self.service = service
        self.component = component
        self.version = version
        self.version_replaced = version_replaced
        self.patch_level = patch_level
        self.applied_time_msecs = applied_time_msecs
        self.count = count
        self.dependencies = dependencies
        self.fixed_issues = fixed_issues


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
        patch_level = dictionary.get('patchLevel')
        applied_time_msecs = dictionary.get('appliedTimeMsecs')
        count = dictionary.get('count')
        dependencies = dictionary.get('dependencies')
        fixed_issues = None
        if dictionary.get("fixedIssues") is not None:
            fixed_issues = list()
            for structure in dictionary.get('fixedIssues'):
                fixed_issues.append(cohesity_management_sdk.models_v2.fixed_issue.FixedIssue.from_dictionary(structure))

        # Return an object of this model
        return cls(service,
                   component,
                   version,
                   version_replaced,
                   patch_level,
                   applied_time_msecs,
                   count,
                   dependencies,
                   fixed_issues)


