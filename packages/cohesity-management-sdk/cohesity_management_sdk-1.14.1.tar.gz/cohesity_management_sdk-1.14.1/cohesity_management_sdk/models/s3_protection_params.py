# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class S3ProtectionParams(object):

    """Implementation of the 'S3ProtectionParams' model.

    Specifies the inventory report params required for s3 backups.

    Attributes:
        s3_inventory_report_bucket (string): ARN of the inventory report
            destination bucket for S3 backups.
            This is required for s3 backups.
        s3_inventory_report_bucket_prefix (string): Specifies the creation time
            of the entity.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "s3_inventory_report_bucket": 's3InventoryReportBucket',
        "s3_inventory_report_bucket_prefix": 's3InventoryReportBucketPrefix'
    }

    def __init__(self,
                 s3_inventory_report_bucket=None,
                 s3_inventory_report_bucket_prefix=None):
        """Constructor for the S3ProtectionParams class"""

        # Initialize members of the class
        self.s3_inventory_report_bucket = s3_inventory_report_bucket
        self.s3_inventory_report_bucket_prefix = s3_inventory_report_bucket_prefix


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
        s3_inventory_report_bucket = dictionary.get('s3InventoryReportBucket', None)
        s3_inventory_report_bucket_prefix = dictionary.get('s3InventoryReportBucketPrefix', None)

        # Return an object of this model
        return cls(s3_inventory_report_bucket,
                   s3_inventory_report_bucket_prefix)


