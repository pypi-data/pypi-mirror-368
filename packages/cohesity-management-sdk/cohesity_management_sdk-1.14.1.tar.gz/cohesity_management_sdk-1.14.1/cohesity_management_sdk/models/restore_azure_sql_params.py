# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.entity_sku
import cohesity_management_sdk.models.sql_package

class RestoreAzureSQLParams(object):

    """Implementation of the 'RestoreAzureSQLParams' model.

    TODO: type model description here.

    Attributes:
        disk_type (int): The type of temporary disk to be provisioned for
            database restore.
        new_database_name (string): The new name of the database.
            It is optional, if not specified then backup time database name
            will be used.
        overwrite_database (bool): If false, recovery will fail if the database
            (with same name as this request) exists on the target server.
            If true, recovery will delete/overwrite the existing database as
            part of recovery.
        restored_db_sku (Entity_SKU): Specifies a list of
            schemaInfos of the tenant (organization).
        sql_package_options (SqlPackage): Specifies the data usage metric of the data
            stored on the Cohesity Cluster or Storage Domains (View Boxes).

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "disk_type":'diskType',
        "new_database_name":'newDatabaseName',
        "overwrite_database":'overwriteDatabase',
        "restored_db_sku":'restoredDbSku',
        "sql_package_options":'sqlPackageOptions'
    }

    def __init__(self,
                 disk_type=None,
                 new_database_name=None,
                 overwrite_database=None,
                 restored_db_sku=None,
                 sql_package_options=None):
        """Constructor for the RestoreAzureSQLParams class"""

        # Initialize members of the class
        self.disk_type = disk_type
        self.new_database_name = new_database_name
        self.overwrite_database = overwrite_database
        self.restored_db_sku = restored_db_sku
        self.sql_package_options = sql_package_options


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
        disk_type = dictionary.get('diskType')
        new_database_name = dictionary.get('newDatabaseName')
        overwrite_database = dictionary.get('overwriteDatabase')
        restored_db_sku = cohesity_management_sdk.models.entity_sku.Entity_SKU.from_dictionary(dictionary.get('restoredDbSku')) if dictionary.get('restoredDbSku') else None
        sql_package_options = cohesity_management_sdk.models.sql_package.SqlPackage.from_dictionary(dictionary.get('sqlPackageOptions')) if dictionary.get('sqlPackageOptions') else None

        # Return an object of this model
        return cls(disk_type,
                   new_database_name,
                   overwrite_database,
                   restored_db_sku,
                   sql_package_options)


