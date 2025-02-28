def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


if __name__ == '__main__':
    print(rgb_to_hex(255, 0, 0))