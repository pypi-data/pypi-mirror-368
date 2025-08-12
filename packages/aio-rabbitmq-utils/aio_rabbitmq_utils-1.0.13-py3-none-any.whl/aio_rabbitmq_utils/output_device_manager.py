from typing import Dict, List

from pamqp.constants import DEFAULT_PORT

from .base_device_manager import RabbitMQBaseOutputDeviceManager
from .device_manager import RabbitMQDeviceManager
from .output_device import RabbitMQOutputDevice


class RabbitMQOutputDeviceManager(
    RabbitMQDeviceManager,
    RabbitMQBaseOutputDeviceManager,
):
    def __init__(
        self,
        hosts: List[str],
        user: str,
        password: str,
        vhost: str,
        exchange_name: str,
        publisher_confirms: bool = True,
        channel_qos_kwargs: Dict[str, int | float | bool | None] = None,
        use_transaction: bool = False,
        use_ssl: bool = True,
        port: int = None,
    ):
        super().__init__(
            hosts=hosts,
            user=user,
            password=password,
            vhost=vhost,
            publisher_confirms=publisher_confirms,
            channel_qos_kwargs=channel_qos_kwargs,
            use_transaction=use_transaction,
            use_ssl=use_ssl,
            port=port,
        )
        self._exchange_name = exchange_name

    async def get_device(
        self,
        device_name: str,
    ) -> RabbitMQOutputDevice:
        return RabbitMQOutputDevice(
            self,
            device_name,
            self._exchange_name,
        )
