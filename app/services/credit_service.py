import math
import secrets

from app.repositories.pix_charges import confirm, create, expire_overdue, find_open, get_by_code


def package_price_usd(package, credit_value):
    return package * credit_value


def parse_page(value):
    if value is None or value == "":
        return True, 1
    if not value.isdecimal():
        return False, None
    try:
        page = int(value)
    except ValueError:
        return False, None
    if page < 1:
        return False, None
    return True, page


def count_pages(total_items, per_page):
    return max(1, math.ceil(total_items / per_page))


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


def confirm_top_up(organization_id, code):
    expire_overdue(organization_id)
    charge = get_by_code(organization_id, code)
    if charge is None:
        return "not_found", ""
    result = confirm(organization_id, code, f"Recarga via PIX simulado · {code}")
    messages = {
        "paid": f"Pagamento simulado confirmado. +{charge['credits']} créditos.",
        "already_paid": "Esta cobrança já foi confirmada. Os créditos foram adicionados uma única vez.",
        "expired": "Esta cobrança expirou. Gere uma nova.",
    }
    return result, messages.get(result, "")
