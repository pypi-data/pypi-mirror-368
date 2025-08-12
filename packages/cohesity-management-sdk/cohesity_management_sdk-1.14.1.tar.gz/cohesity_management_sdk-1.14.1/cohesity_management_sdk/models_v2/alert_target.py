# -*- coding: utf-8 -*-


class AlertTarget(object):

    """Implementation of the 'AlertTarget' model.

    Specifies an alert target to receive an alert.

    Attributes:
        email_address (string): Specifies an email address to receive an
            alert.
        language (Language3Enum): Specifies the language of the delivery
            target. Default value is 'en-us'.
        recipient_type (RecipientTypeEnum): Specifies the recipient type of
            email recipient. Default value is 'kTo'.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "email_address":'emailAddress',
        "language":'language',
        "recipient_type":'recipientType'
    }

    def __init__(self,
                 email_address=None,
                 language=None,
                 recipient_type=None):
        """Constructor for the AlertTarget class"""

        # Initialize members of the class
        self.email_address = email_address
        self.language = language
        self.recipient_type = recipient_type


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
        email_address = dictionary.get('emailAddress')
        language = dictionary.get('language')
        recipient_type = dictionary.get('recipientType')

        # Return an object of this model
        return cls(email_address,
                   language,
                   recipient_type)


