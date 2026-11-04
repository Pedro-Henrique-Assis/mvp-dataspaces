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
