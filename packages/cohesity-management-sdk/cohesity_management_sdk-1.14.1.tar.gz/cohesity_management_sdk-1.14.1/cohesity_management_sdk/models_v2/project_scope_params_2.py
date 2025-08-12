# -*- coding: utf-8 -*-


class ProjectScopeParams2(object):

    """Implementation of the 'ProjectScopeParams2' model.

    Specifies the parameter for project type scope.

    Attributes:
        project_name (string): Specifies the project name.
        domain_name (string): Specifies the domain name of the project.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "project_name":'projectName',
        "domain_name":'domainName'
    }

    def __init__(self,
                 project_name=None,
                 domain_name=None):
        """Constructor for the ProjectScopeParams2 class"""

        # Initialize members of the class
        self.project_name = project_name
        self.domain_name = domain_name


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
        project_name = dictionary.get('projectName')
        domain_name = dictionary.get('domainName')

        # Return an object of this model
        return cls(project_name,
                   domain_name)


