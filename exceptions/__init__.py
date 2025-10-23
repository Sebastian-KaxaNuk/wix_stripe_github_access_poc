class StripeConnectionError(Exception):
    pass

class SignatureError(StripeConnectionError):
    pass
