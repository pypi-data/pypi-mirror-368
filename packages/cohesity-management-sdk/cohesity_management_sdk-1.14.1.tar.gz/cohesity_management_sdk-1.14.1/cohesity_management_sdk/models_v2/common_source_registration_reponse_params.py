# -*- coding: utf-8 -*-


class CommonSourceRegistrationReponseParams(object):

    """Implementation of the 'CommonSourceRegistrationReponseParams' model.

    Specifies the parameters which are common between all Protection Source
    registrations.

    Attributes:
        id (long|int): Source Registration ID. This can be used to retrieve,
            edit or delete the source registration.
        source_id (long|int): ID of top level source object discovered after
            the registration.
        environment (Environment8Enum): Specifies the environment type of the
            Protection Source.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "source_id":'sourceId',
        "environment":'environment'
    }

    def __init__(self,
                 id=None,
                 source_id=None,
                 environment=None):
        """Constructor for the CommonSourceRegistrationReponseParams class"""

        # Initialize members of the class
        self.id = id
        self.source_id = source_id
        self.environment = environment


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
        source_id = dictionary.get('sourceId')
        environment = dictionary.get('environment')

        # Return an object of this model
        return cls(id,
                   source_id,
                   environment)


