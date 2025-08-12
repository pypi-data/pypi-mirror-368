# -*- coding: utf-8 -*-


class EncryptionConfigurationParams(object):

    """Implementation of the 'EncryptionConfigurationParams' model.

    Specifies the parameters the user wants to use when configuring encryption
      for the new Cluster

    Attributes:
        enable_fips_mode (bool): Specifies whether or not to enable FIPS mode
        enable_hardware_encryption (bool): Specifies whether or not to enable hardware encryption
        enable_software_encryption (bool): Specifies whether or not to enable software encryption
        rotation_period (long|int): Specifies the encryption configuration parameters
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "enable_fips_mode":'enableFipsMode',
        "enable_hardware_encryption":'enableHardwareEncryption',
        "enable_software_encryption":'enableSoftwareEncryption',
        "rotation_period":'rotationPeriod'
    }

    def __init__(self,
                 enable_fips_mode=None,
                 enable_hardware_encryption=None,
                 enable_software_encryption=None,
                 rotation_period=None
                 ):
        """Constructor for the EncryptionConfigurationParams class"""

        # Initialize members of the class
        self.enable_fips_mode = enable_fips_mode
        self.enable_hardware_encryption = enable_hardware_encryption
        self.enable_software_encryption = enable_software_encryption
        self.rotation_period = rotation_period


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
        enable_fips_mode = dictionary.get('enableFipsMode')
        enable_hardware_encryption = dictionary.get('enableHardwareEncryption')
        enable_software_encryption = dictionary.get('enableSoftwareEncryption')
        rotation_period = dictionary.get('rotationPeriod')

        # Return an object of this model
        return cls(enable_fips_mode, enable_hardware_encryption, enable_software_encryption, rotation_period)