#  Copyright Femtosense 2024
#
#  By using this software package, you agree to abide by the terms and conditions
#  in the license agreement found at https://femtosense.ai/legal/eula/
#

try:
    from femtobehav import cfg
except ImportError:
    from femtodriver import cfg

APB_ADDR = 0x0  # base of APB addr range

N_CORES = 4

B_CONF_ADDR = 17
CONF_BLOCK = 2**B_CONF_ADDR
B_AXI_CHUNK = B_CONF_ADDR + 3
AXI_CHUNK = 2**B_AXI_CHUNK
BANK_BLOCK = cfg.DATA_MEM_BANK_WORDS // 4

PHYS_DM_BANKS = 4
PHYS_TM_BANKS = 4

HAS_PLL = False

#############################################
# SPI registers--there are none

SPI_REGS = []
SPI_REG_TO_IDXS = {reg: i for i, reg in enumerate(SPI_REGS)}

#############################################
# toplevel registers, outside core array

# 16b SPI reg space
# still programmable with 32b words
SYS_REGS = [
    "VERSION",  # HW version, 8b, {4b: major , 4b: minor}
    "SPI_ENCRYPTION_KEY_IDX",  # select from preset keys
    "SPI_ENCRYPTION_SALT_3",  # user can modify key
    "SPI_ENCRYPTION_SALT_2",
    "SPI_ENCRYPTION_SALT_1",
    "SPI_ENCRYPTION_SALT_0",
    "AXIS_SELECT",  # where to source/sink AXIS streams, 1=APB or 0=external
]
SYS_REG_TO_IDXS = {reg: i for i, reg in enumerate(SYS_REGS)}

##############################################
# 32b control register space
# each core now has a copy of the original SYS_REGS + CONTROL_REGS

# useful mem power state values:
# (default timing adjust pin values)
# to "off"                    : 0x01098
# to "chip disable (CD)" hub  : 0x05098
# to "sleep"                  : 0x09098
# to "sleep trans"            : 0x0d098
# to "on"                     : 0x11098
# to "FSM control"            : 0x15098
#
# allowed transitions
# off <-> CD
# on <->
# sleep_trans <-> CD
# sleep_trans <-> sleep
#
# e.g.:
# power on:
#   off -> CD -> on
# power off:
#   on  -> CD -> off
# powered -> retention:
#   on  -> CD -> sleep_trans -> sleep
# retention -> powered:
#   sleep -> sleep_trans -> CD -> on
CORE_REGS = [
    "RST",  # core reset
    "DM_TIMERS",  # automatic sleep FSM regs
    "TM_TIMERS",
    "IM_TIMERS",
    "REG_DP_ACK_DELAY",  # how many fudge cycles to pad on the end of the datapaths' ack
    *[
        f"DM_CONF{i}" for i in range(PHYS_DM_BANKS)
    ],  # power state toggles, delay adjust values (EMA, eg)
    *[f"TM_CONF{i}" for i in range(PHYS_TM_BANKS)],
    "IM_CONF",
]

SYS_REG_ADDRS = {r: i for i, r in enumerate(SYS_REGS)}
CORE_REG_REL_ADDRS = {r: i for i, r in enumerate(CORE_REGS)}

CONF_ADDRS = {
    "DM": 0,
    "TM": 0 + BANK_BLOCK * (PHYS_DM_BANKS),
    "IM": 0 + BANK_BLOCK * (PHYS_DM_BANKS + PHYS_TM_BANKS + 0),
    "SB": 0 + BANK_BLOCK * (PHYS_DM_BANKS + PHYS_TM_BANKS + 1),
    "RQ": 0 + BANK_BLOCK * (PHYS_DM_BANKS + PHYS_TM_BANKS + 2),
    "PB": 0 + BANK_BLOCK * (PHYS_DM_BANKS + PHYS_TM_BANKS + 3),
    "HEAD_TAIL_REG": 0 + CONF_BLOCK - 3,
}

# system register useful const values:
# fmt: off
MEM_TO_OFF         = 0x01098
MEM_TO_CD          = 0x05098
MEM_TO_SLEEP       = 0x09098
MEM_TO_SLEEP_TRANS = 0x0D098
MEM_TO_ON          = 0x11098
MEM_TO_FSM         = 0x15098
# fmt: on

# add addresses for individual banks, allow us to program one bank at a time
for i in range(cfg.CORE_DATA_MEM_BANKS):
    CONF_ADDRS[f"DM{i}"] = CONF_ADDRS["DM"] + BANK_BLOCK * i
for i in range(cfg.CORE_TABLE_MEM_BANKS):
    CONF_ADDRS[f"TM{i}"] = CONF_ADDRS["TM"] + BANK_BLOCK * i

APB_OBJS = set(SYS_REGS) | set(CORE_REGS) | set(CONF_ADDRS.keys())

# NOTE THAT HEAD_TAIL_REG HAS MOVED FROM ITS TRADITIONAL CONF_BLOCK-1 ADDR!
# now the MEM_POWERs go in -1 and -2


# num banks, bitwidth, bank size
class MemInfoEntry:
    def __init__(self, *args):
        (
            self.logical_banks,
            self.physical_banks,
            self.bits,
            self.logical_bank_words,
        ) = args


MEM_INFO = {
    "DM": MemInfoEntry(1, PHYS_DM_BANKS, cfg.B_DATA_WORD, cfg.DATA_MEM_BANK_WORDS),
    "TM": MemInfoEntry(1, PHYS_TM_BANKS, cfg.B_TABLE_WORD, cfg.TABLE_MEM_BANK_WORDS),
    "IM": MemInfoEntry(1, 1, cfg.B_INSTR, cfg.MAX_INSTR),
    "SB": MemInfoEntry(1, 1, cfg.B_SB, cfg.MAX_THREADS),
    "RQ": MemInfoEntry(1, 1, cfg.B_TIDX, cfg.MAX_THREADS),
    "PB": MemInfoEntry(1, 1, cfg.B_PC, cfg.MAX_THREADS),
}


def mem_conf_addr_map(mem, file_offset):
    base_addr = CONF_ADDRS[mem]

    if mem == "TM":
        addr_offset = (
            BANK_BLOCK * (file_offset // cfg.TABLE_MEM_BANK_WORDS)
            + file_offset % cfg.TABLE_MEM_BANK_WORDS
        )
    else:
        addr_offset = file_offset

    addr = base_addr + addr_offset
    # print(f'mem: {mem}, file_offset {file_offset}, addr {addr}')

    return addr


# APB space is arranged
# register space for all cores (size of CONF_BLOCK)
# memories for core 0 (CONF_BLOCK)
# memories for core 1 (CONF_BLOCK)
# ...
def CONF_ADDR_TO_BYTE_ADDR(core, rel_conf_addr):
    return APB_ADDR + (2 + 2 * core + 1) * AXI_CHUNK + rel_conf_addr * 8


def SYS_REG_ADDR_TO_BYTE_ADDR(core, rel_reg_addr):  # core is unused
    return APB_ADDR + rel_reg_addr * 4


def CORE_REG_ADDR_TO_BYTE_ADDR(core, rel_reg_addr):
    return APB_ADDR + (2 + 2 * core + 0) * AXI_CHUNK + rel_reg_addr * 4


def OBJ_TO_BYTE_ADDR(obj, core=None, file_offset=0):
    if (
        obj in MEM_INFO
        or len(obj) == 3
        and (obj.startswith("DM") or obj.startswith("TM"))
    ):
        conf_addr = mem_conf_addr_map(obj, file_offset)
        axi_addr = CONF_ADDR_TO_BYTE_ADDR(core, conf_addr)
    elif obj in CONF_ADDRS:
        conf_addr = CONF_ADDRS[obj]
        axi_addr = CONF_ADDR_TO_BYTE_ADDR(core, conf_addr + file_offset)
    elif obj in SYS_REGS:
        reg_addr = SYS_REG_ADDRS[obj]
        axi_addr = SYS_REG_ADDR_TO_BYTE_ADDR(core, reg_addr + file_offset)
    elif obj in CORE_REGS:
        reg_addr = CORE_REG_REL_ADDRS[obj]
        axi_addr = CORE_REG_ADDR_TO_BYTE_ADDR(core, reg_addr + file_offset)
    elif obj == "RTR":
        assert file_offset == 0
        axi_addr = 0  # filled in by zynq
    elif obj in SPI_REGS:
        assert False and "no SPI regs in 2.0"
    else:
        axi_addr = None
    return axi_addr


# just for printout
def get_axi_mem_map():
    def hexify(x):
        return "{:08X}".format(x)

    print("######################################")

    def _print_dict_lines(D):
        for k, v in D.items():
            print(f"{hexify(k)} : {v}")

    print("######################################")
    print("APB address space")
    print("######################################")
    print("")
    print("######################################")
    print("system-wide registers")
    print("######################################")
    sys_reg_addr = {
        SYS_REG_ADDR_TO_BYTE_ADDR(0, i): reg for reg, i in SYS_REG_ADDRS.items()
    }
    _print_dict_lines(sys_reg_addr)

    print("######################################")
    print("per-core conf registers")
    print("######################################")
    for j in range(N_CORES):
        core_reg_addr = {
            CORE_REG_ADDR_TO_BYTE_ADDR(j, i): f"core {j} : {reg}"
            for reg, i in CORE_REG_REL_ADDRS.items()
        }
        _print_dict_lines(core_reg_addr)

    for j in range(N_CORES):
        print("######################################")
        print(f"core {j} primary memory")
        print("######################################")

        for mem, info in MEM_INFO.items():
            banks = info.logical_banks
            bank_size = info.logical_bank_words
            # print(f'memory: {mem}, {info.bits} bits wide')
            assert info.logical_banks == 1

            start_addr = OBJ_TO_BYTE_ADDR(mem, core=j, file_offset=0)
            end_addr = OBJ_TO_BYTE_ADDR(mem, core=j, file_offset=bank_size - 1)

            print(
                f"{hexify(start_addr)} : {mem} start | (conf = {hexify(start_addr // 8)})"
            )
            print(
                f"{hexify(end_addr)} : {mem} end   | (conf = {hexify(end_addr // 8)})"
            )

            # print MSB range for IM
            if mem == "IM":
                start_addr = OBJ_TO_BYTE_ADDR(mem, core=j, file_offset=bank_size)
                end_addr = OBJ_TO_BYTE_ADDR(mem, core=j, file_offset=2 * bank_size - 1)

                print(
                    f"{hexify(start_addr)} : {mem}_msbs start | (conf = {hexify(start_addr // 8)})"
                )

                print(
                    f"{hexify(end_addr)} : {mem}_msbs end   | (conf = {hexify(end_addr // 8)})"
                )

        start_addr = OBJ_TO_BYTE_ADDR("HEAD_TAIL_REG", core=j)
        end_addr = OBJ_TO_BYTE_ADDR("HEAD_TAIL_REG", core=j)
        print(f"{hexify(start_addr)} : HEAD_TAIL_REG start")
        print(f"{hexify(end_addr)} : HEAD_TAIL_REG end")


if __name__ == "__main__":
    get_axi_mem_map()
