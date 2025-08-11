
def pad_to_equal_length(str1, str2):
    """Pad the shorter string with null bytes so both strings are the same length.""" #
    if len(str1) > len(str2): #
        str2 = str2.ljust(len(str1), '\x00') #
    elif len(str2) > len(str1): #
        str1 = str1.ljust(len(str2), '\x00') #
    return str1, str2 #

def xor_strings(str1, str2):
    """XOR two strings of equal length and return the result in hexadecimal.""" #
    return ''.join(format(ord(a) ^ ord(b), '02x') for a, b in zip(str1, str2)) #

def mac_manual(key, message):
    """
    A simple MAC using XOR.

    WARNING: This function is for educational purposes only and is not
    cryptographically secure. Do not use in production.
    """
    # Pad the key or message to make them the same length
    key, message = pad_to_equal_length(key, message) #

    # XOR the key and message and convert to hex
    mac_value = xor_strings(key, message) #
    return mac_value #