def package_price_usd(package, credit_value):
    return package * credit_value


def validate_package(value, packages):
    try:
        package = int(value)
    except (TypeError, ValueError):
        return False, "Pacote de créditos inválido."
    if package not in packages:
        return False, "Pacote de créditos inválido."
    return True, package
