import secrets

from app.repositories.pix_charges import create, expire_overdue, find_open


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


def open_top_up(organization_id, value, packages, credit_value, minutes):
    valid, package = validate_package(value, packages)
    if not valid:
        return False, package
    expire_overdue(organization_id)
    code = find_open(organization_id, package)
    if code is None:
        code = fake_pix_code(organization_id, package)
        create(organization_id, code, package, package_price_usd(package, credit_value), minutes)
    return True, code
