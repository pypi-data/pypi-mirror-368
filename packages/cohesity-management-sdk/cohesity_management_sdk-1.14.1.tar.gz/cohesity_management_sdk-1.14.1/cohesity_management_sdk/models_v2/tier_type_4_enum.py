# -*- coding: utf-8 -*-

class TierType4Enum(object):

    """Implementation of the 'Name' enum.

    Specifies the sku tier selection for azure sql databases and
          by default HS_Gen5 is selected. The tiers must match their sku name selected.

    Attributes:
        GENERALPURPOSE: TODO: type description here.
        BUSINESSCRITICAL: TODO: type description here.
        HYPERSCALE: TODO: type description here.
        BASIC: TODO: type description here.
        STANDARD: TODO: type description here.
        PREMIUM: TODO: type description here.
        DATAWAREHOUSE: TODO: type description here.
        STRETCH: TODO: type description here.
    """

    GENERALPURPOSE = 'GeneralPurpose'

    BUSINESSCRITICAL = 'BusinessCritical'

    HYPERSCALE = 'HyperScale'

    BASIC = 'Basic'

    STANDARD = 'Standard'

    PREMIUM = 'Premium'

    DATAWAREHOUSE = 'DataWarehouse'

    STRETCH = 'Stretch'