# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.source_registration

class SourceRegistrations(object):

    """Implementation of the 'SourceRegistrations' model.

    Protection Source Registrations.

    Attributes:
        registrations (list of SourceRegistration): Specifies the list of
            Protection Source Registrations.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "registrations":'registrations'
    }

    def __init__(self,
                 registrations=None):
        """Constructor for the SourceRegistrations class"""

        # Initialize members of the class
        self.registrations = registrations


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
        registrations = None
        if dictionary.get("registrations") is not None:
            registrations = list()
            for structure in dictionary.get('registrations'):
                registrations.append(cohesity_management_sdk.models_v2.source_registration.SourceRegistration.from_dictionary(structure))

        # Return an object of this model
        return cls(registrations)


