# -*- coding: utf-8 -*-


class AWSTags(object):

    """Implementation of the 'AWSTags' model.

    Specifies the AWS tags.

    Attributes:
        vm_tag_ids (list of long|int): Array of Arrays of VMs Tags Ids that
            Specify VMs to Protect. Optionally specify a list of VMs to
            protect by listing Protection Source ids of VM Tags in this two
            dimensional array. Using this two dimensional array of Tag ids,
            the Cluster generates a list of VMs to protect which are derived
            from intersections of the inner arrays and union of the outer
            array, as shown by the following example. To protect only 'Eng'
            VMs in the East and all the VMs in the West, specify the following
            tag id array: [ [1101, 2221], [3031] ], where 1101 is the 'Eng' VM
            Tag id, 2221 is the 'East' VM Tag id and 3031 is the 'West' VM Tag
            id. The inner array [1101, 2221] produces a list of VMs that are
            both tagged with 'Eng' and 'East' (an intersection). The outer
            array combines the list from the inner array with list of VMs
            tagged with 'West' (a union). The list of resulting VMs are
            protected by this Protection Group.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "vm_tag_ids":'vmTagIds'
    }

    def __init__(self,
                 vm_tag_ids=None):
        """Constructor for the AWSTags class"""

        # Initialize members of the class
        self.vm_tag_ids = vm_tag_ids


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
        vm_tag_ids = dictionary.get('vmTagIds')

        # Return an object of this model
        return cls(vm_tag_ids)


