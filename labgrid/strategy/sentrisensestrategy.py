import enum

import attr

from ..factory import target_factory
from ..step import step
from .common import Strategy, StrategyError


class Status(enum.Enum):
    unknown = 0
    off = 1
    on = 2
    charger_1 = 3
    charger_2 = 4
    charger_3 = 5
    charger_4 = 6
    charger_usb = 7
    charger_all = 8


@target_factory.reg_driver
@attr.s(eq=False)
class SentrisenseStrategy(Strategy):
    bindings = {
        "power": "PowerProtocol",
        "charger1": "PowerProtocol",
        "charger2": "PowerProtocol",
        "charger3": "PowerProtocol",
        "charger4": "PowerProtocol",
        "chargerusb": "PowerProtocol",
        "esptool": "EsptoolDriver",
    }

    status = attr.ib(default=Status.unknown)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

    @step(args=['status'])
    def transition(self, status, *, step):  # pylint: disable=redefined-outer-name
        self.target.activate(self.charger1)
        self.target.activate(self.charger2)
        self.target.activate(self.charger3)
        self.target.activate(self.charger4)
        self.target.activate(self.chargerusb)
        self.target.activate(self.power)
        if not isinstance(status, Status):
            status = Status[status]
        if status == Status.unknown:
            raise StrategyError(f"can not transition to {status}")
        elif status == self.status:
            step.skip("nothing to do")
            return  # nothing to do
        elif status == Status.off:
            self.charger1.off()
            self.charger2.off()
            self.charger3.off()
            self.charger4.off()
            self.chargerusb.off()
            self.power.off()
        elif status == Status.on:
            self.charger1.off()
            self.charger2.off()
            self.charger3.off()
            self.charger4.off()
            self.chargerusb.off()
            self.power.on()
        elif status == Status.charger_1:
            self.charger1.on()
            self.charger2.off()
            self.charger3.off()
            self.charger4.off()
            self.chargerusb.off()
            self.power.on()
        elif status == Status.charger_2:
            self.charger1.off()
            self.charger2.on()
            self.charger3.off()
            self.charger4.off()
            self.chargerusb.off()
            self.power.on()
        elif status == Status.charger_3:
            self.charger1.off()
            self.charger2.off()
            self.charger3.on()
            self.charger4.off()
            self.chargerusb.off()
            self.power.on()
        elif status == Status.charger_4:
            self.charger1.off()
            self.charger2.off()
            self.charger3.off()
            self.charger4.on()
            self.chargerusb.off()
            self.power.on()
        elif status == Status.charger_usb:
            self.charger1.off()
            self.charger2.off()
            self.charger3.off()
            self.charger4.off()
            self.chargerusb.on()
            self.power.on()
        elif status == Status.charger_all:
            self.charger1.on()
            self.charger2.on()
            self.charger3.on()
            self.charger4.on()
            self.chargerusb.on()
            self.power.on()
        else:
            raise StrategyError(
                f"no transition found from {self.status} to {status}"
            )
        self.status = status
