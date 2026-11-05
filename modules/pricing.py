def calculate_totals(quantity, price_per_product, discount, is_rush_order):
    subtotal = quantity * price_per_product
    discount_amount = subtotal * (discount / 100)
    discounted_total = subtotal - discount_amount

    if is_rush_order:
        rush_fee = round(discounted_total * 0.2, 2)
    else:
        rush_fee = 0

    total_price = round(discounted_total + rush_fee, 2)
    return round(subtotal, 2), rush_fee, total_price
