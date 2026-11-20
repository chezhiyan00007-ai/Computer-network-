def text_to_bits(message):
    return ''.join(format(ord(ch), '08b') for ch in message)


def parity_bit(bits):
    return str(bits.count('1') % 2)  # even parity


def check_parity(bits, parity):
    return (bits + parity).count('1') % 2 == 0


def pad_words(bits, size=16):
    if len(bits) % size:
        bits += '0' * (size - len(bits) % size)
    return [int(bits[i:i + size], 2) for i in range(0, len(bits), size)]


def checksum_value(bits):
    total = 0
    for word in pad_words(bits, 16):
        total += word
        total = (total & 0xFFFF) + (total >> 16)
    return (~total) & 0xFFFF


def check_checksum(bits, checksum):
    total = checksum
    for word in pad_words(bits, 16):
        total += word
        total = (total & 0xFFFF) + (total >> 16)
    return total == 0xFFFF


def xor_division(dividend, divisor):
    work = list(dividend)
    n = len(divisor)
    for i in range(len(work) - n + 1):
        if work[i] == '1':
            for j in range(n):
                work[i + j] = '0' if work[i + j] == divisor[j] else '1'
    return ''.join(work[-(n - 1):]) if n > 1 else ''


def crc_remainder(bits, generator='1101'):
    return xor_division(bits + '0' * (len(generator) - 1), generator)


def check_crc(bits, remainder, generator='1101'):
    return set(xor_division(bits + remainder, generator)) <= {'0'}


def flip_bit(bits, position):
    data = list(bits)
    index = position - 1
    if index < 0 or index >= len(data):
        raise ValueError("Bit position is outside the data length.")
    data[index] = '1' if data[index] == '0' else '0'
    return ''.join(data)


def main():
    print("NETWORK ERROR DETECTION AND LAN MONITOR")
    message = input("Enter data message: ")
    if not message:
        print("Message cannot be empty.")
        return

    bits = text_to_bits(message)
    print("Sender binary data:", bits)
    print("Data length:", len(bits), "bits")

    method = input("Choose method (parity/checksum/crc): ").strip().lower()
    if method not in ("parity", "checksum", "crc"):
        print("Invalid method.")
        return

    if method == "parity":
        check_value = parity_bit(bits)
        print("Generated even-parity bit:", check_value)
    elif method == "checksum":
        check_value = checksum_value(bits)
        print("Generated 16-bit checksum:", format(check_value, "016b"))
    else:
        check_value = crc_remainder(bits)
        print("CRC remainder:", check_value)

    received = bits
    inject = input("Inject one-bit error? (y/n): ").strip().lower()
    if inject == 'y':
        try:
            position = int(input(
                "Enter data bit position to flip (1 to " + str(len(bits)) + "): "
            ))
            received = flip_bit(bits, position)
        except (ValueError, TypeError):
            print("Invalid bit position.")
            return

    print("Receiver binary data:", received)

    if method == "parity":
        passed = check_parity(received, check_value)
    elif method == "checksum":
        passed = check_checksum(received, check_value)
    else:
        passed = check_crc(received, check_value)

    print("\n--- TRANSMISSION REPORT ---")
    print("Method:", method.upper())
    print("Data bits:", len(bits))
    print("Error injected:", "Yes" if received != bits else "No")
    print("Receiver check:", "PASSED" if passed else "FAILED")
    print("Transmission status:",
          "SUCCESSFUL" if passed else "UNSUCCESSFUL")


if __name__ == "__main__":
    main()
