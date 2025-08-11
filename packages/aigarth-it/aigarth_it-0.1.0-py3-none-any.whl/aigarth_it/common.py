"""Aigarth Intelligent Tissue (AIT) common tools."""

import secrets


def ternary_clamp(x: int) -> int:
    """Clamp a decimal integer number to a ternary value ([-1, 0, +1]).

    :param x: decimal number to clamp
    :return:  clamped number
    """
    match int(x):
        case 0:
            return 0
        case _:
            return 1 if x >= 1 else -1


def bitstring64_to_int(bit_str: str) -> int:
    """Convert a number, represented by a signed bit string to an integer.

    :param bit_str: bit string representation of an integer value to be converted (e.g. '00101010')
    :return:        value of the bit string in the form of integer number
    """
    len_bit_str = len(bit_str)

    if len_bit_str > 64:
        raise ValueError(f"Bit string can't hold more than 64 positions': {bit_str}")
    elif bit_str.startswith("-"):
        raise ValueError(f"Bit string can't hold symbols other than '0' and '1': {bit_str}")

    unsigned_int = int(bit_str, 2)

    mask_sign = 1 << (len_bit_str - 1)
    mask_value = mask_sign - 1

    return (unsigned_int & mask_value) - (unsigned_int & mask_sign)


def int_to_bitstring(num: int, max_bits: int = 64, const_len: bool = False) -> str:
    """Convert a signed integer number to signed bit string representation.
    NOTE. The 'two's compliment' form is used to represent negative binary numbers [1].

    Reference:
        [1] [Two's complement](https://en.wikipedia.org/wiki/Two%27s_complement)

    :param num:         signed integer number to be converted
    :param max_bits:    maximum number of bit positions that may be used to represent an integer number.
                        I.e. the following condition must be met: -2**(max_bits - 1) <= num <= 2 ** (max_bits - 1) - 1
    :param const_len:   produce bit strings of constant length equal to 'max_bits', if True, otherwise the resulting
                        bit string will take the least amount of bits required to represent the target integer number.
                        Example:
                            num=5, max_bits=8, const_len=False : 5 -> '0101'
                            num=5, max_bits=8, const_len=True : 5 -> '00000101'
                            num=-4, max_bits=8, const_len=False : -4 -> '100'
                            num=-4, max_bits=8, const_len=True : -4 -> '11111100'
    :return:            signed bit string
    """
    # Conversion won't produce correct results, if an integer being converted cannot fit into allowed number of bits
    if not (-(2 ** (max_bits - 1)) <= num <= 2 ** (max_bits - 1) - 1):
        raise ValueError(f"Number must fall into range [-2**{max_bits - 1}, 2**{max_bits - 1}-1]: {num}")

    if const_len:
        len_mask = max_bits
        # All the resulting bit strings are to have the same 'constant' length so, cropping duplicating 'negative
        # sign' bit is not to be done here.
        crop_leading_one = False
    else:
        len_mask = len(f"{num:b}".lstrip("-")) + 1
        # For negative numbers which are powers of 2 (-2, -4, -8, ...) the 'sign bit' may be safely omitted since in the
        # 'two's compliment' binary form of representing signed integers the 'sign bit' may also represent a part of
        # magnitude. E.g. '-4' has two valid binary representation: '1100' and '100' so, using the latter form is
        # preferable when the 'const_len' requirement is not applied.
        crop_leading_one = True

    mask_str = f"0b{'1' * len_mask}"
    bit_str = f"{num & int(mask_str, 2):0{len_mask}b}"

    if crop_leading_one and len(bit_str) > 2 and bit_str.startswith("11"):
        bit_str = bit_str[1:]

    return bit_str


def bitstring_to_trits(bitstring: str) -> tuple[int, ...]:
    """Convert bit string into a set of balanced trit values.

    :param bitstring:   a string representing a signed integer value in binary form (e.g. '00101010')
    :return:            a sequence of balanced trit values corresponding the input bit string.
                        Bit to trit value conversion rules:
                            binary '1' -> ternary '1'
                            binary '0' -> ternary '-1'
    """
    trits = []

    for b in str(bitstring):
        match b:
            case "1":
                trits.append(1)
            case "0":
                trits.append(-1)
            case _:
                raise ValueError(f"Invalid binary value: {b}")

    return tuple(trits)


def trits_to_bitstring(trits: tuple[int, ...]) -> str:
    """Convert a sequence of trit values to a bit string representation.

    :param trits:   a sequence of balanced trit values
    :return:        a bit string representation of input trit values
    """
    if not isinstance(trits, tuple):
        raise TypeError(f"Trits to bit string conversion: Invalid argument type: trits: {type(trits).__name__}")

    bits = []

    for t in trits:
        match int(t):
            case 1:
                bits.append("1")
            case -1:
                bits.append("0")
            case 0:
                bits.append("?")
            case _:
                raise ValueError(f"Trits to bit string conversion: Invalid ternary value: {t}")

    bitstring = "".join(bits)

    return bitstring


def random_trit_vector(size: int) -> list[int]:
    """Generate a sequence of randomly chosen balanced ternary values ([-1, 0, 1]).

    :param size:    size of the target sequence.
    :return:        list of ternary values.
    """
    trit_vector: list[int] = [secrets.choice((-1, 0, 1)) for _ in range(size)]

    return trit_vector
