"""
Copyright Femtosense 2024

By using this software package, you agree to abide by the terms and conditions
in the license agreement found at https://femtosense.ai/legal/eula/
"""

import io
import os
import zipfile
import json
import yaml
from dataclasses import dataclass, field
from typing import Any
import re
from collections import defaultdict
import logging
import numpy as np
from femtodriver import cfg
from typing_extensions import Self
from femtodriver.plugins.femtofile_export import (
    FemtoFile,
    MemoryType,
    SpuVectorType,
    CoreStatus,
)
import femtodriver.util.packing as packing

logger = logging.getLogger(__name__)


@dataclass
class CompiledData:
    """
    This dataclass is used to pass the compiled data between parts of femtodriver.

    We can ingest the compiled data from
    1) zipfile from femtocrux, either from disk or in memory
    2) get_yaml_metadata() and save_packed_mems() from femtobehav

    This contains objects that previously were serialized to disk in metadata_from_femtocrux
    or metadata_from_femtomapper. This dataclass can still serialize to disk in the same
    file formats for compatibility.

    The @dataclass decorator provides an __init__ using the order of the class variables below.

    properties:

    metadata: The yaml metadata is the same as the data previously in metadata.yaml

    mems_per_core: This has the format:

        {int_core_num:
            {"mem_type": [ ndarray, dtype=uint64 ]
        }

        There is a list outside of the ndarray for the bitgroup. The ndarray contains the memory values.

        Example:
        {0:
            {
             'PB': [array([14314090843277134396,  2018386756837530037], dtype=uint64)],
             'SB': [array([4135357273466834195, 4135357273466834195], dtype=uint64)],
             'RQ': [array([], dtype=uint64)],
             'DM': [array([13888226787968091394,  9843035493399530530, ... , 14314090843277134396], dtype=uint64)],
             'TM': [array([14314090843277134396, 14314090843277134396, ... , 14314090843277134396], dtype=uint64)],
             'IM': [array([ 6799421245011815489,  8027002519056196319, ... , 14314090843277134396], dtype=uint64)]
            }
        }

    files: the contents of the files that were previously generated in a dict {"filename": file_bytes}
    _metadata_filename: a string representation of the filename used to distinguish the metadata.yaml
    """

    metadata: Any = field(default_factory=dict)
    mems_per_core: Any = field(default_factory=dict)
    files: dict[str, Any] = field(default_factory=dict)  # Store objects, not raw bytes
    _metadata_filename: str = (
        "metadata.yaml"  # Internal storage for the metadata file name
    )

    @classmethod
    def read_from_files(cls, input_directory: str) -> Self:
        """
        Reads all files from the specified directory and reconstructs the mems_per_core and metadata.

        @param input_directory: a string representing the meta directory to read the files from

        @returns a CompiledData object with populated metadata and mems_per_core
        """
        if not os.path.exists(input_directory):
            raise FileNotFoundError(f"Directory '{input_directory}' does not exist.")

        files = {}
        mems_per_core = defaultdict(
            lambda: defaultdict(list)
        )  # Initialize the memory structure
        metadata = None

        # Load files from the directory
        for root, _, file_names in os.walk(input_directory):
            for file_name in file_names:
                file_path = os.path.join(root, file_name)

                with open(file_path, "rb") as file:
                    content = file.read()

                if file_name == cls._metadata_filename:
                    metadata = cls._decode_file(cls, file_name, content)
                else:
                    core_num, mem_type, bitgroup = cls.parse_memory_file_name(file_name)
                    if core_num is None or mem_type is None:
                        logger.debug(
                            f"Skipping file '{file_name}' as it doesn't match expected patterns."
                        )
                        continue

                    mem_bg = cls.convert_hex_to_ndarray(content)
                    mems_per_core[core_num][mem_type].append(mem_bg)

                # Store decoded file content
                files[file_name] = cls._decode_file(cls, file_name, content)

        return cls(files=files, metadata=metadata, mems_per_core=dict(mems_per_core))

    @classmethod
    def read_from_zip(cls, zip_input: str | bytes) -> Self:
        """
        Reads files from a zip archive and reconstructs the mems_per_core and metadata.

        @param: zip_input: the input zip as either a string to a file on disk or the bytes object

        @returns: a constructed CompiledData object with populated metadata and mems_per_core
        """
        files = {}
        mems_per_core = defaultdict(
            lambda: defaultdict(list)
        )  # Initialize the memory structure
        metadata = None

        if isinstance(zip_input, bytes):
            zip_data = io.BytesIO(zip_input)
        elif isinstance(zip_input, str):
            zip_data = zip_input

        with zipfile.ZipFile(zip_data, "r") as zip_file:
            # Iterate through files in the ZIP archive
            for file_name in zip_file.namelist():
                with zip_file.open(file_name) as file:
                    content = file.read()

                if file_name == cls._metadata_filename:
                    metadata = cls._decode_file(cls, file_name, content)
                else:
                    core_num, mem_type, bitgroup = cls.parse_memory_file_name(file_name)
                    if core_num is None or mem_type is None:
                        logger.debug(
                            f"Skipping file '{file_name}' as it doesn't match expected patterns."
                        )
                        continue

                    mem_bg = cls.convert_hex_to_ndarray(content)
                    mems_per_core[core_num][mem_type].append(mem_bg)

                # Store decoded file content
                files[file_name] = cls._decode_file(cls, file_name, content)

        return cls(files=files, metadata=metadata, mems_per_core=dict(mems_per_core))

    @classmethod
    def read_from_femtofile(cls, femtofile_path: str) -> Self:
        """
        Reads the femtofile and reconstructs the mems_per_core and metadata.

        @param: femtofile_path: path to the femtofile to load

        @returns: a constructed CompiledData object with populated metadata and mems_per_core
        """
        femtofile: FemtoFile = FemtoFile.import_file(femtofile_path)
        mems_per_core = defaultdict(lambda: defaultdict(list))
        metadata = defaultdict(
            lambda: defaultdict(list),
            {
                "data_bank_sizes": {0: {}, 1: {}},
                "table_bank_sizes": {0: {}, 1: {}},
                "inst_counts": {},
                "inputs": {},
                "outputs": {},
            },
        )
        files = None
        for vector in femtofile.model.vectors:
            match vector.type:
                case SpuVectorType.INPUT:
                    metadata["inputs"][str(len(metadata["inputs"]))] = {
                        "core": vector.target_core_id,
                        "pc_val": vector.parameter,
                        # convert from i16 to u64
                        "len_64b_words": vector.padded_size // 4,
                        "precision": vector.precision.value,
                        "dtype": f"V{vector.precision.value}",
                    }
                case SpuVectorType.OUTPUT:
                    metadata["outputs"][str(len(metadata["outputs"]))] = {
                        "core": vector.target_core_id,
                        "mailbox_id": vector.parameter,
                        # convert from i16 to u64
                        "len_64b_words": vector.padded_size // 4,
                        "precision": vector.precision.value,
                        "dtype": f"V{vector.precision.value}",
                    }
        for core in femtofile.model.spu.cores:
            if core.status == CoreStatus.OFF:
                continue
            for bank_key in core.memory_banks:
                bank = core.memory_banks.get(bank_key)
                bank_len = len(bank.data) // 2  # Femtodriver uses u64, not u32
                padding_required = 0

                # filling metadata
                match bank.type:
                    case MemoryType.DM:
                        metadata["data_bank_sizes"][core.id][bank.id] = bank_len
                        padding_required = cfg.DATA_MEM_BANK_WORDS - bank_len
                    case MemoryType.TM:
                        metadata["table_bank_sizes"][core.id][bank.id] = bank_len
                        padding_required = cfg.TABLE_MEM_BANK_WORDS - bank_len
                    case MemoryType.IM:
                        # do not add IM empty banks in the metadata
                        if bank_len == 0:
                            continue
                        metadata["inst_counts"][core.id] = bank_len
                        padding_required = cfg.MAX_INSTR - bank_len

                # first time create the array
                if len(mems_per_core[core.id][str(bank.type)]) == 0:
                    mems_per_core[core.id][str(bank.type)] = [
                        np.empty(shape=[0, 1], dtype="uint64")
                    ]
                # load bank data
                mems_per_core[core.id][str(bank.type)][0] = np.append(
                    mems_per_core[core.id][str(bank.type)][0],
                    packing.unpack_32_to_64(np.array(bank.data, dtype="uint32")),
                )
                # add padding to fill in the bank
                mems_per_core[core.id][str(bank.type)][0] = np.pad(
                    mems_per_core[core.id][str(bank.type)][0],
                    (0, padding_required),
                    mode="constant",
                    constant_values=14314090843277134396,
                )
            mems_per_core[core.id]["RQ"] = [np.empty(shape=[0, 1], dtype=">u8")]

        return cls(files=files, metadata=metadata, mems_per_core=dict(mems_per_core))

    def read_txt(self, file_name: str) -> str:
        """Reads a text file as a string."""
        if file_name in self.files:
            return self.files[file_name]
        else:
            raise FileNotFoundError(f"File '{file_name}' not found in memory.")

    def read_json(self, file_name: str) -> Any:
        """Reads a JSON file and returns a Python object."""
        if file_name in self.files:
            return self.files[file_name]
        else:
            raise FileNotFoundError(f"File '{file_name}' not found in memory.")

    def read_yaml(self, file_name: str) -> Any:
        """Reads a YAML file and returns a Python object."""
        if file_name in self.files:
            return self.files[file_name]
        else:
            raise FileNotFoundError(f"File '{file_name}' not found in memory.")

    def _decode_file(self, file_name: str, content: bytes) -> Any:
        """Decodes file content based on its extension."""
        if file_name.endswith((".yaml", ".yml")):
            return yaml.safe_load(content.decode("utf-8"))
        elif file_name.endswith(".json"):
            return json.loads(content.decode("utf-8"))
        elif file_name.endswith(".txt"):
            return content.decode("utf-8")
        else:
            # Keep as raw bytes for unknown file types
            return content

    def _encode_file(self, file_name: str, content: Any) -> bytes:
        """Encodes the in-memory object back into bytes based on its extension."""
        if file_name.endswith((".yaml", ".yml")):
            return yaml.dump(content).encode("utf-8")
        elif file_name.endswith(".json"):
            return json.dumps(content, indent=4).encode("utf-8")
        elif file_name.endswith(".txt"):
            return content.encode("utf-8")
        else:
            # Assume raw bytes for unknown file types
            return content

    def _write_to_zip(self, zip_file_obj):
        """Helper function to encode and write files to a zipfile.ZipFile object."""
        for file_name, content in self.files.items():
            zip_file_obj.writestr(file_name, self._encode_file(file_name, content))

    def to_zip_file(self, file_path: str):
        """Writes the in-memory files to a ZIP file on disk."""
        with zipfile.ZipFile(file_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
            self._write_to_zip(zip_file)
        print(f"ZIP file written to {file_path}")

    def to_zip_bytes(self) -> bytes:
        """Serializes the in-memory files to a ZIP file in bytes."""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            self._write_to_zip(zip_file)
        zip_buffer.seek(0)  # Go back to the start of the buffer
        return zip_buffer.read()

    def write_to_files(self, output_dir: str):
        """Writes all in-memory files to the specified output directory."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Write metadata file
        file_path = os.path.join(output_dir, self._metadata_filename)
        with open(file_path, "w") as file:
            yaml.dump(self.metadata, file, sort_keys=False)

        files_written = self._write_mems_to_disk(
            mems=self.mems_per_core, output_dir=output_dir
        )

        logger.debug(f"{files_written} were written to disk in {output_dir}")

    def _write_mems_to_disk(self, mems: Any, output_dir: str) -> list[str]:
        """
        Serialize the mems_per_core datastrucutre to disk. The memories are already encrypted
        so we don't have to do that here.
        """
        if cfg.ISA < 2.0:
            return self._write_mems_to_disk_1pX(mems, output_dir)
        else:
            return self._write_mems_to_disk_2pX(mems, output_dir)

    def _write_mems_to_disk_1pX(self, mems: Any, output_dir: str) -> list[str]:
        list_of_files = []

        names_bw = {
            "PB": ("progbuf", cfg.B_PC),
            "SB": ("sboard", cfg.B_SB),
            "RQ": ("rqueue", cfg.B_RQ),
            "DM": ("data_mem", cfg.B_DATA_WORD),
            "TM": ("table_mem", cfg.B_TABLE_WORD),
            "IM": ("instr_mem", cfg.B_INSTR),
        }

        for cidx, mems in self.mems_per_core.items():
            for shortname, mem in mems.items():
                mem_longname = names_bw[shortname][0]
                bitwidth = names_bw[shortname][1]
                for bg_idx, mem_bg in enumerate(mem):
                    if len(mem) == 1:
                        bg_str = ""
                    else:
                        bg_str = "bitgroup{}_".format(bg_idx)

                    filename = (
                        f"test_core_{cidx}_{mem_longname}_{bg_str}initial_py_hex.txt"
                    )

                    file_path = os.path.join(output_dir, filename)

                    np.savetxt(
                        file_path,
                        mem_bg,
                        fmt="%0{}x".format(int(np.ceil(bitwidth / 4))),
                    )
                    list_of_files.append(filename)

            # also writes out the length of a the ready queue to a file
            rq_len_fname = f"test_core_{cidx}_rqueue_len_initial.txt"
            rq_len_file_path = os.path.join(output_dir, rq_len_fname)
            with open(rq_len_file_path, "w") as fhandle:
                fhandle.write(str(len(mems["RQ"][0])) + "\n")

            list_of_files.append(rq_len_fname)

        return list_of_files

    def _write_mems_to_disk_2pX(self, mems: Any, output_dir: str) -> list[str]:
        list_of_files = []

        names_bw = {
            "PB": ("progbuf", cfg.B_PC),
            "SB": ("sboard", cfg.B_SB),
            "RQ": ("rqueue", cfg.B_RQ),
            "DM": ("data_mem", cfg.B_DATA_WORD),
            "TM": ("table_mem", cfg.B_TABLE_WORD),
            "IM": ("instr_mem", cfg.B_INSTR),
        }

        for cidx, mems in self.mems_per_core.items():
            for shortname, mem in mems.items():
                mem_longname, bitwidth = names_bw[shortname]  # don't need bitwidth

                fname_base = f"test_core_{cidx}_{mem_longname}_initial"
                if mem is not None:
                    if "bin" in formats:
                        membytes = mem.to_bytestream()
                        with open(fname_base + "_bin.bin", "wb") as f:
                            f.write(membytes)

                    if "binstr" in formats:
                        bin_strs = mem.bin_strs()
                        with open(fname_base + "_bin_dbg.txt", "w") as f:
                            f.writelines("\n".join(bin_strs))

                    if "binstr_dbg" in formats:
                        bin_strs = mem.bin_strs(readability_spaces=False)
                        with open(fname_base + "_bin.txt", "w") as f:
                            f.writelines("\n".join(bin_strs))

            # also writes out the length of a the ready queue to a file
            rq_len_fname = f"test_core_{cidx}_rqueue_len_initial.txt"
            rq_len_file_path = os.path.join(output_dir, rq_len_fname)
            with open(rq_len_file_path, "w") as fhandle:
                fhandle.write(str(len(mems["RQ"][0])) + "\n")

            list_of_files.append(rq_len_fname)

        return list_of_files

    @staticmethod
    def parse_memory_file_name(file_name: str):
        """Extracts the core number, memory type, and bitgroup index from the file name."""

        mem_long_to_short = {
            "progbuf": "PB",
            "sboard": "SB",
            "rqueue": "RQ",
            "data_mem": "DM",
            "table_mem": "TM",
            "instr_mem": "IM",
        }

        pattern = re.compile(r"test_core_(\d+)_(\w+)(_bitgroup\d+)?_initial_py_hex.txt")
        match = pattern.match(file_name)
        if match:
            core_num = int(match.group(1))
            mem_longname = match.group(2)
            bitgroup = match.group(3)
            mem_type = mem_long_to_short.get(mem_longname, None)
            return core_num, mem_type, bitgroup
        return None, None, None

    @staticmethod
    def convert_hex_to_ndarray(hexstr: bytes):
        """
        Convert a hex string (in bytes) to a NumPy ndarray based on the memory type.
        Assumes each line is a hex value.
        """
        data_io = io.StringIO(hexstr.decode())
        data = np.loadtxt(
            data_io, dtype=f"uint64", converters={0: lambda s: int(s, 16)}
        )
        return data

    def set_metadata_file(self, file_name: str):
        """Sets the file to be used as metadata."""
        if file_name in self.files:
            self._metadata_filename = file_name
        else:
            raise FileNotFoundError(f"File '{file_name}' not found in memory.")
