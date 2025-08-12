# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.azure_sql_sku_options
import cohesity_management_sdk.models_v2.azure_object_protection_and_recovery_sql_package_options

class RecoverAzureSqlObjectParams(object):

    """Implementation of the 'Recover Azure Sql Object Params.' model.

     Specifies details of recovery object to be recovered.

    Attributes:
        new_database_name (string): Specifies the new name to which the object should be renamed
          to after the recovery.
        overwrite_database (bool): Set to true to overwrite an existing object at the destination.
          If set to false, and the same object exists at the destination, then recovery
          will fail for that object.
        restored_database_sku (AzureSqlSkuOptions): Specifies the SQL package options to be used during Azure SQL
          Object Recovery.
        sql_package_options (AzureObjectProtectionAndRecoverySQLPackageOption): Specifies the SQL package options to be used during Azure SQL
          Object Recovery.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "new_database_name":'newDatabaseName',
        "overwrite_database":'overwriteDatabase',
        "restored_database_sku":'restoredDatabaseSku',
        "sql_package_options":'sqlPackageOptions'
    }

    def __init__(self,
                 new_database_name=None,
                 overwrite_database=None,
                 restored_database_sku=None,
                 sql_package_options=None):
        """Constructor for the RecoverAzureSqlObjectParams class"""

        # Initialize members of the class
        self.new_database_name = new_database_name
        self.overwrite_database = overwrite_database
        self.restored_database_sku = restored_database_sku
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
        new_database_name = dictionary.get('newDatabaseName')
        overwrite_database = dictionary.get('overwriteDatabase')
        restored_database_sku = cohesity_management_sdk.models_v2.azure_sql_sku_options.AzureSqlSkuOptions.from_dictionary(
            dictionary.get('restoredDatabaseSku')) if dictionary.get('restoredDatabaseSku') else None
        sql_package_options = cohesity_management_sdk.models_v2.azure_object_protection_and_recovery_sql_package_options.AzureObjectProtectionAndRecoverySQLPackageOption.from_dictionary(
            dictionary.get('sqlPackageOptions')) if dictionary.get('sqlPackageOptions') else None

        # Return an object of this model
        return cls(new_database_name,
                   overwrite_database,
                   restored_database_sku,
                   sql_package_options)