# -*- coding: utf-8 -*-


class TrustedCa(object):

    """Implementation of the 'TrustedCa' model.

    Specifies the basic info about CA Root Certificate.

    Attributes:
        id (string): Unique id for the certificate.
        name (string): Unique name for the certificate.
        issued_by (string): Specifies the issuer.
        issued_to (string): Specifies whom it was issued to.
        issued_time_usecs (long|int): Specifies the timestamp epoch in
            microseconds when this certificate will start being valid.
        expiration_time_usecs (long|int): Specifies the timestamp epoch in
            microseconds when this certificate will no longer be valid.
        description (string): description of the certificate.
        registration_time_usecs (long|int): Specifies the timestamp epoch in
            microseconds when this certificate was registered on the cluster.
        last_validated_time_usecs (long|int): Specifies the timestamp epoch in
            microseconds when this certificate was last validated.
        status (Status25Enum): Validation Status of the certificate.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "issued_by":'issuedBy',
        "issued_to":'issuedTo',
        "issued_time_usecs":'issuedTimeUsecs',
        "expiration_time_usecs":'expirationTimeUsecs',
        "description":'description',
        "registration_time_usecs":'registrationTimeUsecs',
        "last_validated_time_usecs":'lastValidatedTimeUsecs',
        "status":'status'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 issued_by=None,
                 issued_to=None,
                 issued_time_usecs=None,
                 expiration_time_usecs=None,
                 description=None,
                 registration_time_usecs=None,
                 last_validated_time_usecs=None,
                 status=None):
        """Constructor for the TrustedCa class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.issued_by = issued_by
        self.issued_to = issued_to
        self.issued_time_usecs = issued_time_usecs
        self.expiration_time_usecs = expiration_time_usecs
        self.description = description
        self.registration_time_usecs = registration_time_usecs
        self.last_validated_time_usecs = last_validated_time_usecs
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
        id = dictionary.get('id')
        name = dictionary.get('name')
        issued_by = dictionary.get('issuedBy')
        issued_to = dictionary.get('issuedTo')
        issued_time_usecs = dictionary.get('issuedTimeUsecs')
        expiration_time_usecs = dictionary.get('expirationTimeUsecs')
        description = dictionary.get('description')
        registration_time_usecs = dictionary.get('registrationTimeUsecs')
        last_validated_time_usecs = dictionary.get('lastValidatedTimeUsecs')
        status = dictionary.get('status')

        # Return an object of this model
        return cls(id,
                   name,
                   issued_by,
                   issued_to,
                   issued_time_usecs,
                   expiration_time_usecs,
                   description,
                   registration_time_usecs,
                   last_validated_time_usecs,
                   status)


