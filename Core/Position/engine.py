signed_qty = quantity if order_side == BUY else -quantity
old_qty = self.net_quantity

# Case 1: mở mới
if old_qty == 0:
    self.net_quantity = signed_qty
    self.avg_entry_price = fill_price
    return 0.0

# Case 2: cùng chiều -> add
if old_qty * signed_qty > 0:
    new_qty = old_qty + signed_qty
    self.avg_entry_price = (
        self.avg_entry_price * abs(old_qty)
        + fill_price * abs(signed_qty)
    ) / abs(new_qty)
    self.net_quantity = new_qty
    return 0.0

# Case 3: ngược chiều -> close (partial / full)
closing_qty = abs(signed_qty)

if closing_qty > abs(old_qty):
    raise ValueError("Flip position is not allowed")

closed_qty = closing_qty

realized_pnl_delta = (
    closed_qty
    * (fill_price - self.avg_entry_price)
    * (1 if old_qty > 0 else -1)
)

new_qty = old_qty + signed_qty
self.net_quantity = new_qty

if new_qty == 0:
    self.avg_entry_price = None

return realized_pnl_delta
