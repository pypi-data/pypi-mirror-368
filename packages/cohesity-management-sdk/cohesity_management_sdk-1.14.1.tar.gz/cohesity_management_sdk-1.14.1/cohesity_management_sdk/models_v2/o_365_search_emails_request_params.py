# -*- coding: utf-8 -*-


class O365SearchEmailsRequestParams(object):

    """Implementation of the 'O365 Search Emails Request Params' model.

    Specifies email search request params specific to O365 environment.

    Attributes:
        domain_ids (list of long|int): Specifies the domain Ids in which
            mailboxes are registered.
        mailbox_ids (list of long|int): Specifies the mailbox Ids which
            contains the emails/folders.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "domain_ids":'domainIds',
        "mailbox_ids":'mailboxIds'
    }

    def __init__(self,
                 domain_ids=None,
                 mailbox_ids=None):
        """Constructor for the O365SearchEmailsRequestParams class"""

        # Initialize members of the class
        self.domain_ids = domain_ids
        self.mailbox_ids = mailbox_ids


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
        domain_ids = dictionary.get('domainIds')
        mailbox_ids = dictionary.get('mailboxIds')

        # Return an object of this model
        return cls(domain_ids,
                   mailbox_ids)


