#!/usr/bin/env python

"""
LICENSE

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import fileinput
import texttable
import decimal

def main():
    rows_raw = [ process(line) for line in fileinput.input() if line.strip() ]
    rows = [ format_line(row) for row in unique_rows(rows_raw) ]
    rows.reverse()
    print format_table(rows)
    print
    print '%d entries total.' % len(rows)
    print

def format_table(rows):
    table = texttable.Texttable(max_width=0)
    table.header(('dBV', 'dBu', 'Volts RMS', 'Volts peak-to-peak'))
    table.add_rows(rows, header=False)
    table.set_cols_align(['r', 'r', 'r', 'r'])
    return table.draw()

def unique_rows(rows):
    def discriminant(row):
        return (row[0], row[1], row[3], row[5])

    def update(old, new):
        return (
            old[0], old[1], old[2] or new[2], old[3], old[4] or new[4], old[5]
            )

    def split_info(info_value):
        parts = info_value.split(' = ')

        if len(parts) == 1:
            info, value = None, parts[0]
        elif len(parts) == 2:
            info, value = parts
        else:
            raise
        return info, value

    def join_parts(info, value):
        left = ''
        if info is not None:
            left = info + ' = '
        return left + value

    def join_info(row):
        return \
            ( row[0]
            , row[1]
            , join_parts(row[2], row[3])
            , join_parts(row[4], row[5])
            )

    old = None

    for row in rows:
        dBV, dBu, descrms_Vrms, descpp_Vpp = row
        descrms, Vrms = split_info(descrms_Vrms)
        descpp,  Vpp  = split_info(descpp_Vpp)

        new = (dBV, dBu, descrms, Vrms, descpp, Vpp)
        if old is None:
            old = new
            continue

        if discriminant(old) == discriminant(new):
            old = update(old, new)
            continue
        else:
            yield join_info(old)
            old = new

    yield join_info(old)


def format_line(line):
    ''' add unit names '''
    dBV, dBu, Vrms, Vpp = line
    return (dBV + ' dBV', dBu + ' dBu', Vrms + ' Vrms', Vpp + ' Vpp')

def process(line):
    if '    ' == line[0:4]:
        return process_vpptable_exp(line)
    elif '   ' == line[0:3]:
        return process_vtable_exp(line)
    else:
        return process_other(line)

def split(line):
    return [ field.strip() for field in line.lstrip().split(',') ]

def short_form(num):
    float_precision = 5
    f_format = "%%.%df" % float_precision
    f = "%.5f" % num
    e = "%.2e" % num

    if int(num) == num:
        ''' Don't put zeros after exact integers. '''
        return "%d" % num

    unacceptable_float_zeros = int((1.0 * float_precision + 1) / 2)
    float_test_digits = unacceptable_float_zeros + 2
    if all([c in '.0' for c in f[0:float_test_digits]]):
        ''' don't return values which truncate down to 0.0000... '''
        return e
    if len(f) < len(e) + 2:
        return f
    return e

def short(string):
    ''' Returns a short string representation of a number. '''
    return short_form(
        decimal.Decimal(string).normalize()
        )

def process_other(line):
    dBV, dBu, Vrms, Vpp = [
        short(num)
        for num in split(line)
        ]
    return (dBV, dBu, Vrms, Vpp)

def process_vtable_exp(line):
    dBV, dBu, desc_Vrms, Vpp = split(line)
    desc, Vrms = [ x.strip() for x in desc_Vrms.split('=') ]
    return (short(dBV), short(dBu), desc + ' = ' + short(Vrms), short(Vpp))

def process_vpptable_exp(line):
    dBV, dBu, Vrms, desc_Vpp = split(line)
    desc, Vpp = [ x.strip() for x in desc_Vpp.split('=') ]
    return (short(dBV), short(dBu), short(Vrms), desc + ' = ' + short(Vpp))

if '__main__' == __name__:
    main()
