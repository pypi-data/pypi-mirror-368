# -*- coding: utf-8 -*-


class TargetOneDriveParam(object):

    """Implementation of the 'TargetOneDriveParam' model.

    Specifies the target OneDrive to recover to.

    Attributes:
        id (long|int): Specifies the id of the object.
        name (string): Specifies the name of the object.
        target_folder_path (string): Specifies the path to the target folder.
        primary_smtp_address (string): Specifies the primary SMTP address of the target onedrive. Atleast
          one of id or primarySMTPAddress needs to be defined. In case both id and
          primarySMTPAddress are defined then id takes precedence.
        parent_source_id (long|int): Specifies the id of the domain for alternate domain recovery.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "target_folder_path":'targetFolderPath',
        "name":'name',
        "primary_smtp_address":'primarySmtpAddress',
        "parent_source_id":'parentSourceId'
    }

    def __init__(self,
                 id=None,
                 target_folder_path=None,
                 name=None,
                 primary_smtp_address=None,
                 parent_source_id=None
                 ):
        """Constructor for the TargetOneDriveParam class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.target_folder_path = target_folder_path
        self.primary_smtp_address = primary_smtp_address
        self.parent_source_id = parent_source_id


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
        target_folder_path = dictionary.get('targetFolderPath')
        name = dictionary.get('name')
        primary_smtp_address = dictionary.get('primarySmtpAddress')
        parent_source_id = dictionary.get('parentSourceId')

        # Return an object of this model
        return cls(id,
                   target_folder_path,
                   name,
                   primary_smtp_address,
                   parent_source_id)