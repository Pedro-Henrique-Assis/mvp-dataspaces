def only_digits(value):
    return "".join(char for char in value or "" if char.isdigit())


def check_digit(digits, weights):
    total = sum(int(digit) * weight for digit, weight in zip(digits, weights))
    rest = total % 11
    return "0" if rest < 2 else str(11 - rest)


def is_valid_cnpj(cnpj):
    cnpj = only_digits(cnpj)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False
    first = check_digit(cnpj[:12], [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    second = check_digit(cnpj[:12] + first, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return cnpj[12:] == first + second
