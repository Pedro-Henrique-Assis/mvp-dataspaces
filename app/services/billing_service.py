from decimal import Decimal


def calculate_request_amount(subscription):
    return Decimal(str(subscription["request_price_usd"]))


def calculate_subscription_total(subscription, request_amount):
    fixed = Decimal(str(subscription["subscription_price_usd"]))
    return fixed + request_amount