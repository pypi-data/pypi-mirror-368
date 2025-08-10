__all__ = [
    'pyappleinternalException', 'DeviceVersionNotSupportedError', 'IncorrectModeError',
    'NotTrustedError', 'PairingError', 'NotPairedError', 'CannotStopSessionError',
    'PasswordRequiredError', 'StartServiceError', 'FatalPairingError', 'NoDeviceConnectedError', 'DeviceNotFoundError',
    'TunneldConnectionError', 'ConnectionFailedToUsbmuxdError', 'MuxException', 'InvalidConnectionError',
    'MuxVersionError', 'ArgumentError', 'AfcException', 'AfcFileNotFoundError', 'DvtException', 'DvtDirListError',
    'NotMountedError', 'AlreadyMountedError', 'UnsupportedCommandError', 'ExtractingStackshotError',
    'ConnectionTerminatedError', 'WirError', 'WebInspectorNotEnabledError', 'RemoteAutomationNotEnabledError',
    'ArbitrationError', 'InternalError', 'DeveloperModeIsNotEnabledError', 'DeviceAlreadyInUseError', 'LockdownError',
    'PairingDialogResponsePendingError', 'UserDeniedPairingError', 'InvalidHostIDError', 'SetProhibitedError',
    'MissingValueError', 'PasscodeRequiredError', 'AmfiError', 'DeviceHasPasscodeSetError', 'NotificationTimeoutError',
    'DeveloperModeError', 'ProfileError', 'IRecvError', 'IRecvNoDeviceConnectedError', 'UnrecognizedSelectorError',
    'MessageNotSupportedError', 'InvalidServiceError', 'InspectorEvaluateError',
    'LaunchingApplicationError', 'BadCommandError', 'BadDevError', 'ConnectionFailedError', 'CoreDeviceError',
    'AccessDeniedError', 'RSDRequiredError', 'SysdiagnoseTimeoutError', 'GetProhibitedError',
    'FeatureNotSupportedError', 'OSNotSupportedError', 'DeprecationError', 'NotEnoughDiskSpaceError',
    'CloudConfigurationAlreadyPresentError', 'QuicProtocolNotSupportedError', 'RemotePairingCompletedError',
    'DisableMemoryLimitError',
]

from typing import Optional


class pyappleinternalException(Exception):
    pass


class DeviceVersionNotSupportedError(pyappleinternalException):
    pass


class IncorrectModeError(pyappleinternalException):
    pass


class NotTrustedError(pyappleinternalException):
    pass


class PairingError(pyappleinternalException):
    pass


class NotPairedError(pyappleinternalException):
    pass


class CannotStopSessionError(pyappleinternalException):
    pass


class PasswordRequiredError(PairingError):
    pass


class StartServiceError(pyappleinternalException):
    pass


class FatalPairingError(pyappleinternalException):
    pass


class NoDeviceConnectedError(pyappleinternalException):
    pass


class InterfaceIndexNotFoundError(pyappleinternalException):
    def __init__(self, address: str):
        super().__init__()
        self.address = address


class DeviceNotFoundError(pyappleinternalException):
    def __init__(self, udid: str):
        super().__init__()
        self.udid = udid


class TunneldConnectionError(pyappleinternalException):
    pass


class MuxException(pyappleinternalException):
    pass


class MuxVersionError(MuxException):
    pass


class BadCommandError(MuxException):
    pass


class BadDevError(MuxException):
    pass


class ConnectionFailedError(MuxException):
    pass


class ConnectionFailedToUsbmuxdError(ConnectionFailedError):
    pass


class ArgumentError(pyappleinternalException):
    pass


class AfcException(pyappleinternalException, OSError):
    def __init__(self, message, status):
        OSError.__init__(self, status, message)
        self.status = status


class AfcFileNotFoundError(AfcException):
    pass


class DvtException(pyappleinternalException):
    """ Domain exception for DVT operations. """
    pass


class UnrecognizedSelectorError(DvtException):
    """ Attempted to call an unrecognized selector from DVT. """
    pass


class DvtDirListError(DvtException):
    """ Raise when directory listing fails. """
    pass


class NotMountedError(pyappleinternalException):
    """ Given image for umount wasn't mounted in the first place """
    pass


class AlreadyMountedError(pyappleinternalException):
    """ Given image for mount has already been mounted in the first place """
    pass


class MissingManifestError(pyappleinternalException):
    """ No manifest could be found """
    pass


class UnsupportedCommandError(pyappleinternalException):
    """ Given command isn't supported for this iOS version """
    pass


class ExtractingStackshotError(pyappleinternalException):
    """ Raise when stackshot is not received in the core profile session. """
    pass


class ConnectionTerminatedError(pyappleinternalException):
    """ Raise when a connection is terminated abruptly. """
    pass


class StreamClosedError(ConnectionTerminatedError):
    """ Raise when trying to send a message on a closed stream. """
    pass


class WebInspectorNotEnabledError(pyappleinternalException):
    """ Raise when Web Inspector is not enabled. """
    pass


class RemoteAutomationNotEnabledError(pyappleinternalException):
    """ Raise when Web Inspector remote automation is not enabled. """
    pass


class WirError(pyappleinternalException):
    """ Raise when Webinspector WIR command fails. """
    pass


class InternalError(pyappleinternalException):
    """ Some internal Apple error """
    pass


class ArbitrationError(pyappleinternalException):
    """ Arbitration failed """
    pass


class DeviceAlreadyInUseError(ArbitrationError):
    """ Device is already checked-in by someone """

    @property
    def message(self):
        return self.args[0].get('message')

    @property
    def owner(self):
        return self.args[0].get('owner')

    @property
    def result(self):
        return self.args[0].get('result')


class DeveloperModeIsNotEnabledError(pyappleinternalException):
    """ Raise when mounting failed because developer mode is not enabled. """
    pass


class DeveloperDiskImageNotFoundError(pyappleinternalException):
    """ Failed to locate the correct DeveloperDiskImage.dmg """
    pass


class DeveloperModeError(pyappleinternalException):
    """ Raise when amfid failed to enable developer mode. """
    pass


class LockdownError(pyappleinternalException):
    """ lockdown general error """

    def __init__(self, message: str, identifier: Optional[str] = None) -> None:
        super().__init__(message)
        self.identifier = identifier


class GetProhibitedError(LockdownError):
    pass


class SetProhibitedError(LockdownError):
    pass


class PairingDialogResponsePendingError(PairingError):
    """ User hasn't yet confirmed the device is trusted """
    pass


class UserDeniedPairingError(PairingError):
    pass


class InvalidHostIDError(PairingError):
    pass


class MissingValueError(LockdownError):
    """ raised when attempting to query non-existent domain/key """
    pass


class InvalidConnectionError(LockdownError):
    pass


class PasscodeRequiredError(LockdownError):
    """ passcode must be present for this action """
    pass


class AmfiError(pyappleinternalException):
    pass


class DeviceHasPasscodeSetError(AmfiError):
    pass


class NotificationTimeoutError(pyappleinternalException, TimeoutError):
    pass


class ProfileError(pyappleinternalException):
    pass


class CloudConfigurationAlreadyPresentError(ProfileError):
    pass


class IRecvError(pyappleinternalException):
    pass


class IRecvNoDeviceConnectedError(IRecvError):
    pass


class MessageNotSupportedError(pyappleinternalException):
    pass


class InvalidServiceError(LockdownError):
    pass


class InspectorEvaluateError(pyappleinternalException):
    def __init__(self, class_name: str, message: str, line: Optional[int] = None, column: Optional[int] = None,
                 stack: Optional[list[str]] = None):
        super().__init__()
        self.class_name = class_name
        self.message = message
        self.line = line
        self.column = column
        self.stack = stack

    def __str__(self) -> str:
        stack_trace = '\n'.join([f'\t - {frame}' for frame in self.stack])
        return (f'{self.class_name}: {self.message}.\n'
                f'Line: {self.line} Column: {self.column}\n'
                f'Stack: {stack_trace}')


class LaunchingApplicationError(pyappleinternalException):
    pass


class AppInstallError(pyappleinternalException):
    pass


class AppNotInstalledError(pyappleinternalException):
    pass


class CoreDeviceError(pyappleinternalException):
    pass


class AccessDeniedError(pyappleinternalException):
    """ Need extra permissions to execute this command """
    pass


class NoSuchBuildIdentityError(pyappleinternalException):
    pass


class MobileActivationException(pyappleinternalException):
    """ Mobile activation can not be done """
    pass


class NotEnoughDiskSpaceError(pyappleinternalException):
    """ Computer does not have enough disk space for the intended operation """
    pass


class DeprecationError(pyappleinternalException):
    """ The requested action/service/method is deprecated """
    pass


class RSDRequiredError(pyappleinternalException):
    """ The requested action requires an RSD object """

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        super().__init__()


class SysdiagnoseTimeoutError(pyappleinternalException, TimeoutError):
    """ Timeout collecting new sysdiagnose archive """
    pass


class SupportError(pyappleinternalException):
    def __init__(self, os_name):
        self.os_name = os_name
        super().__init__()


class OSNotSupportedError(SupportError):
    """ Operating system is not supported. """
    pass


class FeatureNotSupportedError(SupportError):
    """ Feature has not been implemented for OS. """

    def __init__(self, os_name, feature):
        super().__init__(os_name)
        self.feature = feature


class QuicProtocolNotSupportedError(pyappleinternalException):
    """ QUIC tunnel support was removed on iOS 18.2+ """
    pass


class RemotePairingCompletedError(pyappleinternalException):
    """
    Raised upon pairing completion using the `remotepairingdeviced` service (RemoteXPC).

    remotepairingdeviced closes connection after pairing, so client must re-establish it after pairing is
    completed.
    """
    pass


class DisableMemoryLimitError(pyappleinternalException):
    """ Disabling memory limit fails. """
    pass
