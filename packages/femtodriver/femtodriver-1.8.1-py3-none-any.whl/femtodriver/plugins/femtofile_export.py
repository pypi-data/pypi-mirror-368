#  Copyright Femtosense 2025
#
#  By using this software package, you agree to abide by the terms and conditions
#  in the license agreement found at https://femtosense.ai/legal/eula/
#

from enum import IntEnum, unique
from os import path
import numpy as np
from dataclasses import dataclass
from typing import Any
from typing_extensions import Self
from collections import OrderedDict

SPU001_MAX_FREQ: int = 180
SPU001_NUM_CORES: int = 2
SPU001_BANK_COUNT: dict[str, int] = {
    "DM": 8,
    "TM": 4,
    "SB": 1,
    "RQ": 1,
    "PB": 1,
    "IM": 1,
}
SPU001_BANK_CAPACITY: dict[str, int] = {
    "DM": 0x10000,
    "TM": 0x4000,
    "SB": 0x0200,
    "RQ": 0x0200,
    "PB": 0x0200,
    "IM": 0x8000,
}
SPU001_BANK_START_ADDR: dict[str, int] = {
    "DM": 0x0,
    "TM": 0x80000,
    "SB": 0xC0000,
    "RQ": 0xD0000,
    "PB": 0xE0000,
    "IM": 0xF0000,
}
SPU001_BANK_OFFSET: int = 0x10000
SPU001_MEMORY_START_ADDR: int = 0x00100000
MODEL_EXTENSION: str = ".femto"
FILE_MAGIC: str = "f3mt0"
FILE_FORMAT_VERSION: int = 0x0100
FILE_ENDIANNESS: str = "little"  # "big" or "little"
FILE_CHUNK_SIZE: int = 256  # matching a page in flash memory
# FILE_PAGE_SIZE is the number of u32 in a model page to ensure sizeof(ModelPage)=FILE_CHUNK_SIZE
FILE_PAGE_SIZE: int = 62
NAME_LENGTH_MAX: int = 32
VERSION_LENGTH_MAX: int = 16
FILE_HEADER_SIZE: int = FILE_CHUNK_SIZE
MODEL_CONFIG_SIZE: int = FILE_CHUNK_SIZE
SPU_CONFIG_SIZE: int = FILE_CHUNK_SIZE


@unique
class ModelType(IntEnum):
    """Status supported for SPU memory banks"""

    NONE = 0
    KWS = 1
    SLU = 2
    CLARA = 3
    CUSTOM = 10
    INVALID = 0xFFFF

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def _missing_(cls, value):
        return cls.CUSTOM

    def __str__(self) -> str:
        match self.value:
            case self.KWS:
                return "Keyword spotting"
            case self.SLU:
                return "Spoken Language Understanding"
            case self.CLARA:
                return "Clara AI Noise Reduction"
            case self.CUSTOM:
                return "Custom"
            case _:
                return "Invalid"

    @classmethod
    def str_to_type(cls, type: str):
        match type.upper():
            case "KWS" | "WWD" | "GSC":
                return cls.KWS
            case "SLU":
                return cls.SLU
            case "CLARA" | "AINR":
                return cls.CLARA
            case _:
                return cls.CUSTOM


@unique
class SpuPartNumber(IntEnum):
    """Supported SPU part numbers"""

    SPU001 = 1
    UNKNOWN = 255

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN

    def __str__(self) -> str:
        if not self.has_value(self.value):
            return "SPU part number unknown"
        return self.name

    @classmethod
    def str_to_pn(cls, pn: str):
        match pn.upper():
            case "SPU001":
                return cls.SPU001
            case _:
                return cls.UNKNOWN


@unique
class CoreStatus(IntEnum):
    """SPU core status"""

    OFF = 0
    ON = 1
    SLEEPING = 2
    INVALID = 255

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def _missing_(cls, value):
        return cls.INVALID

    def __str__(self) -> str:
        if not self.has_value(self.value):
            return "SPU core status invalid"
        return self.name


@unique
class SpuVectorPrecision(IntEnum):
    """Vector types supported by SPU"""

    I8 = 8
    I16 = 16
    INVALID = 255

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def _missing_(cls, value):
        return cls.INVALID

    def __str__(self) -> str:
        if not self.has_value(self.value):
            return "Vector precision invalid"
        return self.name

    @classmethod
    def to_vector_precision(cls, vec_precision: Any):
        if isinstance(vec_precision, str):
            match vec_precision.lower():
                case "i8" | "single" | "std":
                    return cls.I8
                case "i16" | "double" | "dbl":
                    return cls.I16
                case _:
                    return cls.INVALID
        elif isinstance(vec_precision, int):
            return cls(vec_precision)
        else:
            return cls.INVALID


@unique
class SpuVectorType(IntEnum):
    """Vector types supported by SPU"""

    INPUT = 0
    OUTPUT = 1
    COMMAND = 2
    INVALID = 255

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def _missing_(cls, value):
        return cls.INVALID

    def __str__(self) -> str:
        if not self.has_value(self.value):
            return "Vector type invalid"
        return self.name

    @classmethod
    def to_vector_type(cls, vec_type: Any):
        if isinstance(vec_type, str):
            match vec_type.lower():
                case "input":
                    return cls.INPUT
                case "output":
                    return cls.OUTPUT
                case "command":
                    return cls.COMMAND
                case _:
                    return cls.INVALID
        elif isinstance(vec_type, int):
            return cls(vec_type)
        else:
            return cls.INVALID


@unique
class MemoryState(IntEnum):
    """Model types supported by SPU"""

    OFF = 0
    DISABLED = 1
    SLEEPING = 2
    TRANSITIONING = 3
    ON = 4
    FSM = 5
    INVALID = 255

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def _missing_(cls, value):
        return cls.INVALID

    @classmethod
    def inactive_states(cls) -> list:
        return [MemoryState.DISABLED, MemoryState.INVALID, MemoryState.OFF]

    def __str__(self) -> str:
        if not self.has_value(self.value):
            return "Memory status invalid"
        return self.name


@unique
class MemoryType(IntEnum):
    """SPU001 memory bank types"""

    DM = 0
    TM = 0x20
    IM = 0x30
    SB = 0x40
    RQ = 0x50
    PB = 0x60
    INVALID = 255

    @classmethod
    def has_value(cls, value) -> bool:
        return value in cls._value2member_map_

    @classmethod
    def _missing_(cls, value):
        return cls.INVALID

    @classmethod
    def str_to_type(cls, type: str):
        match type.upper():
            case "DM":
                return cls.DM
            case "TM":
                return cls.TM
            case "SB":
                return cls.SB
            case "RQ":
                return cls.RQ
            case "PB":
                return cls.PB
            case "IM":
                return cls.IM
            case _:
                return cls.INVALID

    def __str__(self) -> str:
        if not self.has_value(self.value):
            return "SPU memory type invalid"
        return self.name

    @classmethod
    def static_memories(cls) -> list:
        return [MemoryType.SB, MemoryType.RQ, MemoryType.PB]


@dataclass
class SpuVector:
    """
    Class representing a data vector to exchange with SPU

    Attributes:
        id (int): vector identifier
        type (SpuVectorType): type of the vector
        target_core_id (int): target core when writing/reading the vector to/from SPU
        precision (SpuVectorPrecision): precision of the vector
        size (int): size of the vector usable data in int16
        padded_size (int): size of the vector payload in int16 including padding
        parameter (int): parameter to provide to SPU when writing the vector, or expected mailbox_id when reading from SPU
    """

    id: int
    type: SpuVectorType
    target_core_id: int
    precision: SpuVectorPrecision
    size: int
    padded_size: int
    parameter: int

    def __init__(
        self,
        id: int,
        vector_type: str,
        target_core_id: int,
        precision: str,
        size: int,
        padded_size: int,
        parameter: int,
    ) -> None:
        """
        Initializes a SpuVector object

        Args:
            id (int): vector identifier
            vector_type (SpuVectorType): type of the vector
            target_core_id (int): target core when writing/reading the vector to/from SPU
            precision (SpuVectorPrecision): precision of the vector
            size (int): size of the vector usable data in int16
            padded_size (int): size of the vector payload in int16 (i.e. padded vector size)
            parameter (int): parameter to provide to SPU when writing the vector, or expected mailbox_id when reading from SPU
        Returns:
            None
        """
        self.id: int = id
        self.type: SpuVectorType = SpuVectorType.to_vector_type(vector_type)
        self.precision: SpuVectorPrecision = SpuVectorPrecision.to_vector_precision(
            precision
        )

        self.target_core_id: int = target_core_id
        self.size: int = size
        self.padded_size: int = padded_size
        self.parameter: int = parameter

        assert self.type != SpuVectorType.INVALID
        assert self.precision != SpuVectorPrecision.INVALID
        assert self.size <= self.padded_size

    def __str__(self):
        return str(
            f"Vector {self.id} ({str(self.type)} {str(self.precision)}) Core {self.target_core_id} "
            f"{'MailboxId' if self.type==SpuVectorType.OUTPUT else 'PC'}: {self.parameter} length: {self.size} ({self.padded_size})"
        )

    def size_in_bytes(self) -> int:
        """
        Provide the size in bytes of the serialized vector

        Args: None
        Return:
            int: the size of the serialized vector in bytes
        """
        return 12

    def serialize(self) -> bytearray:
        """
        Serializes the SpuVector

        Args:
            None
        Returns:
            bytearray: object serialized into bytes
        """
        byte_buffer = bytearray()

        byte_buffer.extend(
            int.to_bytes(self.id, 1, byteorder=FILE_ENDIANNESS, signed=False)
        )
        byte_buffer.extend(
            int.to_bytes(self.type, 1, byteorder=FILE_ENDIANNESS, signed=False)
        )
        byte_buffer.extend(
            int.to_bytes(
                self.target_core_id, 1, byteorder=FILE_ENDIANNESS, signed=False
            )
        )
        byte_buffer.extend(
            int.to_bytes(self.precision, 1, byteorder=FILE_ENDIANNESS, signed=False)
        )
        byte_buffer.extend(
            int.to_bytes(self.size, 2, byteorder=FILE_ENDIANNESS, signed=False)
        )
        byte_buffer.extend(
            int.to_bytes(self.padded_size, 2, byteorder=FILE_ENDIANNESS, signed=False)
        )
        byte_buffer.extend(
            int.to_bytes(self.parameter, 4, byteorder=FILE_ENDIANNESS, signed=False)
        )
        return byte_buffer

    @classmethod
    def deserialize(cls, vector_bytes: bytearray, endianness: str) -> Self:
        """
        Deserializes a byte array into a SpuVector object

        Args:
            vector_bytes (bytearray): byte array containing the vector serialized data
            endianness (str): byte order of the serialized data ("big" or "little")
        Return:
            SpuVector: deserialized vector object
        """
        id = int(vector_bytes[0])
        type = SpuVectorType(int(vector_bytes[1]))
        target_core_id = int(vector_bytes[2])
        precision = SpuVectorPrecision.to_vector_precision(int(vector_bytes[3]))
        size = int.from_bytes(
            vector_bytes[4:6],
            byteorder=endianness,
            signed=False,
        )
        padded_size = int.from_bytes(
            vector_bytes[6:8],
            byteorder=endianness,
            signed=False,
        )
        parameter = int.from_bytes(
            vector_bytes[8:11], byteorder=endianness, signed=False
        )
        return cls(
            id=id,
            vector_type=type,
            target_core_id=target_core_id,
            precision=precision,
            size=size,
            padded_size=padded_size,
            parameter=parameter,
        )


@dataclass
class SpuSequence:
    """
    Class describing an exchange of SpuVectors sequence with SPU

    Attributes:
        id (int): SpuSequence identifier
        input_ids (list(int)): list of the input vector IDs in chronological order
        output_ids (list(int)): list of the outputs vectors IDs in chronological order
    """

    id: int
    input_ids: list[int]
    output_ids: list[int]

    def __init__(
        self, id: int, input_ids: list[int] = None, output_ids: list[int] = None
    ) -> None:
        """
        Initializes a new SpuSequence object

        Args:
            id (int): SpuSequence identifier
            input_ids (list(int)): list of the input vector IDs in chronological order
            output_ids (list(int)): list of the outputs vectors IDs in chronological order
        Returns:
            None
        """
        self.id: int = id
        self.input_ids: list[int] = input_ids if input_ids is not None else []
        self.output_ids: list[int] = output_ids if output_ids is not None else []

    def serialize(self) -> bytearray:
        """
        Serializes the SpuSequence

        Args:
            None
        Returns:
            bytearray: object serialized into bytes
        """
        byte_buffer = bytearray()

        inputs_buffer = bytearray()
        for input in self.input_ids:
            inputs_buffer.extend(
                int.to_bytes(input, 1, byteorder=FILE_ENDIANNESS, signed=False)
            )

        outputs_buffer = bytearray()
        for output in self.output_ids:
            outputs_buffer.extend(
                int.to_bytes(output, 1, byteorder=FILE_ENDIANNESS, signed=False)
            )

        inputs_offset: int = 5
        outputs_offset: int = inputs_offset + len(inputs_buffer)

        byte_buffer.extend(
            int.to_bytes(self.id, 1, byteorder=FILE_ENDIANNESS, signed=False)
        )
        byte_buffer.extend(
            int.to_bytes(
                len(self.input_ids), 1, byteorder=FILE_ENDIANNESS, signed=False
            )
        )
        byte_buffer.extend(
            int.to_bytes(inputs_offset, 1, byteorder=FILE_ENDIANNESS, signed=False)
        )
        byte_buffer.extend(
            int.to_bytes(
                len(self.output_ids), 1, byteorder=FILE_ENDIANNESS, signed=False
            )
        )
        byte_buffer.extend(
            int.to_bytes(outputs_offset, 1, byteorder=FILE_ENDIANNESS, signed=False)
        )

        byte_buffer.extend(inputs_buffer)
        byte_buffer.extend(outputs_buffer)

        return byte_buffer

    @classmethod
    def deserialize(cls, sequence_bytes: bytearray, endianness: str) -> Self:
        """
        Deserializes a byte array into a SpuSequence object

        Args:
            sequence_bytes (bytearray): byte array containing the sequence serialized data
            endianness (str): byte order of the serialized data ("big" or "little")
        Return:
            SpuSequence: deserialized sequence object
        """
        id = int(sequence_bytes[0])
        input_count = int(sequence_bytes[1])
        input_offset = int(sequence_bytes[2])
        output_count = int(sequence_bytes[3])
        output_offset = int(sequence_bytes[4])
        input_ids = np.frombuffer(
            sequence_bytes[input_offset : input_offset + input_count],
            dtype=np.dtype(np.uint8).newbyteorder(
                "<" if endianness == "little" else ">"
            ),
        ).tolist()
        output_ids = np.frombuffer(
            sequence_bytes[output_offset : output_offset + output_count],
            dtype=np.dtype(np.uint8).newbyteorder(
                "<" if endianness == "little" else ">"
            ),
        ).tolist()
        return cls(id=id, input_ids=input_ids, output_ids=output_ids)


@dataclass
class ModelPage:
    """
    Class describing a page of the model. A page contains a subsection of the data store in one of SPU's memory bank

    Attributes:
        id (int): ModelPage identifier
        length (int): number of words (uint32) stored in the ModelPage
        address (int): start address to write the ModelPage in SPU memory
        data (list(int)): list of words (uint32) to be written in SPU memory
    """

    id: int
    length: int
    address: int
    data: list[int]

    def __init__(
        self,
        id: int = -1,
        length: int = 0,
        address: int = 0,
        data: list[int] = None,
    ) -> None:
        """
        Initializes a new ModelPage object

        Args:
            id (int): ModelPage identifier
            length (int): number of words (uint32) stored in the ModelPage
            address (int): start address to write the ModelPage in SPU memory
            data (list(int)): list of words (uint32) to be written in SPU memory
        Returns:
            None
        """
        self.id: int = id
        self.length: int = length
        self.address: int = address
        self.data: list[int] = data if data is not None else []
        assert self.length == len(self.data)

    def serialize(self, chunk_size: int) -> bytearray:
        """
        Serializes the ModelPage

        Args:
            chunk_size (int): size to align the final serialize array
        Returns:
            bytearray: object serialized into bytes
        """
        assert chunk_size > 0
        byte_buffer = bytearray()
        byte_buffer.extend(
            int.to_bytes(self.id, 2, byteorder=FILE_ENDIANNESS, signed=False)
        )
        byte_buffer.extend(
            int.to_bytes(self.length, 2, byteorder=FILE_ENDIANNESS, signed=False)
        )
        byte_buffer.extend(
            int.to_bytes(self.address, 4, byteorder=FILE_ENDIANNESS, signed=False)
        )
        for d in self.data:
            byte_buffer.extend(
                int.to_bytes(int(d), 4, byteorder=FILE_ENDIANNESS, signed=False)
            )
        # Adding padding to reach a multiple of chunk_size
        while len(byte_buffer) % chunk_size != 0:
            byte_buffer.append(0xFF)
        return byte_buffer

    @classmethod
    def deserialize(cls, page_bytes: bytearray, endianness: str) -> Self:
        """
        Deserializes a byte array into a ModelPage object

        Args:
            page_bytes (bytearray): byte array containing the model page serialized data
            endianness (str): byte order of the serialized data ("big" or "little")
        Return:
            ModelPage: object containing all page data
        """
        id = int.from_bytes(
            page_bytes[0:2],
            byteorder=endianness,
            signed=False,
        )
        length = int.from_bytes(
            page_bytes[2:4],
            byteorder=endianness,
            signed=False,
        )
        address = int.from_bytes(
            page_bytes[4:8],
            byteorder=endianness,
            signed=False,
        )
        data = np.frombuffer(
            page_bytes[8 : 8 + length * 4],
            dtype=np.dtype(np.uint32).newbyteorder(
                "<" if endianness == "little" else ">"
            ),
        ).tolist()
        return cls(id=id, length=length, address=address, data=data)


@dataclass
class MemoryBank:
    """
    Class describing an SPU internal memory bank

    Attributes:
        id (int): memory bank identifier
        type (MemoryType): type of memory bank
        state (MemoryState): state of the memory bank
        capacity (int): capacity of the memory bank in bytes
        page_count (int): number of ModelPages constituting the MemoryBank
        start_address (int): address of the first word of the MemoryBank
        data (list[int]): data stored in the memory bank
        pages (list(ModelPage)): list of ModelPages containing the MemoryBank data
    """

    id: int
    type: MemoryType
    state: MemoryState
    capacity: int
    page_count: int
    start_address: int
    data: list[int]
    pages: list[ModelPage]

    def __init__(
        self,
        id: int,
        type: str,
        core_id: int,
        spu_pn: SpuPartNumber,
        state: MemoryState = MemoryState.OFF,
    ) -> None:
        """
        Initializes a new MemoryBank object

        Args:
            id (int): memory bank identifier
            type (MemoryType): type of memory bank
            core_id (int): identifier of the SpuCore in which the MemoryBank resides
            spu_pn (SpuPartNumber): part number of the SPU in which the MemoryBank resides
        Returns:
            None
        """
        self.id: int = id
        self.type: MemoryType = MemoryType.str_to_type(type)
        self.state: MemoryState = state
        self.capacity: int = self.get_memory_capacity(memory_type=type, spu_pn=spu_pn)
        self.page_count: int = 0
        self.start_address: int = self.get_memory_start_address(
            core_id=core_id, spu_pn=spu_pn
        )
        self.data: list[int] = []
        self.pages: list[ModelPage] = []

        assert self.type != MemoryType.INVALID
        assert self.state != MemoryState.INVALID

    def add_data(self, data: list[int]) -> None:
        """
        Adds data to the MemoryBank

        Args:
            data (list[int]): list of words (uint32) divided in arrays setting the page length
        Returns:
            None
        Raises:
            Exception: if the data added exceeds the capacity of the memory bank
        """
        if len(data) == 0:
            return

        self.state = MemoryState.FSM
        self.data.extend(data)

        # Make sure the data stored in the bank actually fits
        content_size = len(self.data) * 4
        if content_size > self.capacity:
            raise Exception(
                f"Trying to store more data than the bank can contain:"
                f"{content_size} bytes in {str(self.type)}{self.id} (capacity: {self.capacity})"
            )

    def is_unused(self) -> bool:
        """
        Indicates whether the MemoryBank is in an inactive state

        Args:
            None
        Returns:
            bool: true if the MemoryBank is inactive, false otherwise
        """
        return self.state in MemoryState.inactive_states()

    def size_in_bytes(self) -> int:
        """
        Provide the size in bytes of the serialized memory bank

        Args: None
        Return:
            int: the size of the serialized memory bank in bytes
        """
        return 2

    def __str__(self):
        return (
            f"{str(self.type)}"
            f"{self.id if self.type in [MemoryType.DM, MemoryType.TM] else ''}"
            f"({str(self.state)}) {round(100.0*len(self.data)*4/self.capacity,1)}% full"
        )

    @staticmethod
    def get_memory_capacity(
        memory_type: str, spu_pn: SpuPartNumber = SpuPartNumber.SPU001
    ) -> int:
        """
        Provides the capacity of a memory bank based on the type of MemoryBank and the SPU part number

        Args:
            memory_type (str): type of the memory
            spu_pn (SpuPartNumber): part number of the SPU in which the MemoryBank resides
        Returns:
            int: capacity of the MemoryBank in bytes
        Raises:
            Exception: if the part number is not supported
            ValueError: if the memory type is invalid
        """
        if spu_pn is not SpuPartNumber.SPU001:
            raise Exception(f"SPU part number not supported: {str(spu_pn)}")

        if memory_type not in SPU001_BANK_CAPACITY.keys():
            raise ValueError(f"Memory type invalid: {memory_type}")

        return SPU001_BANK_CAPACITY[memory_type]

    def get_memory_start_address(self, spu_pn: SpuPartNumber, core_id: int) -> int:
        """
        Prodides the start address of the MemoryBank according to the SPU part number and the core ID

        Args:
            spu_pn (SpuPartNumber): part number of the SPU in which the MemoryBank resides
            core_id (int): identifier of the SpuCore in which the MemoryBank resides
        Returns:
            int: first address of the MemoryBank
        Raises:
            Exception: if the part number is not supported
            ValueError: if the memory type is invalid
        """
        if spu_pn is not SpuPartNumber.SPU001:
            raise Exception(f"SPU part number not supported: {str(spu_pn)}")

        if core_id >= SPU001_NUM_CORES:
            raise ValueError(f"Core ID invalid: {str(core_id)}")

        if str(self.type) not in SPU001_BANK_CAPACITY.keys():
            raise ValueError(f"Memory type invalid: {str(self.type)}")

        return (
            SPU001_MEMORY_START_ADDR * (core_id + 1)
            + SPU001_BANK_START_ADDR[str(self.type)]
            + self.id * SPU001_BANK_OFFSET
        )

    @classmethod
    def get_info_from_address(
        cls, spu_pn: SpuPartNumber, address: int
    ) -> tuple[MemoryType, int]:
        """
        Prodides the type of memory and bank ID from the address provided

        Args:
            spu_pn (SpuPartNumber): part number of the SPU in which the MemoryBank resides
            address (int): address in SPU memory
        Returns:
            tuple[MemoryType, int]: (memory_type, bank_id) corresponding to the address provided
        Raises:
            Exception: if the part number is not supported
            ValueError: if the address is invalid
        """
        if spu_pn is not SpuPartNumber.SPU001:
            raise Exception(f"SPU part number not supported: {str(spu_pn)}")

        # Remove the core offset from the address
        mem_base = address & (SPU001_MEMORY_START_ADDR - 1)
        mem_type: MemoryType = MemoryType.INVALID
        bank_id: int = -1
        # Iterate over all the memory bank types
        for type in MemoryType:
            start_addr: int = SPU001_BANK_START_ADDR[str(type)]
            end_addr: int = (
                start_addr + SPU001_BANK_COUNT[str(type)] * SPU001_BANK_OFFSET
            )
            # Stop if the address base (address-core offset) fits between the start and end addresses
            if start_addr <= mem_base < end_addr:
                mem_type = type
                bank_id = int((mem_base - start_addr) / SPU001_BANK_OFFSET)
                break
        # Raise an error if not type or id was found
        if mem_type == MemoryType.INVALID or bank_id == -1:
            raise ValueError(f"Address invalid: {str(hex(address))}")

        return (mem_type, bank_id)

    @classmethod
    def get_info_from_uid(
        cls, spu_pn: SpuPartNumber, bank_uid: int
    ) -> tuple[MemoryType, int]:
        """
        Prodides the type of memory and bank ID from the bank unique ID

        Args:
            spu_pn (SpuPartNumber): part number of the SPU in which the MemoryBank resides
            bank_ui (int): memory bank unique ID
        Returns:
            tuple[MemoryType, int]: (memory_type, bank_id) corresponding to the address provided
        Raises:
            Exception: if the part number is not supported
            ValueError: if the memory bank unique ID is invalid
        """
        if spu_pn != SpuPartNumber.SPU001:
            raise Exception(f"Part number not supported ({str(spu_pn)})")

        mem_type: MemoryType = MemoryType.INVALID
        bank_id: int = -1
        for type in MemoryType:
            # Reciprocal operation from get_uid_from_info
            bank_id = int((bank_uid - type) / 4)
            # The memory type is valid only if the bank ID is valid
            if 0 <= bank_id < SPU001_BANK_COUNT[str(type)]:
                mem_type = type
                break
        # Raise an error if not type or id was found
        if mem_type == MemoryType.INVALID or bank_id == -1:
            raise ValueError(f"Bank UID {bank_id} doesn't exist")
        return mem_type, bank_id

    def get_uid_from_info(self) -> int:
        """
        Converts the MemoryBank (type, id) into a unique ID

        Args:
            None
        Returns:
            int: unique MemoryBank identifier
        """
        return self.type.value + self.id * 4

    def get_key(self) -> str:
        """
        Converts the MemeoryBank (type, id) into a key string

        Args:
            None
        Returns:
            str: unique MemoryBank key
        """
        return (
            f"{self.type.name}{str(self.id)}"
            if self.type.name in ["DM", "TM"]
            else self.type.name
        )

    def add_pages(self, start_page_id: int, data: list[np.ndarray[np.uint32]]) -> int:
        """
        Adds pages to the MemoryBank

        Args:
            start_page_id (int): identifier of the first ModelPage of the MemoryBank
            data (list(np.ndarrary[np.uint32])): list of words (uint32) divided in arrays setting the page length
        Returns:
            int: the number of pages added to the MemoryBank
        """
        if len(data) == 0:
            return 0

        self.state = MemoryState.FSM
        batch_page_count = 0
        page_address = (
            self.start_address if self.page_count == 0 else self.pages[-1].address + 4
        )
        self.page_count += len(data)
        for page in data:
            model_page = ModelPage(
                id=batch_page_count + start_page_id,
                length=len(page),
                address=page_address,
                data=page,
            )
            batch_page_count += 1
            page_address += len(page) * 4
            self.pages.append(model_page)

        # Make sure the data stored in the bank actually fits
        content_size = sum([page.length * 4 for page in self.pages])
        if content_size > self.capacity:
            raise Exception(
                f"Trying to store more data than the bank can contain:"
                f"{content_size} bytes in {str(self.type)}{self.id} (capacity: {self.capacity})"
            )
        return batch_page_count

    def generate_pages(self, page_size: int, start_page_id: int) -> int:
        """
        Generates pages from the data stored in the memory banks

        Args:
            page_size (int): number of uint32 words per page
            start_page_id (int): identifier of the first page
        Returns:
            int: number of pages created
        """
        return self.add_pages(
            start_page_id=start_page_id,
            data=[
                self.data[x : x + page_size]
                for x in range(0, len(self.data), page_size)
            ],
        )

    def serialize_data(self, chunk_size: int) -> bytearray:
        """
        Serializes the ModelPage data

        Args:
            chunk_size (int): size to align the final serialize array
        Returns:
            bytearray: data serialized into bytes
        """
        byte_buffer = bytearray()
        if self.page_count == 0:
            return bytearray()
        for page in self.pages:
            byte_buffer.extend(page.serialize(chunk_size=chunk_size))
        return byte_buffer

    def serialize_configuration(self) -> bytearray:
        """
        Serializes the MemoryBank configuration

        Args:
            None
        Returns:
            bytearray: configuration serialized into bytes
        """
        byte_buffer = bytearray()

        if self.type in MemoryType.static_memories():
            return byte_buffer

        byte_buffer.extend(
            int.to_bytes(
                self.get_uid_from_info(), 1, byteorder=FILE_ENDIANNESS, signed=False
            )
        )
        byte_buffer.extend(
            int.to_bytes(self.state, 1, byteorder=FILE_ENDIANNESS, signed=False)
        )
        return byte_buffer

    @classmethod
    def deserialize(
        cls, spu_pn: SpuPartNumber, core_id: int, bank_bytes: bytearray
    ) -> Self:
        """
        Deserializes a byte array into a MemoryBank object

        Args:
            bank_bytes (bytearray): byte array containing the memory bank serialized data
        Return:
            MemoryBank: object describing a memory bank
        """
        uid: int = int(bank_bytes[0])
        type, id = cls.get_info_from_uid(spu_pn=spu_pn, bank_uid=uid)
        state: MemoryState = MemoryState(bank_bytes[1])
        return cls(id=id, type=type.name, core_id=core_id, spu_pn=spu_pn, state=state)


@dataclass
class SpuCore:
    """
    Class describing a SpuCore including its configuration and memory content

    Attributes:
        id (int): SpuCore identifier
        status (CoreStatus): status of the SpuCore
        memory_banks (dict[str, MemoryBank]): dictionary containing the MemoryBanks
                                              in a SpuCore given the Spu part number
    """

    id: int
    status: CoreStatus
    memory_banks: dict[str, MemoryBank]

    def __init__(
        self,
        id: int,
        spu_pn: SpuPartNumber,
        status: CoreStatus = CoreStatus.OFF,
        memory_banks: dict[str, MemoryBank] = None,
    ) -> None:
        """
        Creates a new SpuCore object

        Args:
            id (int): SpuCore identifier
            spu_pn (SpuPartNumber): Spu part number
            status (CoreStatus): status of the SpuCore
        Returns:
            None
        """
        self.id: int = id
        self.status: CoreStatus = status
        self.memory_banks: dict[str, MemoryBank] = {}

        if memory_banks is not None:
            assert self.check_memory_banks(
                spu_pn=spu_pn, core_id=id, bank_config=memory_banks
            )
            self.memory_banks: dict[str, MemoryBank] = memory_banks
        else:
            self.memory_banks = self.get_available_memory_banks(
                spu_pn=spu_pn, core_id=id
            )

    def get_specifications(self) -> str:
        """
        Provides the core specifications

        Args:
            None
        Returns:
            str: description of the Spu core as a string
        """
        banks_desc: str = ""

        for bank in self.memory_banks:
            banks_desc += f"\t{ str(self.memory_banks[bank])}\n"
        return f"Core {self.id} ({str(self.status)})\n{banks_desc}"

    def count_banks_to_export(self) -> int:
        num_banks: int = 0

        for bank_key in self.memory_banks:
            if self.memory_banks[bank_key].type not in MemoryType.static_memories():
                num_banks += 1
        return num_banks

    def populate_bank(self, bank_key: str, data: list[int]) -> int:
        """
        Populates the SpuCore's memory bank with the data provided

        Args:
            bank_key (str): key identifying the MemoryBank to store the data in
            start_page_id (int): identifier of the first page
            data (list[int]): list of words to store
        Returns:
            int: the number of pages added to the MemoryBank
        """
        self.memory_banks.get(bank_key).add_data(data)

    def generate_pages(self, page_size: int, start_page_id: int) -> int:
        """
        Generates pages from the data stored in the memory banks

        Args:
            page_size (int): number of uint32 words per page
            start_page_id (int): identifier of the first page
        Returns:
            int: number of pages created
        """
        page_count = start_page_id
        for bank in self.memory_banks:
            page_count += self.memory_banks.get(bank).generate_pages(
                page_size=page_size, start_page_id=page_count
            )

        return page_count

    def serialize_banks(self, chunk_size: int) -> bytearray:
        """
        Serializes all SpuCore's memory banks used

        Args:
            chunk_size (int): size to align the final serialize array
        Returns:
            bytearray:  serialized into bytes
        """
        byte_buffer = bytearray()
        for bank in self.memory_banks:
            byte_buffer.extend(
                self.memory_banks.get(bank).serialize_data(chunk_size=chunk_size)
            )

        return byte_buffer

    def serialize_configuration(self) -> bytearray:
        """
        Serializes the SpuCore's configuration

        Args:
            None
        Returns:
            bytearray: configuration serialized into bytes
        """
        byte_buffer = bytearray()
        banks_offset: int = 4
        byte_buffer.extend(
            int.to_bytes(self.id, 1, byteorder=FILE_ENDIANNESS, signed=False)
        )
        byte_buffer.extend(
            int.to_bytes(self.status, 1, byteorder=FILE_ENDIANNESS, signed=False)
        )
        byte_buffer.extend(
            int.to_bytes(
                self.count_banks_to_export(),
                1,
                byteorder=FILE_ENDIANNESS,
                signed=False,
            )
        )
        byte_buffer.extend(
            int.to_bytes(banks_offset, 1, byteorder=FILE_ENDIANNESS, signed=False)
        )
        for bank in self.memory_banks:
            byte_buffer.extend(self.memory_banks.get(bank).serialize_configuration())

        return byte_buffer

    @staticmethod
    def check_memory_banks(
        spu_pn: SpuPartNumber, core_id: int, bank_config: dict[str, MemoryBank]
    ) -> bool:
        """
        Checks that the memory bank configuration provided is valid given the SPU part number

        Args:
            spu_pn (SpuPartNumber): SPU part number
            core_id (int): core ID where the banks reside
            bank_config (dict[str, MemoryBank]): dictionary containing the number of banks available (value)
                           for each type of MemoryBank (key)
        Returns:
            bool: True if the memory bank configuration is valid, False otherwise
        Raises:
            Exception: if the part number is not supported
        """
        valid_banks: dict[str, MemoryBank] = {}
        match spu_pn:
            case SpuPartNumber.SPU001:
                valid_banks = SpuCore.get_available_memory_banks(
                    spu_pn=spu_pn, core_id=core_id
                )
            case _:
                raise Exception(f"Part number not supported ({str(spu_pn)}")

        for bank_key in bank_config:
            curr_bank = bank_config[bank_key]
            if bank_key not in valid_banks.keys():
                return False
            valid_bank = valid_banks[bank_key]
            if curr_bank.id != valid_bank.id:
                return False
            if curr_bank.type != valid_bank.type:
                return False
            if curr_bank.capacity != valid_bank.capacity:
                return False
            if curr_bank.start_address != valid_bank.start_address:
                return False

        return True

    @staticmethod
    def get_available_memory_banks(
        spu_pn: SpuPartNumber, core_id: int
    ) -> dict[str, MemoryBank]:
        """
        Provides the number of banks available for a given SPU part number

        Args:
            spu_pn (SpuPartNumber): SPU part number
            core_id (int): core ID where the banks reside
        Returns:
            dict[str,int]: dictionary containing the number of banks available (value)
                           for each type of MemoryBank (key)
        Raises:
            Exception: if the part number is not supported
        """
        available_memory_banks: dict[str, MemoryBank] = {}
        match spu_pn:
            case SpuPartNumber.SPU001:
                banks = SPU001_BANK_COUNT
            case _:
                raise Exception(f"Part number not supported ({str(spu_pn)}")

        for memory_type in banks:
            for bank_id in range(0, banks[memory_type]):
                bank_key: str = (
                    f"{memory_type}{bank_id}".upper()
                    if memory_type in ["DM", "TM"]
                    else f"{memory_type}".upper()
                )
                available_memory_banks[bank_key] = MemoryBank(
                    id=bank_id,
                    type=memory_type,
                    core_id=core_id,
                    spu_pn=spu_pn,
                )
        return available_memory_banks

    @classmethod
    def deserialize(cls, spu_pn: SpuPartNumber, core_bytes: bytearray) -> Self:
        """
        Deserializes a byte array into a SpuCore object

        Args:
            spu_pn (SpuPartNumber): part number of the SPU this SpuCore belongs to
            core_bytes (bytearray): byte array containing the SPU configuration serialized data
        Return:
            SpuCore: object describing a SpuCore configuration
        """
        id: int = int(core_bytes[0])
        status: CoreStatus = CoreStatus(core_bytes[1])
        bank_count: int = int(core_bytes[2])
        banks_offset: int = int(core_bytes[3])
        banks: dict[str, int] = cls.get_available_memory_banks(
            spu_pn=spu_pn, core_id=id
        )
        for i in range(bank_count):
            bank = MemoryBank.deserialize(
                spu_pn=spu_pn, core_id=id, bank_bytes=core_bytes[banks_offset:]
            )
            banks[bank.get_key()] = bank
            banks_offset += bank.size_in_bytes()
        return cls(id=id, spu_pn=spu_pn, status=status, memory_banks=banks)


@dataclass
class Spu:
    """
    Class describing the Spu configuration and content

    Attributes:
        part_number (SpuPartNumber): Spu part number
        core_clock_frequency_mhz (int): recommended core clock frequency in MHz
        encryption_key_index (int): index of the encrytion key to use
        cores (list[SpuCore]): list of the cores present in the SPU
    """

    part_number: SpuPartNumber
    core_clock_frequency_mhz: int
    encryption_key_index: int
    cores: list[SpuCore]

    def __init__(
        self,
        part_number: SpuPartNumber,
        core_clock_frequency_mhz: int,
        encryption_key_index: int,
        num_used_cores: int = 0,
        cores: list[SpuCore] = None,
    ) -> None:
        """
        Creates a new Spu object

        Args:
            part_number (SpuPartNumber): Spu part number
            num_used_cores (int): number of SpuCores in use
            core_clock_frequency_mhz (int): recommended core clock frequency in MHz
            encryption_key_index (int): index of the encrytion key to use
            cores (list[SpuCore]): list of cores in the SPU
        Returns:
            None
        """
        self.part_number: SpuPartNumber = part_number
        self.core_clock_frequency_mhz: int = core_clock_frequency_mhz
        self.encryption_key_index: int = encryption_key_index
        if cores is not None:
            assert self.check_cores(spu_pn=part_number, cores=cores)
            self.cores: list[SpuCore] = cores
        else:
            self.cores: list[SpuCore] = self.get_core_list(
                spu_pn=part_number, num_used_cores=num_used_cores
            )

        # variable to help keep track of pages' consecutiveness when calling populate_from_page
        self.last_page_id: int = 0

    def get_specifications(self) -> str:
        """
        Provides the SPU specifications

        Args:
            None
        Returns:
            str: description of the Spu specifications as a string
        """
        cores_desc: str = ""
        for core in self.cores:
            cores_desc += f"{core.get_specifications()}"

        return f"{str(self.part_number)} ({self.core_clock_frequency_mhz}MHz) using encryption key #{self.encryption_key_index}\n{cores_desc}"

    @staticmethod
    def check_cores(spu_pn: SpuPartNumber, cores: list[SpuCore]) -> bool:
        """
        Checks that the list of cores provided is valid given the SPU part number

        Args:
            spu_pn (SpuPartNumber): SPU part number
            cores (list[SpuCore]): list of cores in the SPU

        Returns:
            bool: True if the memory bank configuration is valid, False otherwise
        Raises:
            Exception: if the part number is not supported
        """
        valid_cores: list[SpuCore] = []
        match spu_pn:
            case SpuPartNumber.SPU001:
                valid_cores = Spu.get_core_list(
                    spu_pn=spu_pn, num_used_cores=len(cores)
                )
            case _:
                raise Exception(f"Part number not supported ({str(spu_pn)}")

        for curr_core, valid_core in zip(cores, valid_cores):
            if curr_core.id != valid_core.id:
                return False
        return True

    @classmethod
    def get_core_list(cls, spu_pn: SpuPartNumber, num_used_cores: int) -> list[SpuCore]:
        """
        Generates the list of SpuCores based on the information provided
        Args:
            part_number (SpuPartNumber): Spu part number
            num_used_cores (int): number of SpuCores in use
        Returns:
            list[SpuCore]: list of cores in the SPU
        Raises:
            Exception: if the part number is not supported
        """
        core_list: list[SpuCore] = []
        if spu_pn != SpuPartNumber.SPU001:
            raise Exception(f"Part number not supported ({str(spu_pn)}")

        core_count = SPU001_NUM_CORES

        for core_id in range(num_used_cores):
            core_list.append(SpuCore(id=core_id, spu_pn=spu_pn, status=CoreStatus.ON))
        while len(core_list) < core_count:
            core_list.append(
                SpuCore(id=core_list[-1].id + 1, spu_pn=spu_pn, status=CoreStatus.OFF)
            )

        return core_list

    def validate_configuration(self) -> bool:
        """
        Checks the validity of the Spu against its physical capabitilites

        Args:
            None
        Returns:
            bool: true if the Spu configuration is valid, false otherwise
        Raises:
            Exception: one of the properties is invalid
        """
        match self.part_number:
            case SpuPartNumber.SPU001:
                if self.encryption_key_index < 0 or self.encryption_key_index > 32:
                    raise Exception(
                        f"Invalid encryption key index {self.encryption_key_index}"
                    )
                if len(self.cores) > SPU001_NUM_CORES:
                    raise Exception(
                        f"Invalid number of cores ({len(self.cores)} - MAX={SPU001_NUM_CORES})"
                    )
                if self.core_clock_frequency_mhz > SPU001_MAX_FREQ:
                    raise Exception(
                        f"Invalid core clock frequency ({self.core_clock_frequency_mhz}MHz - MAX={SPU001_MAX_FREQ}MHz)"
                    )
            case _:
                raise Exception(f"Unsupported SPU part number ({self.part_number})")
        return True

    def populate_memory(
        self,
        core_id: int,
        bank_key: str,
        data: list[int],
    ) -> None:
        """
        Populate the SPU memory bank with the data provided

        Args:
            core_id (int): identifier of the core
            bank_key (str): key identifying the MemoryBank to store the data in
            data (list[int]): list of words to store
        Returns:
            None
        """
        assert (
            core_id >= 0
            and core_id < len(self.cores)
            and bank_key in self.cores[core_id].memory_banks.keys()
        )
        self.cores[core_id].populate_bank(bank_key=bank_key, data=data)

    def populate_from_page(self, page: ModelPage) -> None:
        """
        Appends the data stored in the page provided to the coresponding SPU memory.

        Args:
            page (ModelPage): model page to be added to the SPU
        Returns:
            None
        Raises:
            ValueError: the page ID is invalid
            Exception: the SPU part number is not supported
            ValueError: the core ID is invalid
            ValueError: the address of the page provided doesn't exist
        """
        # TODO: replace the class variable with something more appropriate (look at generators)
        if page.id - self.last_page_id > 1:
            raise ValueError(
                f"Page ID invalid: {str(page.id)} (previous page ID: {str(self.last_page_id)})"
                f"Pages must be provided consecutively to ensure the data is correctly order in the memory bank"
            )

        core_id = (page.address >> 20) - 1
        if self.part_number != SpuPartNumber.SPU001:
            raise Exception(f"SPU part number not supported: {str(self.part_number)}")
        elif core_id >= SPU001_NUM_CORES:
            raise ValueError(f"Core ID invalid: {str(core_id)}")

        memory_type, bank_id = MemoryBank.get_info_from_address(
            spu_pn=self.part_number, address=page.address
        )
        if memory_type == MemoryType.INVALID:
            raise ValueError(
                f"Address {hex(page.address)} does not exist in {str(self.part_number)}'s  memory"
            )

        bank_key: str = (
            f"{memory_type}{bank_id}".upper()
            if str(memory_type) in ["DM", "TM"]
            else f"{memory_type}".upper()
        )

        self.cores[core_id].memory_banks[bank_key].add_data(page.data[: page.length])
        self.last_page_id = page.id
        return (core_id, memory_type, bank_id)

    def generate_pages(self, page_size: int) -> int:
        """
        Generates pages from the data stored in the memory banks

        Args:
            page_size (int): number of uint32 words per page
        Returns:
            int: number of pages created
        """
        page_count = 0
        for core in self.cores:
            page_count = core.generate_pages(
                page_size=page_size, start_page_id=page_count
            )
        return page_count

    def serialize_memory(self, chunk_size: int) -> bytearray:
        """
        Serializes the content of all Spu memory banks used

        Args:
            chunk_size (int): size to align the final serialize array
        Returns:
            bytearray: memory serialized into bytes
        """
        byte_buffer = bytearray()
        for core in self.cores:
            byte_buffer.extend(core.serialize_banks(chunk_size=chunk_size))
        return byte_buffer

    def serialize_cores(self) -> bytearray:
        """
        Serializes the Spu cores

        Args:
            None
        Returns:
            bytearray: Spu cores serialized into bytes
        """
        byte_buffer = bytearray()
        cores_bytes = bytearray()
        mapping_table: list[tuple[int, int]] = []

        # each core takes 2 u16 in the mapping table
        core_data_offset: int = 4 * len(self.cores)

        # Serialize each IO sequence and build the mapping table at the same time
        for c in self.cores:
            core_bytes = c.serialize_configuration()
            cores_bytes.extend(core_bytes)
            # reference sequence size in bytes and offset from the beginning of the section
            mapping_table.append((len(core_bytes), core_data_offset))
            # increment the offset with the length of the serialized sequence
            core_data_offset += len(core_bytes)

        # 1. mapping table
        for size, offset in mapping_table:
            byte_buffer.extend(
                int.to_bytes(size, 2, byteorder=FILE_ENDIANNESS, signed=False)
            )
            byte_buffer.extend(
                int.to_bytes(offset, 2, byteorder=FILE_ENDIANNESS, signed=False)
            )
        # 2. sequences data
        byte_buffer.extend(cores_bytes)

        # Add padding to prevent issues related to unaligned section when on device (in particular 32b MCUs)
        while len(byte_buffer) % 4 != 0:
            byte_buffer.append(0xFF)

        return byte_buffer

    @classmethod
    def deserialize_cores(
        cls,
        spu_pn: SpuPartNumber,
        core_count: int,
        cores_bytes: bytearray,
        endianness: str,
    ) -> list[SpuCore]:
        """
        Deserializes the Spu cores

        Args:
            spu_pn (SpuPartNumber): Spu part number
            core_count (int): number of cores to deserialize
            cores_bytes (bytearray): bytes to deserialize
            endianness (str): byte order of the serialized data ("big" or "little")
        Returns:
            list[SpuCore]: list of SpuCore objcects
        """
        # 1. deserialize the mapping table to retrieve the serialized cores
        mapping_table = np.frombuffer(
            cores_bytes[: core_count * 4],
            dtype=np.dtype(np.uint16).newbyteorder(
                "<" if endianness == "little" else ">"
            ),
        ).tolist()
        # 2. deserialize each core
        cores: list[SpuCore] = []
        for i in range(core_count):
            size = mapping_table[2 * i]
            offset = mapping_table[2 * i + 1]
            core = SpuCore.deserialize(
                spu_pn=spu_pn,
                core_bytes=cores_bytes[offset : offset + size],
            )
            if core.status != CoreStatus.INVALID:
                cores.append(core)

        return cores

    def serialize_configuration(self) -> bytearray:
        """
        Serializes the Spu configuration

        Args:
            None
        Returns:
            bytearray: configuration serialized into bytes
        """
        byte_buffer = bytearray()
        cores_offset: int = 6
        byte_buffer.extend(
            int.to_bytes(self.part_number, 1, byteorder=FILE_ENDIANNESS, signed=False)
        )
        byte_buffer.extend(
            int.to_bytes(
                self.encryption_key_index,
                1,
                byteorder=FILE_ENDIANNESS,
                signed=False,
            )
        )
        byte_buffer.extend(
            int.to_bytes(
                self.core_clock_frequency_mhz,
                2,
                byteorder=FILE_ENDIANNESS,
                signed=False,
            )
        )
        byte_buffer.extend(
            int.to_bytes(
                len(self.cores),
                1,
                byteorder=FILE_ENDIANNESS,
                signed=False,
            )
        )
        byte_buffer.extend(
            int.to_bytes(
                cores_offset,
                1,
                byteorder=FILE_ENDIANNESS,
                signed=False,
            )
        )
        byte_buffer.extend(self.serialize_cores())

        # Add padding to prevent issues related to unaligned section when on device (in particular 32b MCUs)
        while len(byte_buffer) % 4 != 0:
            byte_buffer.append(0xFF)

        return byte_buffer

    @classmethod
    def deserialize(cls, spu_bytes: bytearray, endianness: str) -> Self:
        """
        Deserializes a byte array into a Spu object

        Args:
            spu_bytes (bytearray): byte array containing the SPU configuration serialized data
            endianness (str): byte order of the serialized data ("big" or "little")
        Return:
            Spu: object containing all information describing the SPU configuration
        """
        part_number = SpuPartNumber(spu_bytes[0])
        encryption_key_index = int(spu_bytes[1])
        core_clock_frequency_mhz = int.from_bytes(
            spu_bytes[2:4],
            byteorder=endianness,
            signed=False,
        )
        core_count: int = int(spu_bytes[4])
        cores_offset: int = int(spu_bytes[5])
        cores: list[SpuCore] = cls.deserialize_cores(
            spu_pn=part_number,
            core_count=core_count,
            cores_bytes=spu_bytes[cores_offset:],
            endianness=endianness,
        )

        return cls(
            part_number=part_number,
            core_clock_frequency_mhz=core_clock_frequency_mhz,
            encryption_key_index=encryption_key_index,
            cores=cores,
        )


@dataclass
class Model:
    """
    Class describing a SPU Model

    Attributes:
        type (ModelType): type of the Model
        vectors (list[SpuVector]): list of the SpuVectors that can be used to interact with the Model
        io_sequences (list[SpuSequence]): list of the SpuSequences that can be used to interact with the Model
        page_count (int): numbers of pages constituting the model
        spu (Spu): object describing the Spu configuration and content
        userdata (bytearray): custom data to store alongside the model
    """

    type: ModelType
    vectors: list[SpuVector]
    io_sequences: list[SpuSequence]
    page_count: int
    spu: Spu
    userdata: bytearray

    def __init__(
        self,
        type: ModelType,
        target_spu: SpuPartNumber = SpuPartNumber.UNKNOWN,
        num_used_cores: int = 0,
        spu_core_clock_frequency_mhz: int = 0,
        encryption_key_index: int = -1,
        page_count: int = 0,
        spu: Spu = None,
        vectors: list[SpuVector] = None,
        io_sequences: list[SpuSequence] = None,
        userdata: bytearray = None,
    ) -> None:
        """
        Creates a new Model object

        Args:
            type (ModelType): type of the Model
            target_spu (SpuPartNumber): SPU part number for which the Model is intended to run on
            num_used_cores (int): number of SpuCores used by the Model
            spu_core_clock_frequency_mhz (int): recommended SpuCore clock frequency to run the Model
            encryption_key_index (int): index of the key used to encrypt the Model

            page_count (int): number of pages in the model
            spu (Spu): object describing the Spu configuration and content
            vectors (list[SpuVector]): list of the SpuVectors that can be used to interact with the Model
            io_sequences (list[SpuSequence]): list of the SpuSequences that can be used to interact with the Model
            userdata (bytearray): custom data to store alongside the model
        Returns:
            None
        """
        self.type: ModelType = type
        self.vectors: list[SpuVector] = vectors if vectors is not None else []
        self.io_sequences: list[SpuSequence] = (
            io_sequences if io_sequences is not None else []
        )
        self.page_count: int = page_count
        self.spu: Spu = (
            Spu(
                part_number=target_spu,
                num_used_cores=num_used_cores,
                core_clock_frequency_mhz=spu_core_clock_frequency_mhz,
                encryption_key_index=encryption_key_index,
            )
            if not spu
            else spu
        )
        self.userdata = userdata if userdata is not None else bytearray()

    def get_specifications(self) -> str:
        """
        Provides the model specifications

        Args:
            None
        Returns:
            str: description of the model specifications as a string
        """
        io_desc: str = ""
        for sequence in self.io_sequences:
            io_desc += f"Sequence {sequence.id}\nInputs:\n"
            for input_id in sequence.input_ids:
                io_desc += f"\t{str(self.vectors[input_id])}\n"
            io_desc += "Outputs:\n"
            for output_id in sequence.output_ids:
                io_desc += f"\t{str(self.vectors[output_id])}\n"
        return f"Type: {str(self.type)}\nI/O specifications:\n{io_desc}"

    def populate_memory(self, core_id: int, bank_key: str, data: list[int]) -> None:
        """
        Populate the SPU memory bank with the data provided

        Args:
            core_id (int): identifier of the SpuCore where the data should be stored
            bank_key (str): key (concatenation of MemoryBank.type and MemoryBank.id)
                            describing the MemoryBank where the data should be stored
            data (list[int]): list of words to be stored in memory
        Returns:
            None
        """
        self.spu.populate_memory(
            core_id=core_id,
            bank_key=bank_key,
            data=data,
        )

    def serialize_data(self, chunk_size: int) -> bytearray:
        """
        Serializes the Model data

        Args:
            chunk_size (int): size to align the final serialize array
        Returns:
            bytearray: data serialized into bytes
        """
        self.page_count = self.spu.generate_pages(page_size=FILE_PAGE_SIZE)
        return self.spu.serialize_memory(chunk_size=chunk_size)

    def serialize_io_sequences(self) -> bytearray:
        """
        Serializes the I/O sequences

        Args:
            None
        Returns:
            bytearray: I/O sequences serialized into bytes
        """
        byte_buffer = bytearray()
        sequences_bytes = bytearray()
        mapping_table: list[tuple[int, int]] = []
        # each sequence takes 2 u16 in the mapping table
        sequence_data_offset: int = 4 * len(self.io_sequences)

        # Serialize each IO sequence and build the mapping table at the same time
        for seq in self.io_sequences:
            seq_bytes = seq.serialize()
            sequences_bytes.extend(seq_bytes)
            # reference sequence size in bytes and offset from the beginning of the section
            mapping_table.append((len(seq_bytes), sequence_data_offset))
            # increment the offset with the length of the serialized sequence
            sequence_data_offset += len(seq_bytes)

        # 1. mapping table
        for size, offset in mapping_table:
            byte_buffer.extend(
                int.to_bytes(size, 2, byteorder=FILE_ENDIANNESS, signed=False)
            )
            byte_buffer.extend(
                int.to_bytes(offset, 2, byteorder=FILE_ENDIANNESS, signed=False)
            )
        # 2. sequences data
        byte_buffer.extend(sequences_bytes)
        # Add padding to prevent issues related to unaligned section when on device (in particular 32b MCUs)
        while len(byte_buffer) % 4 != 0:
            byte_buffer.append(0xFF)

        return byte_buffer

    @classmethod
    def deserialize_io_sequences(
        cls, sequence_count: int, sequences_bytes: bytearray, endianness: str
    ) -> list[SpuSequence]:
        """
        Deserializes a byte array into a list of SpuSequence objects

        Args:
            sequence_count (int): number of sequences to derserialize
            sequences_bytes (bytearray): byte array containing the I/O sequences serialized data
            endianness (str): byte order of the serialized data ("big" or "little")
        Return:
            list[SpuSequence]: list of I/O sequences objects
        """
        mapping_table = np.frombuffer(
            sequences_bytes[: sequence_count * 4],
            dtype=np.dtype(np.uint16).newbyteorder(
                "<" if endianness == "little" else ">"
            ),
        ).tolist()
        reference_sequences: list[SpuSequence] = []
        for i in range(sequence_count):
            size = mapping_table[2 * i]
            offset = mapping_table[2 * i + 1]
            reference_sequences.append(
                SpuSequence.deserialize(
                    sequence_bytes=sequences_bytes[offset : offset + size],
                    endianness=endianness,
                )
            )
        return reference_sequences

    def serialize_header(self) -> bytearray:
        """
        Serializes the Model header

        Args:
            None
        Returns:
            bytearray: header serialized into bytes
        """
        byte_buffer = bytearray()
        vectors_buffer = bytearray()
        sequences_buffer = self.serialize_io_sequences()

        for vector in self.vectors:
            vectors_buffer.extend(vector.serialize())

        vectors_offset: int = 16
        sequences_offset: int = vectors_offset + len(vectors_buffer)
        userdata_offset: int = sequences_offset + len(sequences_buffer)

        byte_buffer.extend(
            int.to_bytes(self.type, 2, byteorder=FILE_ENDIANNESS, signed=False)
        )
        byte_buffer.extend(
            int.to_bytes(self.page_count, 2, byteorder=FILE_ENDIANNESS, signed=False)
        )
        byte_buffer.extend(
            int.to_bytes(len(self.vectors), 2, byteorder=FILE_ENDIANNESS, signed=False)
        )
        byte_buffer.extend(
            int.to_bytes(vectors_offset, 2, byteorder=FILE_ENDIANNESS, signed=False)
        )
        byte_buffer.extend(
            int.to_bytes(
                len(self.io_sequences), 2, byteorder=FILE_ENDIANNESS, signed=False
            )
        )
        byte_buffer.extend(
            int.to_bytes(sequences_offset, 2, byteorder=FILE_ENDIANNESS, signed=False)
        )
        byte_buffer.extend(
            int.to_bytes(len(self.userdata), 2, byteorder=FILE_ENDIANNESS, signed=False)
        )
        byte_buffer.extend(
            int.to_bytes(userdata_offset, 2, byteorder=FILE_ENDIANNESS, signed=False)
        )
        byte_buffer.extend(vectors_buffer)
        byte_buffer.extend(sequences_buffer)
        byte_buffer.extend(self.userdata)

        # Add padding to prevent issues related to unaligned section when on device (in particular 32b MCUs)
        while len(byte_buffer) % 4 != 0:
            byte_buffer.append(0xFF)

        return byte_buffer

    @classmethod
    def deserialize(
        cls,
        model_config_bytes: bytearray,
        spu_config_bytes: bytearray,
        model_data_bytes: bytearray,
        chunk_size: int,
        endianness: str,
    ) -> Self:
        """
        Deserializes a byte array into a Model object

        Args:
            model_config_bytes (bytearray): byte array containing the model configuration serialized data
            spu_config_bytes (bytearray): byte array containing the model configuration serialized data
            model_data_bytes (bytearray): byte array containing the model configuration serialized data
            chunk_size (int): size of the chunk (amount of data that can be processed at once) in bytes
            endianness (str): byte order of the serialized data ("big" or "little")
        Return:
            Model: object containing all information describing the model
        """
        type = ModelType(
            int.from_bytes(model_config_bytes[:2], byteorder=endianness, signed=False)
        )
        page_count = int.from_bytes(
            model_config_bytes[2:4], byteorder=endianness, signed=False
        )
        vector_count = int.from_bytes(
            model_config_bytes[4:6], byteorder=endianness, signed=False
        )
        vector_offset = int.from_bytes(
            model_config_bytes[6:8], byteorder=endianness, signed=False
        )
        sequence_count = int.from_bytes(
            model_config_bytes[8:10], byteorder=endianness, signed=False
        )
        sequence_offset = int.from_bytes(
            model_config_bytes[10:12], byteorder=endianness, signed=False
        )
        userdata_size = int.from_bytes(
            model_config_bytes[12:14], byteorder=endianness, signed=False
        )
        userdata_offset = int.from_bytes(
            model_config_bytes[14:16], byteorder=endianness, signed=False
        )
        vectors: list[SpuVector] = []
        for i in range(vector_count):
            vector = SpuVector.deserialize(
                vector_bytes=model_config_bytes[vector_offset:],
                endianness=endianness,
            )
            vectors.append(vector)
            vector_offset += vector.size_in_bytes()

        io_sequences: list[SpuSequence] = cls.deserialize_io_sequences(
            sequence_count=sequence_count,
            sequences_bytes=model_config_bytes[sequence_offset:],
            endianness=endianness,
        )

        userdata = model_data_bytes[userdata_offset : userdata_offset + userdata_size]
        spu = Spu.deserialize(spu_bytes=spu_config_bytes, endianness=endianness)

        # Break down the model data into chunk_size long arrays to be parse as ModelPages
        raw_model_pages: list[np.ndarray[np.uint32]] = [
            model_data_bytes[x : x + chunk_size]
            for x in range(0, len(model_data_bytes), chunk_size)
        ]

        for page_bytes in raw_model_pages:
            spu.populate_from_page(
                page=ModelPage.deserialize(page_bytes=page_bytes, endianness=endianness)
            )
        page_count = spu.generate_pages(page_size=FILE_PAGE_SIZE)

        return cls(
            type=type,
            vectors=vectors,
            io_sequences=io_sequences,
            spu=spu,
            page_count=page_count,
            userdata=userdata,
        )


@dataclass
class FileHeader:
    """
    Class describing the information contained in the header starting the ModelFile

    Attributes:
        magic (str): signature indicating that the file is a femtofile
        endianness (str): endianness of the data used to encode this file
        chunk_size (int): size of the data chunk to read this file
        file_format_version (int): version of the file format
        femtodriver_version (str): version of Femtodriver used to generate this file
        model_name (str): name of the model
        model_version (str): version of the model
        checksum (int): value of checksum for validity verification
        model_config_offset (int): offset in bytes of the model configuration section from the beginning of the file
        model_config_size (int): size of the model header section in bytes
        spu_config_offset (int): offset in bytes of the spu configuration section from the beginning of the file
        spu_config_size (int): size of the SPU configuration section in bytes
        reference_sequence_offset (int): offset of the model reference sequence section
        reference_sequence_size (int): size of the model reference sequence section in bytes
        model_data_offset (int): offset in bytes of the model data section from the beginning of the file
        model_data_size (int): size of the model data section in bytes
    """

    magic: str
    endianness: str
    chunk_size: int
    file_format_version: int
    femtodriver_version: str
    model_name: str
    model_version: str
    checksum: int
    model_config_offset: int
    model_config_size: int
    spu_config_offset: int
    spu_config_size: int
    reference_sequence_offset: int
    reference_sequence_size: int
    model_data_offset: int
    model_data_size: int

    def __init__(
        self,
        magic: str,
        endianness: str,
        chunk_size: int,
        file_format_version: int,
        femtodriver_version: str,
        model_name: str,
        model_version: str,
        checksum: int,
        model_config_size: int,
        spu_config_size: int,
        reference_sequence_size: int,
        model_data_size: int,
    ) -> None:
        """
        Creates a FileHeader object

        Args:
            magic (str): signature indicating that the file is a femtofile
            endianness (str): byte order of the serialized data ("big" or "little")
            chunk_size (int): size of the data chunk to read this file
            file_format_version (int): version of the file format used
            femtodriver_version (str): version of Femtodriver used to generate the file
            model_name (str): name of the model
            model_version (str): version of the model
            checksum (int): value of checksum for validity verification
            model_config_size (int): size of the model header section in bytes
            spu_config_size (int): size of the SPU configuration section in bytes
            reference_sequence_size (int): size of the model reference sequence section in bytes
            model_data_size (int): size of the model data section in bytes
        Return:
            None
        """
        self.magic: str = magic
        self.endianness: str = endianness
        self.chunk_size: int = chunk_size
        self.file_format_version: int = file_format_version
        # Truncating the version and name fields if exceeding max length
        self.femtodriver_version: str = (
            femtodriver_version[:VERSION_LENGTH_MAX]
            if len(femtodriver_version) > VERSION_LENGTH_MAX
            else femtodriver_version.ljust(VERSION_LENGTH_MAX, "\0")
        )
        self.model_name: str = (
            model_name[:NAME_LENGTH_MAX]
            if len(model_name) > NAME_LENGTH_MAX
            else model_name.ljust(NAME_LENGTH_MAX, "\0")
        )
        self.model_version: str = (
            model_version[:VERSION_LENGTH_MAX]
            if len(model_version) > VERSION_LENGTH_MAX
            else model_version.ljust(VERSION_LENGTH_MAX, "\0")
        )
        self.checksum: int = checksum
        self.model_config_offset: int = FILE_HEADER_SIZE
        self.model_config_size: int = model_config_size
        self.spu_config_offset: int = self.model_config_offset + self.model_config_size
        self.spu_config_size: int = spu_config_size
        self.model_data_offset: int = self.spu_config_offset + self.spu_config_size
        self.model_data_size: int = model_data_size
        self.reference_sequence_offset: int = (
            self.model_data_offset + self.model_data_size
        )
        self.reference_sequence_size: int = reference_sequence_size

    def serialize(self) -> bytearray:
        """
        Serializes the FileHeader

        Args:
            None
        Returns:
            bytearray: object serialized into bytes
        """
        byte_buffer = bytearray()
        byte_buffer.extend(FILE_MAGIC.encode("utf-8"))
        byte_buffer.extend(
            int.to_bytes(
                1 if self.endianness == "little" else 2,
                1,
                byteorder=FILE_ENDIANNESS,
                signed=False,
            )
        )
        byte_buffer.extend(
            int.to_bytes(self.chunk_size, 2, byteorder=FILE_ENDIANNESS, signed=False)
        )
        byte_buffer.extend(
            int.to_bytes(
                self.file_format_version, 2, byteorder=FILE_ENDIANNESS, signed=False
            )
        )
        byte_buffer.extend(self.femtodriver_version.encode("utf-8"))
        byte_buffer.extend(self.model_name.encode("utf-8"))
        byte_buffer.extend(self.model_version.encode("utf-8"))
        byte_buffer.extend(
            int.to_bytes(self.checksum, 4, byteorder=FILE_ENDIANNESS, signed=False)
        )

        byte_buffer.extend(
            int.to_bytes(
                self.model_config_size, 2, byteorder=FILE_ENDIANNESS, signed=False
            )
        )
        byte_buffer.extend(
            int.to_bytes(
                self.model_config_offset, 2, byteorder=FILE_ENDIANNESS, signed=False
            )
        )
        byte_buffer.extend(
            int.to_bytes(
                self.spu_config_size,
                2,
                byteorder=FILE_ENDIANNESS,
                signed=False,
            )
        )
        byte_buffer.extend(
            int.to_bytes(
                self.spu_config_offset,
                2,
                byteorder=FILE_ENDIANNESS,
                signed=False,
            )
        )
        byte_buffer.extend(
            int.to_bytes(
                self.model_data_size, 4, byteorder=FILE_ENDIANNESS, signed=False
            )
        )
        byte_buffer.extend(
            int.to_bytes(
                self.model_data_offset, 4, byteorder=FILE_ENDIANNESS, signed=False
            )
        )
        byte_buffer.extend(
            int.to_bytes(
                self.reference_sequence_size,
                4,
                byteorder=FILE_ENDIANNESS,
                signed=False,
            )
        )
        byte_buffer.extend(
            int.to_bytes(
                self.reference_sequence_offset,
                4,
                byteorder=FILE_ENDIANNESS,
                signed=False,
            )
        )
        while len(byte_buffer) % FILE_HEADER_SIZE != 0:
            byte_buffer.append(0xFF)
        return byte_buffer

    @classmethod
    def deserialize(cls, file_header_bytes: bytearray) -> Self:
        """
        Deserializes a byte array into a FileHeader object

        Args:
            file_header_bytes (bytearray): byte array containing the file header serialized data
        Return:
            FileHeader: object containing information necessary to read the file
        Raises:
            ValueError: the file was not recognized
        """
        magic = file_header_bytes[:5].decode("utf-8").strip()
        if magic != FILE_MAGIC:
            raise ValueError(f"File not recognized! Magic={magic}")

        endianness = "little" if file_header_bytes[5] == 1 else "big"

        chunk_size = int.from_bytes(
            file_header_bytes[6:8], byteorder=endianness, signed=False
        )
        file_format_version = int.from_bytes(
            file_header_bytes[8:10], byteorder=endianness, signed=False
        )
        femtodriver_version = file_header_bytes[10:26].decode("utf-8").strip("\x00")
        model_name = file_header_bytes[26:58].decode("utf-8").strip("\x00")
        model_version = file_header_bytes[58:74].decode("utf-8").strip("\x00")
        checksum = int.from_bytes(
            file_header_bytes[74:78], byteorder=endianness, signed=False
        )
        model_config_size = int.from_bytes(
            file_header_bytes[78:80], byteorder=endianness, signed=False
        )
        model_config_offset = int.from_bytes(
            file_header_bytes[80:82], byteorder=endianness, signed=False
        )
        spu_config_size = int.from_bytes(
            file_header_bytes[82:84], byteorder=endianness, signed=False
        )
        spu_config_offset = int.from_bytes(
            file_header_bytes[84:86], byteorder=endianness, signed=False
        )
        model_data_size = int.from_bytes(
            file_header_bytes[86:90], byteorder=endianness, signed=False
        )
        model_data_offset = int.from_bytes(
            file_header_bytes[90:94], byteorder=endianness, signed=False
        )
        reference_sequence_size = int.from_bytes(
            file_header_bytes[94:98], byteorder=endianness, signed=False
        )
        reference_sequence_offset = int.from_bytes(
            file_header_bytes[98:102], byteorder=endianness, signed=False
        )
        assert model_config_offset == FILE_HEADER_SIZE
        assert spu_config_offset == model_config_offset + model_config_size
        assert model_data_offset == spu_config_offset + spu_config_size
        assert reference_sequence_offset == model_data_offset + model_data_size

        return cls(
            magic=magic,
            endianness=endianness,
            chunk_size=chunk_size,
            file_format_version=file_format_version,
            femtodriver_version=femtodriver_version,
            model_name=model_name,
            model_version=model_version,
            checksum=checksum,
            model_config_size=model_config_size,
            spu_config_size=spu_config_size,
            reference_sequence_size=reference_sequence_size,
            model_data_size=model_data_size,
        )


@dataclass
class FemtoFile:
    """
    Class representing the femtofile to export

    Attributes:
        file_header (FileHeader): object containing information necessary to read the file
        model (Model): object containing all information describing the model
        model_name (str): name of the model
        model_version (str): version of the model
        femtodriver_version (str): version of Femtodriver used to generate the femtofile
    """

    file_header: FileHeader
    model: Model
    model_name: str
    model_version: str
    femtodriver_version: str

    def __init__(
        self,
        model_type: str = "",
        model_name: str = "generic_model",
        model_version: str = "1.0.0",
        metadata: dict = None,
        encryption_key_index: int = 0,
        target_spu: SpuPartNumber = SpuPartNumber.UNKNOWN,
        num_used_cores: int = 0,
        femtodriver_version: str = "unknown",
        spu_core_clock_frequency_mhz: int = SPU001_MAX_FREQ,
        model: Model = None,
        file_header: FileHeader = None,
        userdata: bytearray = None,
    ) -> None:
        """
        Initializes a ModelFile object

        Args:
            model_name (str): name of the model
            model_type (str): type of the model
            model_version (str): version of the model
            metadata (dict): metadata generated by Femtodriver containing information to run the model (e.g. input-output specifications)
            encryption_key_index (int): index of the key used encrypt the model
            target_spu (str): intented SPU part number to run this model
            num_used_cores (int): number of cores in use to run the model
            femtodriver_version (str): version of Femtodriver used to generate the femtofile
            spu_core_clock_frequency_mhz (int): recommended SPU core frequency in MHz
            model (Model): object containing all information describing the model
            file_header (FileHeader): object containing information necessary to read the file
            userdata (bytearray): customer data to be store alongside the model
        Returns:
            None
        Raises:
            Exception: the SPU configuration is invalid
        """
        self.file_header = file_header
        self.model_name = model_name
        self.model_version = model_version
        self.femtodriver_version = femtodriver_version
        self.model = (
            Model(
                type=ModelType.str_to_type(model_type),
                target_spu=SpuPartNumber.str_to_pn(target_spu),
                num_used_cores=num_used_cores,
                spu_core_clock_frequency_mhz=spu_core_clock_frequency_mhz,
                encryption_key_index=encryption_key_index,
                userdata=userdata,
            )
            if not model
            else model
        )
        if metadata:
            self._parse_io_specs(
                metadata=metadata,
            )
            if not self.model.spu.validate_configuration():
                raise Exception("The SPU configuration is not valid!")

    def _parse_io_specs(
        self,
        metadata: dict,
    ) -> None:
        """
        Extracts necessary information from the metadata dictionary provided by Femtodriver

        Args:
            metadata (dict): metadata generated by Femtodriver containing information to run the model (e.g. input-output specifications)
        Returns:
            Model: model objects with IO specifications attributes populated
        """
        vector_id: int = 0
        # Current models have only 1 sequence
        sequence: SpuSequence = SpuSequence(id=0, input_ids=[], output_ids=[])

        # sort the input vectors in increasing order of pc_val to ensure consistent input order
        inputs = OrderedDict(
            sorted(metadata["inputs"].items(), key=lambda x: x[1]["pc_val"])
        )
        for input_key in inputs:
            # Setting the size from metadata["fqir_input_padding"] (unpadded size) when available
            # otherwise default to metadata["inputs"] (e.g. when loading from femtofile)
            size = (
                metadata["fqir_input_padding"][input_key]["fqir"]
                if metadata.get("fqir_input_padding", None) is not None
                else metadata["inputs"][input_key]["len_64b_words"] * 4
            )
            self.model.vectors.append(
                SpuVector(
                    id=vector_id,
                    vector_type="input",
                    precision=metadata["inputs"][input_key]["precision"],
                    size=size,
                    padded_size=metadata["inputs"][input_key]["len_64b_words"] * 4,
                    target_core_id=metadata["inputs"][input_key]["core"],
                    parameter=metadata["inputs"][input_key]["pc_val"],
                )
            )
            sequence.input_ids.append(vector_id)
            vector_id += 1

        # sort the output vectors in increasing order of mailbox_id to ensure sequence order matches the model execution
        outputs = OrderedDict(
            sorted(metadata["outputs"].items(), key=lambda x: x[1]["mailbox_id"])
        )
        for output_key in outputs:
            # Setting the size from metadata["fqir_output_padding"] (unpadded size) when available
            # otherwise default to metadata["outputs"] (e.g. when loading from femtofile)
            size = (
                metadata["fqir_output_padding"][output_key]["fqir"]
                if metadata.get("fqir_output_padding", None) is not None
                else metadata["outputs"][output_key]["len_64b_words"] * 4
            )
            self.model.vectors.append(
                SpuVector(
                    id=vector_id,
                    vector_type="output",
                    precision=metadata["outputs"][output_key]["precision"],
                    size=size,
                    padded_size=metadata["outputs"][output_key]["len_64b_words"] * 4,
                    target_core_id=metadata["outputs"][output_key]["core"],
                    parameter=metadata["outputs"][output_key]["mailbox_id"],
                )
            )
            sequence.output_ids.append(vector_id)
            vector_id += 1

        self.model.io_sequences.append(sequence)

    def fill_memory(
        self, core_id: int, bank_id: str, data: np.ndarray[np.uint32]
    ) -> None:
        """
        Fill the SPU memory with the data provided. The data array is broken down into chunks to match the page size

        Args:
            core_id (int): ID of the core where the data should be stored (e.g. 0 or 1 for SPU001)
            bank_id (str): ID of the memory bank where the data should be stored (e.g. "DM2", "TM3")
            data (np.ndarray[np.uint32]): array containing data to be stored in the memory bank
        Return:
            None
        """
        self.model.populate_memory(
            core_id=core_id,
            bank_key=bank_id,
            data=data,
        )

    def serialize_header(
        self,
        model_size: int,
        reference_sequence_size: int,
        chunk_size: int,
        checksum: int,
    ) -> bytearray:
        """
        Serializes the header section of the model (file header-model header-spu configuration)

        Args:
            model_size (int): size of the model in bytes
            reference_sequence_size (int): size of the reference sequence section
            chunk_size (int): size of the chunk (amount of data that can be processed at once) in bytes
            checksum (int): value of the checksum over the entire model
        Returns:
            bytearray: model header section serialized into bytes
        """
        # Prepare the header data prior to populating the header
        model_config = self.model.serialize_header()
        spu_config = self.model.spu.serialize_configuration()

        # When both model_config and spu_config cannot fit in one chunk_size,
        # allocate a chunk for each by padding them to reach chunk_size
        if (len(model_config) + len(spu_config)) > chunk_size:
            while len(model_config) % chunk_size != 0:
                model_config.append(0xFF)
            while len(spu_config) % chunk_size != 0:
                spu_config.append(0xFF)
        # Add padding to spu_config to make sure the next section (reference_sequence) starts on a new chunk
        else:
            while (len(model_config) + len(spu_config)) % chunk_size != 0:
                spu_config.append(0xFF)

        self.file_header = FileHeader(
            magic=FILE_MAGIC,
            endianness=FILE_ENDIANNESS,
            chunk_size=FILE_CHUNK_SIZE,
            file_format_version=FILE_FORMAT_VERSION,
            femtodriver_version=self.femtodriver_version,
            model_name=self.model_name,
            model_version=self.model_version,
            checksum=checksum,
            model_config_size=len(model_config),
            spu_config_size=len(spu_config),
            reference_sequence_size=reference_sequence_size,
            model_data_size=model_size,
        )

        byte_buffer = bytearray()
        byte_buffer.extend(self.file_header.serialize())
        byte_buffer.extend(model_config)
        byte_buffer.extend(spu_config)
        return byte_buffer

    def print_specifications(self) -> None:
        """
        Prints the femtofile specifications (i.e. model and IOSpecs, SPU)

        Args:
            None
        Returns:
            None
        """
        print(f"{self.model_name} v{self.model_version}")
        print(self.model.spu.get_specifications())
        print(self.model.get_specifications())

    def serialize(self) -> bytearray:
        """
        Serializes the complete model (including headers)

        Args:
            none
        Returns:
            bytearray: model serialized into bytes
        """
        byte_buffer = bytearray()
        reference_sequences_bytes = bytearray()
        model_data = self.model.serialize_data(chunk_size=FILE_CHUNK_SIZE)
        # TODO: compute a valid checksum
        headers = self.serialize_header(
            model_size=len(model_data),
            reference_sequence_size=len(reference_sequences_bytes),
            chunk_size=FILE_CHUNK_SIZE,
            checksum=0,
        )
        byte_buffer.extend(headers)
        byte_buffer.extend(model_data)
        byte_buffer.extend(reference_sequences_bytes)

        return byte_buffer

    def export_file(self, export_path: str, file_name: str) -> tuple[str, int]:
        """
        Writes the serialized model to file

        Args:
            export_path (str): path to export the femtofile
            file_name (str): name of the femtofile
        Return:
            tuple[str, int]: a tuple containing the path to the exported file and its size
        """
        file_size = 0
        file_path = path.join(export_path, f"{file_name}{MODEL_EXTENSION}")
        output_file = open(file=file_path, mode="wb")

        file_size += output_file.write(self.serialize())

        output_file.close()
        self.print_specifications()
        return (file_path, file_size)

    @classmethod
    def import_file(cls, import_path: str) -> Self:
        """
        Reads the file provided and extract the data it contains into a FemtoFile object

        Args:
            import_path (str): path to the femtofile
        Returns:
            FemtoFile: object identical to the one use to generate the femtofile
        """
        input_file = open(file=import_path, mode="rb")

        # Read the header section (always FILE_CHUNK_SIZE)
        file_header_bytes = input_file.read(FILE_CHUNK_SIZE)
        file_header: FileHeader = FileHeader.deserialize(
            file_header_bytes=file_header_bytes
        )

        model_config_bytes = input_file.read(file_header.model_config_size)
        spu_config_bytes = input_file.read(file_header.spu_config_size)
        model_data_bytes = input_file.read(file_header.model_data_size)
        ref_sequences_bytes = input_file.read(file_header.reference_sequence_size)

        model = Model.deserialize(
            model_config_bytes=model_config_bytes,
            spu_config_bytes=spu_config_bytes,
            model_data_bytes=model_data_bytes,
            chunk_size=file_header.chunk_size,
            endianness=file_header.endianness,
        )
        # This value is used only when loading and must be reset
        # to 0 to match the original object and pass the unit test
        model.spu.last_page_id = 0
        return cls(file_header=file_header, model=model)
