import json
import re
import unicodedata

from werkzeug.security import generate_password_hash

from app.repositories.admins import get_by_email as get_admin_by_email
from app.repositories.organizations import (
    create_with_api,
    get_by_cnpj as get_organization_by_cnpj,
    get_by_email as get_organization_by_email,
)


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


SECTORS = ["transport", "logistics", "retail", "industry", "other"]
ROLES = ["consumer", "provider", "both"]
MAX_RESPONSE_BYTES = 20 * 1024


def valid_email(email):
    local, _, domain = email.partition("@")
    return bool(local) and "." in domain and not domain.startswith(".") and not domain.endswith(".")


def validate_organization(form):
    errors = []
    required = {
        "name": "Razão social",
        "cnpj": "CNPJ",
        "email": "E-mail",
        "password": "Senha",
        "contact_name": "Responsável",
    }
    for field, label in required.items():
        if not form.get(field, "").strip():
            errors.append(f"{label} é obrigatório.")

    if form.get("cnpj", "").strip() and not is_valid_cnpj(form["cnpj"]):
        errors.append("CNPJ inválido.")
    if form.get("email", "").strip() and not valid_email(form["email"].strip()):
        errors.append("E-mail inválido.")

    password = form.get("password", "")
    if password and len(password) < 8:
        errors.append("A senha deve ter pelo menos 8 caracteres.")
    if password != form.get("password_confirmation", ""):
        errors.append("A confirmação da senha não confere.")

    if form.get("sector") not in SECTORS:
        errors.append("Setor inválido.")
    if form.get("role") not in ROLES:
        errors.append("Papel inválido.")
    if not form.get("accepted_terms"):
        errors.append("É necessário aceitar os termos de uso.")

    limits = {
        "name": ("Razão social", 120),
        "email": ("E-mail", 160),
        "contact_name": ("Responsável", 120),
        "description": ("Descrição", 255),
        "website": ("Site", 160),
    }
    for field, (label, size) in limits.items():
        if len(form.get(field, "").strip()) > size:
            errors.append(f"{label} deve ter até {size} caracteres.")
    return errors


def validate_api(form):
    errors = []
    name = form.get("api_name", "").strip()
    description = form.get("api_description", "").strip()
    if not name:
        errors.append("Nome da API é obrigatório.")
    elif len(name) > 120:
        errors.append("Nome da API deve ter até 120 caracteres.")
    if not description:
        errors.append("Descrição da API é obrigatória.")
    elif len(description) > 255:
        errors.append("Descrição da API deve ter até 255 caracteres.")
    return errors


def validate_policy(form):
    errors = []
    purpose = form.get("policy_purpose", "").strip()
    if not purpose:
        errors.append("Finalidade de uso é obrigatória.")
    elif len(purpose) > 255:
        errors.append("Finalidade de uso deve ter até 255 caracteres.")

    days = form.get("policy_retention_days", "").strip()
    if not (days.isascii() and days.isdigit()) or not 1 <= int(days) <= 3650:
        errors.append("O prazo de retenção deve ser um número inteiro entre 1 e 3650 dias.")

    if len(form.get("policy_notes", "").strip()) > 500:
        errors.append("Observações devem ter até 500 caracteres.")
    return errors


def make_slug(name):
    text = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-z0-9]+", "-", text.lower())
    return text[:60].strip("-")


def response_fields(data):
    if isinstance(data, dict):
        return set(data)
    fields = set()
    for item in data:
        fields |= set(item)
    return fields


def parse_response(text, plan):
    if len(text.encode("utf-8")) > MAX_RESPONSE_BYTES:
        return None, f"A resposta do plano {plan} deve ter até 20 KB."
    try:
        data = json.loads(text)
    except ValueError:
        return None, f"A resposta do plano {plan} não é um JSON válido."
    is_object = isinstance(data, dict) and data
    is_list = isinstance(data, list) and data and all(isinstance(item, dict) and item for item in data)
    if not is_object and not is_list:
        return None, f"A resposta do plano {plan} deve ser um objeto ou uma lista não vazia de objetos."
    return data, None


def validate_responses(basic_text, premium_text):
    basic, basic_error = parse_response(basic_text or "", "básico")
    premium, premium_error = parse_response(premium_text or "", "premium")
    errors = [error for error in (basic_error, premium_error) if error]
    if errors:
        return errors

    basic_fields = response_fields(basic)
    premium_fields = response_fields(premium)
    if not basic_fields <= premium_fields:
        return ["O plano premium deve conter todos os campos do plano básico."]
    if premium_fields == basic_fields:
        return ["O plano premium deve ter pelo menos um campo a mais que o básico."]
    return []


def register_organization(form):
    errors = validate_organization(form)
    if errors:
        return False, errors

    email = form["email"].strip().lower()
    cnpj = only_digits(form["cnpj"])
    if get_organization_by_email(email) or get_admin_by_email(email):
        errors.append("E-mail já cadastrado.")
    if get_organization_by_cnpj(cnpj):
        errors.append("CNPJ já cadastrado.")
    if errors:
        return False, errors

    organization = {
        "name": form["name"].strip(),
        "cnpj": cnpj,
        "email": email,
        "password_hash": generate_password_hash(form["password"]),
        "did": f"did:example:{cnpj}",
        "sector": form["sector"],
        "role": form["role"],
        "contact_name": form["contact_name"].strip(),
        "description": form.get("description", "").strip() or None,
        "website": form.get("website", "").strip() or None,
    }
    create_with_api(organization, None)
    return True, []
