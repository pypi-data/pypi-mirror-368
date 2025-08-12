# -*- coding: utf-8 -*-

class IoFilterStatusEnum(object):

    """Implementation of the 'IoFilterStatus' enum.

    Specifies the state of CDP IO filter. CDP IO filter is an agent which will
    be installed on the object for performing continious backup. <br> 1.
    'kNotInstalled' specifies that CDP is enabled on this object but filter is
    not installed. <br> 2. 'kInstallFilterInProgress' specifies that IO filter
    installation is triggered and in progress. <br> 3.
    'kFilterInstalledIOInactive' specifies that IO filter is installed but IO
    streaming is disabled due to missing backup or explicitly disabled by the
    user. <br> 4. 'kIOActivationInProgress' specifies that IO filter is
    activated to start streaming. <br> 5. 'kIOActive' specifies that filter is
    attached to theeee object and started streaming. <br> 6.
    'kIODeactivationInProgress' specifies that deactivattion has been
    initiated to stop the IO streaming. <br> 7. 'kUninstallFilterInProgress'
    specifies that uninstallation of IO filter is in progress.

    Attributes:
        NOTINSTALLED: TODO: type description here.
        INSTALLFILTERINPROGRESS: TODO: type description here.
        FILTERINSTALLEDIOINACTIVE: TODO: type description here.
        IOINACTIVE: TODO: type description here.
        IOACTIVATIONINPROGRESS: TODO: type description here.
        IOACTIVE: TODO: type description here.
        IODEACTIVATIONINPROGRESS: TODO: type description here.
        UNINSTALLFILTERINPROGRESS: TODO: type description here.
        UPGRADEFILTERINPROGRESS: TODO: type description here.
        UPGRADEFILTERFAILED: TODO: type description here.
        WAITINGFORCDPPOLICYATTACH: TODO: type description here.

    """

    NOTINSTALLED = 'NotInstalled'

    INSTALLFILTERINPROGRESS = 'InstallFilterInProgress'

    FILTERINSTALLEDIOINACTIVE = 'FilterInstalledIOInactive'

    IOINACTIVE = 'IOInactive'

    IOACTIVATIONINPROGRESS = 'IOActivationInProgress'

    IOACTIVE = 'IOActive'

    IODEACTIVATIONINPROGRESS = 'IODeactivationInProgress'

    UNINSTALLFILTERINPROGRESS = 'UninstallFilterInProgress'

    UPGRADEFILTERINPROGRESS = 'UpgradeFilterInProgress'

    UPGRADEFILTERFAILED = 'UpgradeFilterFailed'

    WAITINGFORCDPPOLICYATTACH = 'WaitingForCDPPolicyAttach'