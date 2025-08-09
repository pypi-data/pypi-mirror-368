#  Copyright Femtosense 2025
#
#  By using this software package, you agree to abide by the terms and conditions
#  in the license agreement found at https://femtosense.ai/legal/eula/
#

"""
Evk2Plugin : IOPlugin, helps SPURunner talk to the EVK2 board

"""
try:
    import hid  # https://pypi.org/project/hid/ https://trezor.github.io/cython-hidapi
except ImportError as e:
    print(
        f"Could not import hid. Did you install libhidapi-hidraw0 and libhidapi-libusb0 on Linux or\n"
        + f"on mac brew install libusb hidapi and then export DYLD_LIBRARY_PATH=/opt/homebrew/lib \n{e}"
    )

import numpy as np
from typing_extensions import Self, override

try:
    from femtobehav import cfg
except ImportError:
    from femtodriver import cfg  # fall back to 1.2 config (eval systems)

import logging

from femtodriver.plugins.io_plugin import *
from femtodriver.typing_help import *

logger = logging.getLogger(__name__)

EVK2_VID = 0x16C0
EVK2_PID = 0x0486
EVK2_INTERFACE = 0
QUEUE_SIZE = 50
USB_PACKET_LEN = 64
USB_DATA_LEN = 14

COMMANDS = {
    "ack": 0,
    "reset": 1,
    "interrupt": 2,
    "apb_write": 3,
    "apb_read": 4,
    "axis_write": 5,
    "axis_write_end": 6,
    "axis_read_start": 7,
    "axis_read": 8,
    "register_write": 9,
    "register_read": 10,
    "error": 11,
    "timeout": 12,
    "invalid": 255,
}
CODE_TO_COMMANDS = {v: k for k, v in COMMANDS.items()}

# TODO: fix this redundancy
MSG_CODES = {
    "apb_read": "apb_read",
    "apb_write": "apb_write",
    "axis_read": "axis_read",
    "axis_write": "axis_write",
    "spu_top_read": "register_read",
    "spu_top_write": "register_write",  # not implemented
    "host_write": "reset",  # not implemented
}


class UsbPacket:
    """
    Class describing an exchange of SpuVectors sequence with SPU

    Attributes:
        command (int): command id of the packet (see COMMANDS)
        address (int): address in SPU-001 memory of the data stored in the packet
        data (list(int)): data stored int packet
        length (int): number of values stored in the packet's data field
    """

    def __init__(
        self,
        command: int = COMMANDS["invalid"],
        address: int = 0,
        data: list[int] | None = None,
        length: int = 0,
    ) -> None:
        """
        Initializes a new UsbPacket object

        Args:
            command (int): command id of the packet (see COMMANDS)
            address (int): address in SPU-001 memory of the data stored in the packet
            data (list(int)): data stored int packet
            length (int): number of values stored in the packet's data field
        Returns:
            None
        """

        self.command: int = command
        self.address: int = address
        self.data: list[int] = data if data is not None else []
        self.length: int = min(max(len(self.data), length), USB_DATA_LEN)

    @override
    def __str__(self) -> str:
        return f"{CODE_TO_COMMANDS[self.command]}: @{hex(self.address)} [{self.length}] {[hex(d) for d in self.data]}"

    def serialize(self) -> bytes:
        """
        Serializes the UsbPacket

        Args:
            None
        Returns:
            bytearray: object serialized into bytes
        """

        byte_buffer: bytearray = bytearray()

        byte_buffer.extend(
            int.to_bytes(self.command, 1, byteorder="little", signed=False)
        )
        byte_buffer.append(0)  # 1 byte padding
        byte_buffer.extend(
            int.to_bytes(self.length, 2, byteorder="little", signed=False)
        )
        byte_buffer.extend(
            int.to_bytes(self.address, 4, byteorder="little", signed=False)
        )
        for d in self.data:
            byte_buffer.extend(
                int.to_bytes(int(d), 4, byteorder="little", signed=False)
            )
        while len(byte_buffer) < USB_PACKET_LEN:
            byte_buffer.append(0)

        return bytes(byte_buffer)

    @classmethod
    def deserialize(cls, byte_buffer: bytearray) -> Self:
        """
        Deserializes a byte array into a UsbPacket object

        Args:
            byte_buffer (bytearray): byte array containing the UsbPacket serialized data
        Return:
            UsbPacket: deserialized object
        """

        command = int(byte_buffer[0])
        # byte_buffer[1] is padding
        length = int.from_bytes(byte_buffer[2:4], byteorder="little", signed=False)
        address = int.from_bytes(byte_buffer[4:8], byteorder="little", signed=False)
        data: list[int] = np.frombuffer(
            byte_buffer[8 : 8 + length * 4],
            dtype=np.dtype(np.uint32).newbyteorder("<"),
        ).tolist()
        return cls(command=command, address=address, data=data)


class Evk2Plugin(IOPlugin):
    """
    Evk2Plugin is used by HWRunner to send data to and from the board
    provides:
        setup()
        teardown()
        hw_send()
        hw_recv()

    Attributes:
        device (hid.Device): USB HID connection to EVK2
        alive (bool): flag indicating whether the object is running
    """

    def __init__(
        self,
        fake_connection: bool = False,
        fake_hw_recv_vals: ARRAYINT | None = None,
        logfiledir: str = "io_records",
        host: str | None = None,
    ):
        """
        Initializes the Evk2Plugin object

        Args:
            fake _connection (bool): unused
            fake_hw_recv_vals (ARRAYINT): unused
            logfiledir (str): unused
            host (str): unused
        Returns:
            None
        Raises:
            Exception: if EVK2 could not connect
        """

        self.device: hid.Device | None = None
        self.alive: bool = False
        if self.setup():
            super().__init__(logfiledir=logfiledir)
        else:
            raise Exception("No EVK2")

    def __del__(self):
        self.teardown()

    @classmethod
    def _find_device(cls, serial_number: int = 0) -> bytes | None:
        for dev in hid.enumerate(vid=EVK2_VID, pid=EVK2_PID):
            if dev["interface_number"] != EVK2_INTERFACE:
                continue
            if serial_number == 0 or (
                serial_number > 0 and dev["serial_number"] == serial_number
            ):
                return dev["path"]
        return None

    @override
    def setup(self) -> bool:
        """
        Initiates the EVK2 connection

        Args:
            None
        Returns:
            None
        Raises:
            Exception: if the EVK2 was not detected or could not connect
        """
        device_path: bytes | None = self._find_device()
        if device_path is None:
            logger.error("Error: couldn't find any EVK2 ")
            return False

        try:
            self.device = hid.Device(path=device_path)
        except Exception as e:
            logger.error(f"Error: couldn't connect to EVK2 ({e})")
            return False

        self.alive = True
        logger.info(
            f"EVK2 (serial: {self.device.serial} path: {str(device_path)}) connected and ready!"
        )
        return True

    @override
    def teardown(self):
        """
        Cleans up the Evk2Plugin object

        Args:
            None
        Returns:
            None
        """
        if self.alive:
            self.alive = False
            self.device.close()
            logger.info("Closed EVK2")

    def reset(self):
        """
        Sends a request to EVK2 to reset SPU-001

        Args:
            None
        Returns:
            None
        """

        self.hw_send("host", 0, 1, 1, np.zeros((1,), dtype=np.uint32))

    def _read(
        self,
        timeout_ms: int = 1000,
    ) -> tuple[str, int, list[int]]:
        """
        Reads a packet received from EVK2

        Args:
            timeout_ms (int): maximum duration in millisecond before the function returns
        Returns:
            tuple[str, int, list]: packet data as a tuple (command, address, data)
        """
        try:
            rx_buffer: bytearray = bytearray(
                self.device.read(size=USB_PACKET_LEN, timeout=timeout_ms)
            )
        except Exception as e:
            raise IOError(f"EVK2 read failed: {e})")
        if len(rx_buffer) == 0:
            logger.error(f"Timeout waiting for message from EVK2")
            return ("timeout", -1, [])
        packet: UsbPacket = UsbPacket.deserialize(rx_buffer)
        return (CODE_TO_COMMANDS[packet.command], packet.address, packet.data)

    def _write(
        self, command: int, address: int, data: list[int], length: int = 0
    ) -> None:
        """
        Writes a packet to EVK2 and waits for acknowledgment from EVK2

        Args:
            command (int): command id of the packet (see COMMANDS)
            address (int): address in SPU-001 memory of the data stored in the packet
            data (list(int)): data stored int packet
            length (int): number of values stored in the packet's data field
        Returns:
            None
        Raise:
            IOError: the write operation failed
        """
        packet: UsbPacket = UsbPacket(
            command=command, address=address, data=data, length=length
        )
        tx_buffer: bytes = packet.serialize()
        bytes_written: int = self.device.write(tx_buffer)
        if bytes_written != USB_PACKET_LEN:
            raise IOError(
                f"EVK2 write failed: only partial data written ({bytes_written}/{USB_PACKET_LEN})"
            )
        response_command, response_address, _ = self._read()
        if response_command != "ack" or response_address != address:
            raise IOError(
                f"EVK2 write failed - Ack not received: {response_command} (expected {command})"
                + f"@{response_address} (expected @{address}))\nPacket sent: {str(packet)})"
            )

    @classmethod
    def _breakdown_into_packets(
        cls, command: str, address: int, length: int, data: list[int]
    ) -> list[tuple[str, int, int, list[int]]]:
        """
        Breaks down a Femtodriver transaction into USB size packets

        Args:
            command (str): command string description (from COMMANDS)
            address (int): start address of the transaction
            length (int): length of the transaction
            data (list[int]): data of the transaction
        Returns:
            list[(str, int, int, list[int])]: list of packets as tuples (command, address, length, data)
        """
        packets: list[tuple[str, int, int, list[int]]] = []
        transaction_len = length

        while transaction_len > 0:
            packet_len = min(USB_DATA_LEN, transaction_len)
            cmd_suffix = (
                "_end"
                if command == "axis_write" and transaction_len <= USB_DATA_LEN
                else (
                    "_start"
                    if command == "axis_read" and transaction_len == length
                    else ""
                )
            )
            packets.append(
                (
                    f"{command}{cmd_suffix}",
                    address,
                    packet_len,
                    data[:packet_len] if len(data) > 0 else [],
                )
            )
            address += packet_len * 4
            data = data[packet_len:] if len(data) > 0 else []
            transaction_len -= packet_len

        return packets

    @override
    def _hw_send(
        self,
        msgtype: IOTARGET,
        start_addr: int,
        end_addr: int,
        length: int,
        vals: ARRAYU32,
        flush: bool = True,
        comment: str = "",
    ) -> None:
        """
        Writes to EVK2

        Args:
            msgtype (IOTARGET): transaction description (from MSG_CODES)
            start_addr (int): start address of the write transaction
            end_addr (int): end address of the write transaction
            length (int): length of the write transaction
            vals (ARRAYU32): data to write
            flush (bool): unused
            comment (str): unused
        Returns:
            None
        """

        if msgtype + "_write" not in MSG_CODES:
            logger.error("weird message type:", msgtype)
            return

        data: list[int] = vals.tolist()

        """send raw 32b data to the hardware"""
        packets = self._breakdown_into_packets(
            command=MSG_CODES[msgtype + "_write"],
            address=start_addr,
            length=length,
            data=data,
        )

        for cmd, addr, len, data in packets:
            logger.debug(f"{cmd}: @{hex(addr)} [{len}] {[hex(d) for d in data]}")
            self._write(command=COMMANDS[cmd], address=addr, length=len, data=data)

    @override
    def _hw_recv(
        self,
        msgtype: IOTARGET,
        start_addr: int,
        end_addr: int,
        length: int,
        comment: str = "",
    ) -> list[ARRAYU32]:
        """
        Reads from EVK2

        Args:
            msgtype (IOTARGET): transaction description (from MSG_CODES)
            start_addr (int): start address of the transaction
            end_addr (int): end address of the transaction
            length (int): length of the transaction
            comment (str): unused
        Returns:
            list[ARRAYU32]: list of arrays containing the data read from EVK2
        Raises:
            IOError: the read operation failed
        """
        data: list[int] = []
        if msgtype + "_read" not in MSG_CODES:
            logger.error("weird message type:", msgtype)
            return [np.array(data).astype(np.uint32)]

        packets = self._breakdown_into_packets(
            command=MSG_CODES[msgtype + "_read"],
            address=start_addr,
            length=length,
            data=[],
        )

        for cmd, addr, len, _ in packets:
            self._write(command=COMMANDS[cmd], address=addr, length=len, data=[])
            response_command, response_address, response_data = self._read()
            if response_command == cmd and response_address == addr:
                data.extend(response_data)
                logger.debug(
                    f"{cmd}: @{hex(addr)} [{len}] {[hex(d) for d in response_data]}"
                )
            else:
                raise IOError(
                    f"received wrong response: {response_command} (expected {cmd})"
                    + f"@{response_address} (expected @{addr})"
                )

        return [np.array(data).astype(np.uint32)]
