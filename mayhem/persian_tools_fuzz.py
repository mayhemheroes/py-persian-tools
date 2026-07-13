#!/usr/bin/env python3
"""Atheris fuzz harness for py-persian-tools.

Ported from the original fork harness (fuzz/persian_tools_fuzz.py, target
`persian_tools_fuzz`) and broadened: the original drove only the digits and
ordinal_suffix converters; this version keeps those exact code paths and adds
the library's remaining public parsers/validators (separator, national_id,
legal_id, phone_number, bill, plate, bank card_number, bank sheba) so coverage
reflects the whole library. Atheris instruments the imported persian_tools
modules, so libFuzzer drives the parsers toward new code paths.

Exceptions defined by persian_tools itself (InvalidCardNumber, InvalidShebaNumber,
InvalidPlateLength, ...) are the library's documented rejection path for bad
input and are swallowed; anything else (TypeError, IndexError, ... escaping the
library) is a real defect and propagates to the fuzzer.

Run modes (driven by the compiled launcher `persian_tools_fuzz` / `-standalone`):
  * fuzzing      -- `python3 persian_tools_fuzz.py [libFuzzer args]`
  * single input -- `python3 persian_tools_fuzz.py <file>` (libFuzzer runs it once)
"""
import signal
import sys

import atheris

with atheris.instrument_imports():
    from persian_tools import (
        bill,
        digits,
        legal_id,
        national_id,
        ordinal_suffix,
        phone_number,
        plate,
        separator,
    )
    from persian_tools.bank import card_number, sheba


class _InputTimeout(Exception):
    pass


def _alarm(signum, frame):
    raise _InputTimeout()


signal.signal(signal.SIGALRM, _alarm)
_PER_INPUT_SECONDS = 5


def _is_library_error(exc):
    return type(exc).__module__.startswith("persian_tools")


def _bill(s):
    ds = "".join(c for c in s if c.isdecimal())
    bill.get_detail(bill_id=int(ds[:13] or "0"), payment_id=int(ds[13:26] or "0"))


_OPS = None


def _ops():
    global _OPS
    if _OPS is None:
        _OPS = [
            digits.convert_from_word,          # original harness path 0
            ordinal_suffix.remove,             # original harness path 1
            digits.convert_to_fa,              # original harness path 2
            digits.convert_to_en,              # original harness path 3
            digits.convert_to_ar,              # original harness path 4
            ordinal_suffix.add,
            separator.add,
            separator.remove,
            national_id.validate,
            legal_id.validate,
            phone_number.validate,
            phone_number.normalize,
            phone_number.operator_data,
            card_number.validate,
            card_number.extract_card_numbers,
            sheba.validate,
            plate.get_info,
            plate.is_valid,
            plate.normalize,
            _bill,
        ]
    return _OPS


@atheris.instrument_func
def TestOneInput(data):
    if not data:
        return
    fdp = atheris.FuzzedDataProvider(data)
    ops = _ops()
    op = ops[fdp.ConsumeIntInRange(0, len(ops) - 1)]
    in_string = fdp.ConsumeUnicodeNoSurrogates(len(data) - 1)
    signal.setitimer(signal.ITIMER_REAL, _PER_INPUT_SECONDS)
    try:
        op(in_string)
    except _InputTimeout:
        pass
    except Exception as e:  # noqa: BLE001 - filter to library-defined errors only
        if not _is_library_error(e):
            raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
