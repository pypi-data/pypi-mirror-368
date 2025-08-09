#  Copyright Femtosense 2024
#
#  By using this software package, you agree to abide by the terms and conditions
#  in the license agreement found at https://femtosense.ai/legal/eula/
#

import numpy as np

try:
    from femtobehav import cfg
except ImportError:
    from femtodriver import cfg

import warnings


def load_hexfile(filename):
    with warnings.catch_warnings():
        # the rqueue contents may be empty
        warnings.filterwarnings("ignore", message=".*input contained no data.*")
        vals = np.loadtxt(
            filename, dtype="uint64", usecols=(0,), converters={0: lambda s: int(s, 16)}
        )

    return np.atleast_1d(vals)


def save_hexfile(fname, vals, bits=None):
    def bits_to_fmt(x):
        return "%0" + str(int(np.ceil(x) / 4)) + "x"

    def hex_fmt_for_mem(mem):
        membits = {
            "DM": cfg.B_DATA_WORD,
            "TM": cfg.B_TABLE_WORD,
            "SB": cfg.B_SB,
            "RQ": cfg.B_RQ,
            "PB": cfg.B_PC,
            "IM": cfg.B_INSTR,
        }
        return bits_to_fmt(membits[mem])

    # np.savetxt(fname, vals, fmt=hex_fmt_for_mem(mem))
    # XXX should infer memory type
    if bits is None:
        fmt = hex_fmt_for_mem("DM")
    else:
        fmt = bits_to_fmt(bits)
    np.savetxt(fname, np.atleast_1d(vals), fmt=fmt)
