def calculate_request_amount(subscription):
    return int(subscription["request_price_credits"])


def calculate_subscription_total(subscription, request_amount):
    return int(subscription["subscription_price_credits"]) + request_amount
