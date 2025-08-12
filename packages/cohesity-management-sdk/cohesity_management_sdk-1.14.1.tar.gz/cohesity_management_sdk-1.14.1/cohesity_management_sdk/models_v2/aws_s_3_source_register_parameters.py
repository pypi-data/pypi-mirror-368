# -*- coding: utf-8 -*-


class AWS_S3sourceregisterparameters(object):

    """Implementation of the 'AWS_S3sourceregisterparameters' model.

    Specifies the s3 specific parameters for source registration

    Attributes:
        inventory_report_bucket (string): Specifies the ARN for S3 bucket where
            inventory reports are to be stored.
        inventory_report_prefix (string): The inventory bucket prefix where inventory
            reports are to be stored.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "inventory_report_bucket":'inventoryReportBucket',
        "inventory_report_prefix":'inventoryReportPrefix'
    }

    def __init__(self,
                 inventory_report_bucket=None,
                 inventory_report_prefix=None):
        """Constructor for the AWS_S3sourceregisterparameters class"""

        # Initialize members of the class
        self.inventory_report_bucket = inventory_report_bucket
        self.inventory_report_prefix = inventory_report_prefix


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
        inventory_report_bucket = dictionary.get('inventoryReportBucket')
        inventory_report_prefix = dictionary.get('inventoryReportPrefix')

        # Return an object of this model
        return cls(inventory_report_bucket,
                   inventory_report_prefix)