from typing import Dict

from brokers.base_broker import BaseBroker
from brokers.ibkr_broker import IBKRBroker
from brokers.moomoo_futu_broker import MooMooFutuBroker
from brokers.schwab_broker import SchwabBroker
from brokers.webull_broker import WebullBroker


class BrokerFactory:
    _brokers: Dict[str, BaseBroker] = {}

    @classmethod
    def get_broker(cls, broker_name: str) -> BaseBroker:
        if broker_name not in cls._brokers:
            broker = cls._create_broker(broker_name)
            cls._brokers[broker_name] = broker
        return cls._brokers[broker_name]

    @classmethod
    def _create_broker(cls, broker_name: str) -> BaseBroker:
        broker_map = {
            'IBKR': IBKRBroker,
            'WEBULL': WebullBroker,
            'MooMoo': MooMooFutuBroker,
            'Futu': MooMooFutuBroker,
            'SCHWAB': SchwabBroker,  # Add Schwab to the broker map
        }

        if broker_name not in broker_map:
            raise ValueError(f"Unsupported broker: {broker_name}")

        return broker_map[broker_name]()
