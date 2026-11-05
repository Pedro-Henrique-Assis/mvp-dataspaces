import secrets


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


def fake_pix_code(organization_id, package):
    return f"00020126SIMULACAO-DATASPACE-{organization_id}-{package}-{secrets.token_hex(4).upper()}"
