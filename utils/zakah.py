def calculate_zakah(amount: float, type: str = "gold") -> dict:
    """Calculate Zakah based on amount and type."""
    NISAB_GOLD = 85  # grams
    NISAB_SILVER = 595  # grams
    GOLD_PRICE_PER_GRAM = 80  # approximate price in USD
    SILVER_PRICE_PER_GRAM = 0.8  # approximate price in USD
    
    if type == "gold":
        nisab_value = NISAB_GOLD * GOLD_PRICE_PER_GRAM
    elif type == "silver":
        nisab_value = NISAB_SILVER * SILVER_PRICE_PER_GRAM
    elif type == "cash":
        nisab_value = NISAB_SILVER * SILVER_PRICE_PER_GRAM  # Use silver nisab for cash
    else:
        return {"error": "Invalid type. Use: gold, silver, or cash"}
    
    zakah_rate = 0.025  # 2.5%
    zakah_amount = amount * zakah_rate if amount >= nisab_value else 0
    
    return {
        "amount": amount,
        "type": type,
        "nisab_value": nisab_value,
        "zakah_amount": zakah_amount,
        "zakah_rate": "2.5%",
        "eligible": amount >= nisab_value,
    }
