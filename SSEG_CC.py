# Author: Ember Ipek
#
# 7/6/2026
#
# Values for common cathode SSEG displays
# To do: support for different numbers of digits

import machine
import utime

SEG_EN = {0: (1,1,1,1,1,1,0),
          1: (0,1,1,0,0,0,0),
          2: (1,1,0,1,1,0,1),
          3: (1,1,1,1,0,0,1),
          4: (0,1,1,0,0,1,1),
          5: (1,0,1,1,0,1,1),
          6: (1,0,1,1,1,1,1),
          7: (1,1,1,0,0,0,0),
          8: (1,1,1,1,1,1,1),
          9: (1,1,1,1,0,1,1)}

DIG_EN = {0: (0,1,1),
          1: (1,0,1),
          2: (1,1,0),
#           3: (1,1,1,0)
          }

def get_sseg_values(value=int, digit=int):
    '''
    Args:
        value: lookup key for SEG_EN
               valid values: 0 - 9
        digit: which sseg digit to enable
               valid values: 0, 1, 2, 3
          
    Returns:
        tuple with digit to enable
        tuple with segments to enable
    '''
    
    segments = SEG_EN.get(value)
    digits = DIG_EN.get(digit)
    
    return segments, digits

def show_sseg(num=int, segments=tuple, digits=tuple):
    ones = num % 10
    tens = (num // 10) % 10
    hundreds = (num // 100) % 10
    thousands = (num // 1000) % 10
    
    seg, dig = get_sseg_values(ones, 2)
    for i in range(len(seg)):
        segments[i].value(seg[i])
    for i in range(len(dig)):
        digits[i].value(dig[i])
    utime.sleep_ms(2)
    
    if(tens > 0):
        seg, dig = get_sseg_values(tens, 1)
        for i in range(len(seg)):
            segments[i].value(seg[i])
        for i in range(len(dig)):
            digits[i].value(dig[i])
    utime.sleep_ms(5)
    
    if(hundreds > 0):
        seg, dig = get_sseg_values(hundreds, 0)
        for i in range(len(seg)):
            segments[i].value(seg[i])
        for i in range(len(dig)):
            digits[i].value(dig[i])
    utime.sleep_ms(2)
    
#     if(thousands > 0):
#         seg, dig = get_sseg_values(thousands, 0)
#         for i in range(len(seg)):
#             segments[i].value(seg[i])
#         for i in range(len(dig)):
#             digits[i].value(dig[i])
#     utime.sleep_ms(1)
    
    return
