import socket
from collections.abc import Generator
from typing import Union

from pyappleinternal.exceptions import NotificationTimeoutError
from pyappleinternal.lockdown_service_provider import LockdownServiceProvider
from pyappleinternal.remote.remote_service_discovery import RemoteServiceDiscoveryService
from pyappleinternal.services.lockdown_service import LockdownService


class NotificationProxyService(LockdownService):
    SERVICE_NAME = 'com.apple.mobile.notification_proxy'
    RSD_SERVICE_NAME = 'com.apple.mobile.notification_proxy.shim.remote'

    INSECURE_SERVICE_NAME = 'com.apple.mobile.insecure_notification_proxy'
    RSD_INSECURE_SERVICE_NAME = 'com.apple.mobile.insecure_notification_proxy.shim.remote'

    def __init__(self, lockdown: LockdownServiceProvider, insecure=False, timeout: Union[float, int] = None):
        if isinstance(lockdown, RemoteServiceDiscoveryService):
            secure_service_name = self.RSD_SERVICE_NAME
            insecure_service_name = self.RSD_INSECURE_SERVICE_NAME
        else:
            secure_service_name = self.SERVICE_NAME
            insecure_service_name = self.INSECURE_SERVICE_NAME

        if insecure:
            super().__init__(lockdown, insecure_service_name)
        else:
            super().__init__(lockdown, secure_service_name)

        if timeout is not None:
            self.service.socket.settimeout(timeout)

    def notify_post(self, name: str) -> None:
        """ Send notification to the device's notification_proxy. """
        self.service.send_plist({'Command': 'PostNotification', 'Name': name})

    def notify_register_dispatch(self, name: str) -> None:
        """ Tells the device to send a notification on the specified event. """
        self.logger.info(f'Observing {name}')
        self.service.send_plist({'Command': 'ObserveNotification', 'Name': name})

    def receive_notification(self) -> Generator[dict, None, None]:
        while True:
            try:
                yield self.service.recv_plist()
            except socket.timeout as e:
                raise NotificationTimeoutError from e
