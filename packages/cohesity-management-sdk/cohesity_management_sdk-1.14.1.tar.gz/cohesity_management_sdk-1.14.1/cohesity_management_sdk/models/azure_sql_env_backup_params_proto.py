# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.entity_sku
import cohesity_management_sdk.models.sql_package

class AzureSqlEnvBackupParamsProto(object):

    """Implementation of the 'AzureSqlEnvBackupParamsProto' model.

    Message to capture additional backup params specific to Azure SQL.

    Attributes:
        copy_database (bool): If the flag is set to true, a copy of the
            database is created during
            backup, and the backup is performed from the copied database. This backup
            will be transactionally consistent.
            If the flag is set to false, the backup is performed from the production
            database while transactions are in progress. In this case, the backup will
            be transactionally inconsis.tent, and recovery can fail or the recovered
            database may be in an inconsistent state.
        copy_db_sku (Entity_SKU): SKU for the copy db.
        disk_type (int):  The type of temporary disk to be provisioned for
            database backup.
        sql_package_options (SqlPackage):  Can be one of temp_disk_size_gb enum above.
        temp_disk_size_gb (int):  Size of the disk we will attach to rigel to
            use for exporting this DB.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "copy_database":'copyDatabase',
        "copy_db_sku":'copyDbSku',
        "disk_type":'diskType',
        "sql_package_options":'sqlPackageOptions',
        "temp_disk_size_gb":'tempDiskSizeGb'
    }

    def __init__(self,
                 copy_database=None,
                 copy_db_sku=None,
                 disk_type=None,
                 sql_package_options=None,
                 temp_disk_size_gb=None):
        """Constructor for the AzureSqlEnvBackupParamsProto class"""

        # Initialize members of the class
        self.copy_database = copy_database
        self.copy_db_sku = copy_db_sku
        self.disk_type = disk_type
        self.sql_package_options = sql_package_options
        self.temp_disk_size_gb = temp_disk_size_gb


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The names
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        copy_database =  dictionary.get('copyDatabase')
        copy_db_sku = cohesity_management_sdk.models.entity_sku.Entity_SKU.from_dictionary(dictionary.get('copyDbSku')) if dictionary.get('copyDbSku') else None
        disk_type =dictionary.get('diskType')
        sql_package_options =  cohesity_management_sdk.models.sql_package.SqlPackage.from_dictionary(dictionary.get('sqlPackageOptions')) if dictionary.get('sqlPackageOptions') else None
        temp_disk_size_gb = dictionary.get('tempDiskSizeGb')

        # Return an object of this model
        return cls(copy_database,
                   copy_db_sku,
                   disk_type,
                   sql_package_options,
                   temp_disk_size_gb)


