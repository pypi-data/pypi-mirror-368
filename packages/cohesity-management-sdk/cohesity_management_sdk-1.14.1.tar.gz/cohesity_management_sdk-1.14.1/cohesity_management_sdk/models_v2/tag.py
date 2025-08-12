# -*- coding: utf-8 -*-


class Tag(object):

    """Implementation of the 'Tag.' model.

    Tag details

    Attributes:
        id (string): Specifies unique id of the Tag.
        name (string): Name of the Tag. Name has to be unique under
            Namespace.
        namespace (string): Namespace of the Tag. This is used to filter tags
            based on application or usecase. For example all tags related to
            vcenter can be put under one namespace or different departments
            could have their own namespaces e.g. finance/tag1 or
            operations/tag2 etc.
        tenant_id (string): Tenant Id to whom the Tag belongs.
        description (string): Description of the Tag.
        created_time_usecs (int): Specifies the timestamp in microseconds
            since the epoch when this Tag was created.
        last_updated_time_usecs (int): Specifies the timestamp in microseconds
            since the epoch when this Tag was last updated.
        marked_for_deletion (bool): If true, Tag is marked for deletion.
        ui_color (string): Color of the tag in UI.
        ui_path_elements (list of string): Path of the tag for UI nesting
            purposes.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "namespace":'namespace',
        "id":'id',
        "tenant_id":'tenantId',
        "description":'description',
        "created_time_usecs":'createdTimeUsecs',
        "last_updated_time_usecs":'lastUpdatedTimeUsecs',
        "marked_for_deletion":'markedForDeletion',
        "ui_color":'uiColor',
        "ui_path_elements":'uiPathElements'
    }

    def __init__(self,
                 name=None,
                 namespace=None,
                 id=None,
                 tenant_id=None,
                 description=None,
                 created_time_usecs=None,
                 last_updated_time_usecs=None,
                 marked_for_deletion=None,
                 ui_color=None,
                 ui_path_elements=None):
        """Constructor for the Tag class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.namespace = namespace
        self.tenant_id = tenant_id
        self.description = description
        self.created_time_usecs = created_time_usecs
        self.last_updated_time_usecs = last_updated_time_usecs
        self.marked_for_deletion = marked_for_deletion
        self.ui_color = ui_color
        self.ui_path_elements = ui_path_elements


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
        name = dictionary.get('name')
        namespace = dictionary.get('namespace')
        id = dictionary.get('id')
        tenant_id = dictionary.get('tenantId')
        description = dictionary.get('description')
        created_time_usecs = dictionary.get('createdTimeUsecs')
        last_updated_time_usecs = dictionary.get('lastUpdatedTimeUsecs')
        marked_for_deletion = dictionary.get('markedForDeletion')
        ui_color = dictionary.get('uiColor')
        ui_path_elements = dictionary.get('uiPathElements')

        # Return an object of this model
        return cls(name,
                   namespace,
                   id,
                   tenant_id,
                   description,
                   created_time_usecs,
                   last_updated_time_usecs,
                   marked_for_deletion,
                   ui_color,
                   ui_path_elements)


