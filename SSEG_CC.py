import machine

SEG_EN = {'0': (1,1,1,1,1,1,0,0),
          '1': (0,1,1,0,0,0,0,0),
          '2': (1,1,0,1,1,0,1,0),
          '3': (1,1,1,1,0,0,1,0),
          '4': (0,1,1,0,0,1,1,0),
          '5': (1,0,1,1,0,1,1,0),
          '6': (1,0,1,1,1,1,1,0),
          '7': (1,1,1,0,0,0,0,0),
          '8': (1,1,1,1,1,1,1,0),
          '9': (1,1,1,1,0,1,1,0),
          'dp': (0,0,0,0,0,0,0,1)}

DIG_EN = {0: (0,1,1,1),
          1: (1,0,1,1),
          2: (1,1,0,1),
          3: (1,1,1,0)}

def show_sseg(value, digit):
    '''
    Args:
        value: lookup key for SEG_EN
        digit: which sseg digit to enable
               valid values: 0, 1, 2, 3
          
    Returns:
        tuple with digit to enable
        tuple with segments to enable
    '''
    
    segments = SEG_EN.get(value)
    digits = DIG_EN.get(digit)
    
    return segments, digits
