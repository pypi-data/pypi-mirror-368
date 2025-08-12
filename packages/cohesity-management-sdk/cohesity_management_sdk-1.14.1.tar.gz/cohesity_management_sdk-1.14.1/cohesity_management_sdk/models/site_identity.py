# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class SiteIdentity(object):

    """Implementation of the 'SiteIdentity' model.

    O365 Sharepoint online Site Identity. These may be obtained by Graph/REST
    or PnP cmdlets. All fields are case insensitive.

    Attributes:
        id (string): Unique guid for the site in SPO. This is a unqiue
            identifier that can be used to compare sites.
        server_relativeurl (string): Optional ServerRelativeUrl. Not required.
        site_entity_id (long|int): Entity Id of the site.
        title (string): Optional Title of site for display and logging
            purpose. Not mandatory.
        url (string): Full Url of the site. Its of the form
            https://yourtenant.sharepoint.com/sites/yoursite or
            https://yourtenant.sharepoint.com/yoursite
            This parameter is required for all PnP operations.
        webid (string): Unique guid for the site root web.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "server_relativeurl":'serverRelativeurl',
        "site_entity_id":'siteEntityId',
        "title":'title',
        "url":'url',
        "webid":'webid'
    }

    def __init__(self,
                 id=None,
                 server_relativeurl=None,
                 site_entity_id=None,
                 title=None,
                 url=None,
                 webid=None):
        """Constructor for the SiteIdentity class"""

        # Initialize members of the class
        self.id = id
        self.server_relativeurl = server_relativeurl
        self.site_entity_id = site_entity_id
        self.title = title
        self.url = url
        self.webid = webid


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
        server_relativeurl = dictionary.get('serverRelativeurl')
        site_entity_id = dictionary.get('siteEntityId')
        title = dictionary.get('title')
        webid = dictionary.get('webid')
        url = dictionary.get('url')

        # Return an object of this model
        return cls(id,
                   server_relativeurl,
                   site_entity_id,
                   title,
                   url,
                   webid)