#!/usr/local/bin/python3
from multiprocessing.sharedctypes import Value
import atheris
import sys
import io
import os

from persian_tools import digits, ordinal_suffix, bill
from persian_tools.bank import card_number, sheba, exceptions

@atheris.instrument_func
def TestOneInput(data):
    if len(data) > 0:
        fdp = atheris.FuzzedDataProvider(data)
        opt = fdp.ConsumeInt(1)
        in_string = fdp.ConsumeUnicode(len(data)-1)
        
        if opt == 0:
            digits.convert_from_word(in_string)   
        elif opt == 1:
            ordinal_suffix.remove(in_string)
        elif opt == 2:
            digits.convert_to_fa(in_string)
        elif opt == 3:
            digits.convert_to_en(in_string)
        elif opt == 4:
            digits.convert_to_ar(in_string)




atheris.Setup(sys.argv, TestOneInput)
atheris.instrument_all()
atheris.Fuzz()