# -*- coding: utf-8 -*-


class GCPDiskExclusionParams(object):

    """Implementation of the 'GCPDiskExclusionParams' model.

    Specifies the paramaters to exclude disks attached to GCP VM instances
      and exclude VMs without disks.

    Attributes:
        exclude_vm_with_no_disk (bool): Specifies the paramaters to exclude VM without disks.
        raw_query (string): Raw boolean query given as input by the user to exclude disk.
          User can input params in raw query form: (<> AND <> AND <> ..) OR (<> AND
          <> AND <> ..) OR (..) OR (..) OR .. There cannot be an OR operator inside
          the bracket. Example query: (K1 = V1 AND K2 = V2 AND K3 != V3) OR (K4 =
          V4 AND K6 != V6).

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "exclude_vm_with_no_disk":'excludeVmWithNoDisk',
        "raw_query":'rawQuery'
    }

    def __init__(self,
                 exclude_vm_with_no_disk=None,
                 raw_query=None):
        """Constructor for the GCPDiskExclusionParams class"""

        # Initialize members of the class
        self.exclude_vm_with_no_disk = exclude_vm_with_no_disk
        self.raw_query = raw_query


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
        exclude_vm_with_no_disk = dictionary.get('excludeVmWithNoDisk')
        raw_query = dictionary.get('rawQuery')

        # Return an object of this model
        return cls(exclude_vm_with_no_disk,
                   raw_query)