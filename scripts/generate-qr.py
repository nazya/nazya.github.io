#!/usr/bin/env python3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTACT_VCARD = ROOT / "contact/contact.vcf"

QR_CODES = {
    "contact": {
        "version": 5,
        "data_codewords": 108,
        "ecc_codewords": 26,
        "payload": CONTACT_VCARD.read_text(encoding="utf-8").strip(),
        "path": ROOT / "contact/contact-qr.svg",
        "title": "Nazarii Tupitsa contact QR code",
        "desc": "QR code containing a vCard with Nazarii Tupitsa contact details.",
    },
    "linkedin": {
        "version": 5,
        "data_codewords": 108,
        "ecc_codewords": 26,
        "payload": "https://www.linkedin.com/in/nazarii-tupitsa/",
        "path": ROOT / "contact/linkedin-qr.svg",
        "title": "Nazarii Tupitsa LinkedIn QR code",
        "desc": "QR code linking to Nazarii Tupitsa LinkedIn profile.",
    },
}

EXP = [0] * 512
LOG = [0] * 256
value = 1
for index in range(255):
    EXP[index] = value
    LOG[value] = index
    value <<= 1
    if value & 0x100:
        value ^= 0x11D
for index in range(255, 512):
    EXP[index] = EXP[index - 255]


def gf_mul(left, right):
    return 0 if left == 0 or right == 0 else EXP[LOG[left] + LOG[right]]


def rs_generator(degree):
    result = [0] * degree
    result[-1] = 1
    root = 1
    for _ in range(degree):
        for index in range(degree):
            result[index] = gf_mul(result[index], root)
            if index + 1 < degree:
                result[index] ^= result[index + 1]
        root = gf_mul(root, 2)
    return result


def rs_remainder(data_codewords, degree):
    generator = rs_generator(degree)
    result = [0] * degree
    for codeword in data_codewords:
        factor = codeword ^ result.pop(0)
        result.append(0)
        for index, coefficient in enumerate(generator):
            result[index] ^= gf_mul(coefficient, factor)
    return result


def append_bits(bits, value, length):
    for shift in range(length - 1, -1, -1):
        bits.append((value >> shift) & 1)


def make_codewords(payload, data_count):
    data = payload.encode("utf-8")
    bits = []
    append_bits(bits, 0b0100, 4)
    append_bits(bits, len(data), 8)
    for byte in data:
        append_bits(bits, byte, 8)
    append_bits(bits, 0, min(4, data_count * 8 - len(bits)))
    while len(bits) % 8:
        bits.append(0)
    pad_bytes = (0xEC, 0x11)
    pad_index = 0
    while len(bits) < data_count * 8:
        append_bits(bits, pad_bytes[pad_index % 2], 8)
        pad_index += 1
    if len(bits) > data_count * 8:
        raise ValueError("payload too large")
    return [sum(bits[index + bit] << (7 - bit) for bit in range(8)) for index in range(0, len(bits), 8)]


def alignment_positions(version):
    if version == 1:
        return []
    if version == 3:
        return [6, 22]
    if version == 5:
        return [6, 30]
    raise ValueError(f"unsupported QR version: {version}")


def make_qr(config):
    version = config["version"]
    size = 21 + 4 * (version - 1)
    data_codewords = make_codewords(config["payload"], config["data_codewords"])
    all_codewords = data_codewords + rs_remainder(data_codewords, config["ecc_codewords"])

    modules = [[False] * size for _ in range(size)]
    function = [[False] * size for _ in range(size)]

    def set_function(x, y, dark):
        if 0 <= x < size and 0 <= y < size:
            modules[y][x] = dark
            function[y][x] = True

    def draw_finder(center_x, center_y):
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                distance = max(abs(dx), abs(dy))
                set_function(center_x + dx, center_y + dy, distance != 2 and distance != 4)

    def draw_alignment(center_x, center_y):
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                distance = max(abs(dx), abs(dy))
                set_function(center_x + dx, center_y + dy, distance != 1)

    def reserve_format():
        coords = []
        coords += [(8, index) for index in range(6)]
        coords += [(8, 7), (8, 8), (7, 8)]
        coords += [(14 - index, 8) for index in range(9, 15)]
        coords += [(size - 1 - index, 8) for index in range(8)]
        coords += [(8, size - 15 + index) for index in range(8, 15)]
        for x, y in coords:
            set_function(x, y, False)
        set_function(8, size - 8, True)

    for center_x, center_y in ((3, 3), (size - 4, 3), (3, size - 4)):
        draw_finder(center_x, center_y)
    for index in range(8, size - 8):
        set_function(index, 6, index % 2 == 0)
        set_function(6, index, index % 2 == 0)
    for y in alignment_positions(version):
        for x in alignment_positions(version):
            near_top_left = x == 6 and y == 6
            near_bottom_left = x == 6 and y == size - 7
            near_top_right = x == size - 7 and y == 6
            if not (near_top_left or near_bottom_left or near_top_right):
                draw_alignment(x, y)
    reserve_format()

    bit_index = 0
    upward = True
    right = size - 1
    while right >= 1:
        if right == 6:
            right -= 1
        y_range = range(size - 1, -1, -1) if upward else range(size)
        for y in y_range:
            for dx in range(2):
                x = right - dx
                if not function[y][x]:
                    bit = False
                    if bit_index < len(all_codewords) * 8:
                        bit = ((all_codewords[bit_index >> 3] >> (7 - (bit_index & 7))) & 1) != 0
                    modules[y][x] = bit
                    bit_index += 1
        upward = not upward
        right -= 2

    best_matrix = choose_mask(modules, function, size)
    return best_matrix


def mask_bit(mask, x, y):
    if mask == 0:
        return (x + y) % 2 == 0
    if mask == 1:
        return y % 2 == 0
    if mask == 2:
        return x % 3 == 0
    if mask == 3:
        return (x + y) % 3 == 0
    if mask == 4:
        return (x // 3 + y // 2) % 2 == 0
    if mask == 5:
        return (x * y) % 2 + (x * y) % 3 == 0
    if mask == 6:
        return ((x * y) % 2 + (x * y) % 3) % 2 == 0
    return ((x + y) % 2 + (x * y) % 3) % 2 == 0


def format_bits(mask):
    data = (0b01 << 3) | mask
    remainder = data
    for _ in range(10):
        remainder = (remainder << 1) ^ ((remainder >> 9) * 0x537)
    return ((data << 10) | remainder) ^ 0x5412


def draw_format(matrix, mask):
    size = len(matrix)
    bits = format_bits(mask)
    for index in range(6):
        matrix[index][8] = ((bits >> index) & 1) != 0
    matrix[7][8] = ((bits >> 6) & 1) != 0
    matrix[8][8] = ((bits >> 7) & 1) != 0
    matrix[8][7] = ((bits >> 8) & 1) != 0
    for index in range(9, 15):
        matrix[8][14 - index] = ((bits >> index) & 1) != 0
    for index in range(8):
        matrix[8][size - 1 - index] = ((bits >> index) & 1) != 0
    for index in range(8, 15):
        matrix[size - 15 + index][8] = ((bits >> index) & 1) != 0
    matrix[size - 8][8] = True


def penalty(matrix):
    size = len(matrix)
    total = 0
    for rows in (matrix, list(zip(*matrix))):
        for row in rows:
            run_color = row[0]
            run_length = 1
            for value in row[1:]:
                if value == run_color:
                    run_length += 1
                else:
                    if run_length >= 5:
                        total += 3 + run_length - 5
                    run_color = value
                    run_length = 1
            if run_length >= 5:
                total += 3 + run_length - 5
    for y in range(size - 1):
        for x in range(size - 1):
            color = matrix[y][x]
            if matrix[y][x + 1] == color and matrix[y + 1][x] == color and matrix[y + 1][x + 1] == color:
                total += 3
    patterns = ([True, False, True, True, True, False, True, False, False, False, False], [False, False, False, False, True, False, True, True, True, False, True])
    for rows in (matrix, list(zip(*matrix))):
        for row in rows:
            for index in range(size - 10):
                chunk = list(row[index:index + 11])
                if chunk == patterns[0] or chunk == patterns[1]:
                    total += 40
    dark = sum(1 for row in matrix for value in row if value)
    total += (abs(dark * 20 - size * size * 10) // (size * size)) * 10
    return total


def choose_mask(modules, function, size):
    best = None
    for mask in range(8):
        matrix = [row[:] for row in modules]
        for y in range(size):
            for x in range(size):
                if not function[y][x] and mask_bit(mask, x, y):
                    matrix[y][x] = not matrix[y][x]
        draw_format(matrix, mask)
        score = penalty(matrix)
        if best is None or score < best[0]:
            best = (score, matrix)
    return best[1]


def write_svg(config, matrix):
    size = len(matrix)
    quiet_zone = 4
    view_size = size + quiet_zone * 2
    parts = []
    for y, row in enumerate(matrix):
        for x, dark in enumerate(row):
            if dark:
                parts.append(f"M{x + quiet_zone},{y + quiet_zone}h1v1h-1z")
    config["path"].write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_size} {view_size}" role="img" aria-labelledby="title desc">\n'
        f'  <title id="title">{config["title"]}</title>\n'
        f'  <desc id="desc">{config["desc"]}</desc>\n'
        f'  <path fill="#000" d="{" ".join(parts)}"/>\n'
        f'</svg>\n',
        encoding="utf-8",
    )


def main():
    for name, config in QR_CODES.items():
        matrix = make_qr(config)
        write_svg(config, matrix)
        print(f'{name}: wrote {config["path"].relative_to(ROOT)}')


if __name__ == "__main__":
    main()
