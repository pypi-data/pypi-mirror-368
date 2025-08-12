from typing import List, TypeVar

from pamqp.common import Arguments
from pamqp.constants import DEFAULT_PORT

from .base_device_manager import RabbitMQBaseInputDeviceManager
from .device_manager import RabbitMQDeviceManager
from .input_consume_device import RabbitMQInputConsumeDevice

T = TypeVar('T')


class RabbitMQConsumeInputDeviceManager(
    RabbitMQDeviceManager,
    RabbitMQBaseInputDeviceManager,
):
    def __init__(
        self,
        hosts: List[str],
        user: str,
        password: str,
        vhost: str,
        prefetch_count: int,
        consumer_arguments: Arguments = None,
        use_transaction: bool = True,
        use_ssl: bool = True,
        port: int = None,
    ):
        super().__init__(
            hosts=hosts,
            user=user,
            password=password,
            vhost=vhost,
            publisher_confirms=True,
            channel_qos_kwargs=dict(prefetch_count=prefetch_count),
            use_transaction=use_transaction,
            use_ssl=use_ssl,
            port=port,
        )
        self._consumer_arguments = consumer_arguments

    async def get_device(
        self,
        device_name: str,
    ) -> RabbitMQInputConsumeDevice:
        return RabbitMQInputConsumeDevice(
            self,
            device_name,
            self._use_transaction,
            self._consumer_arguments,
        )
