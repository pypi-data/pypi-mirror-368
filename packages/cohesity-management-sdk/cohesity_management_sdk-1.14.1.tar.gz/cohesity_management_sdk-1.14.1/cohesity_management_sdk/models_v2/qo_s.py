# -*- coding: utf-8 -*-


class QoS(object):

    """Implementation of the 'QoS.' model.

    Specifies the Quality of Service (QoS) Policy for the View.

    Attributes:
        name (NameEnum): Specifies the name of the QoS Policy. If not specified,
          the default is ''BackupTargetLow''.
          BackupTargetAuto: (Applicable only for C6K Platform) Use this policy
          for workloads such as backups, which keep many I/Os outstanding.
          This policy splits I/Os across SSDs and HDDs to achieve maximum
          performance based on the current usage.
          The priority for processing workload with this policy is the same as
          Backup Target High and Backup Target SSD.
          JournaledSequentialDump: Use this policy for workloads that write
          large amounts of data sequentially to a very small number of files
          and do not keep many I/Os outstanding. By default data is written to
          the SSD and has the highest priority and low latency.
          TestAndDevHigh: Use this policy for workloads that require lower I/O
          latency or do not keep many I/Os outstanding, as the I/Os are given
          higher priority compared to other QoS policies.
          Data is written to the SSD.
          TestAndDevLow: The same as TestAndDev High, except that the I/Os with
          this QoS policy are given lower priority
          compared to I/Os with TestAndDev High when there is contention.
          BackupTargetCommvault: Use this policy to intelligently detect and
          exclude application-specific markers to achieve better deduplication
          when CommVault backup application is writing to a Cohesity View.
          Data is written to SSD and has the same priority and latency as
          TestAndDev High.
          BackupTargetSSD: Use this policy for workloads such as backups,
          which keep many I/Os outstanding, but in this case,
          DataPlatform sends both sequential and random I/Os to SSD.
          The latency is lower than other Backup Target policies.
          The priority for processing workload with this policy
          is the same as Backup Target Auto.
          BackupTargetHigh: Use this policy for non-latency sensitive workloads
          such as backups, which keep many I/Os outstanding.
          Data is written to HDD and has higher latency compared to other QoS
          policies writing to a SSD The priority for processing workload with
          this policy is the same as Backup Target Auto.
          BackupTargetLow: The same as Backup Target High, except that the
          priority for processing workloads with this policy is lower than
          workloads with Backup Target Auto / High /SSD
          when there is contention.
        principal_id (long|int): Specifies the name of the QoS Policy used for
            the View.
        principal_name (string): Specifies the name of the QoS Policy used for
            the View such as 'TestAndDev High', 'Backup Target SSD', 'Backup
            Target High' 'TestAndDev Low' and 'Backup Target Low'. For a
            complete list and descriptions, see the 'Create or Edit Views'
            topic in the documentation. If not specified, the default is
            'Backup Target Low'.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "principal_id":'principalId',
        "principal_name":'principalName'
    }

    def __init__(self,
                 name=None,
                 principal_id=None,
                 principal_name=None):
        """Constructor for the QoS class"""

        # Initialize members of the class
        self.name = name
        self.principal_id = principal_id
        self.principal_name = principal_name


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
        principal_id = dictionary.get('principalId')
        principal_name = dictionary.get('principalName')

        # Return an object of this model
        return cls(name,
                   principal_id,
                   principal_name)