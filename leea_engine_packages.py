"""Konfigurasi pelan langganan SEA Bot."""


def get_packages():
    """Pulangkan jadual pelan baharu untuk setiap instance enjin."""
    return {
        "Basic Plan": {"setup_fee_one_off": 149.00, "monthly_fee": 130.00},
        "Pro-Plan": {"setup_fee_one_off": 499.00, "monthly_fee": 130.00},
        "Advance-Plan": {"setup_fee_one_off": 999.00, "monthly_fee": 130.00},
        "Custom Plan": {"setup_fee_one_off": "Rundingan Teknikal", "monthly_fee": 130.00},
    }