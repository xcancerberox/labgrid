import attr

from ..factory import target_factory
from ..step import step
from .common import Driver

from ..util.helper import processwrapper

import esptool


@target_factory.reg_driver
@attr.s(eq=False)
class EsptoolDriver(Driver):
    bindings = {
        "tty": {
            "USBSerialPort",
        },
    }
    bindir = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(str)),
    )
    args = attr.ib(
        default=attr.Factory(list),
        validator=attr.validators.optional(attr.validators.instance_of(list)),
    )

    @Driver.check_active
    def get_board_id(self):
        esp = esptool.detect_chip(self.tty.port)
        mac = esp.read_mac()
        return "".join([str(octet) for octet in mac[1:]])

    def base_command(self):
        port = self.tty.port
        return ["esptool.py",
                "-p",
                f"{port}",
                "-b",
                "460800",
                "--before",
                "default_reset",
                "--after",
                "hard_reset",
                "--chip",
                "esp32s2"]

    @Driver.check_active
    @step(args=["bindir"])
    def flash(self, bindir, args=None):
        cmd = self.base_command()
        cmd += ["write_flash",
                "--flash_mode",
                "dio",
                "--flash_size",
                "detect",
                "--flash_freq",
                "40m",
                "0x1000",
                f"{bindir}/bootloader.bin",
                "0x8000",
                f"{bindir}/partition-table.bin",
                "0x10000",
                f"{bindir}/main.bin"]
        processwrapper.check_output(
            cmd, print_on_silent_log=False
        )

    @Driver.check_active
    def erase_flash(self):
        cmd = self.base_command() + ["erase_flash"]
        processwrapper.check_output(
            cmd, print_on_silent_log=False
        )
