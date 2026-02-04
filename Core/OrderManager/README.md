#=======================
# Order Manager Module
#=======================
Chức năng chính: nhận OrderIntent từ Orchestrator -> Validate -> tạo Order
Import: RequireMarginCalculator
Input: OrderIntent, PortfolioSnapshot(free_margin)
Output: Order, OrderSnapshot

Pipeline: tại bar t
1. Nhận OrderIntent, PortfolioSnapshot(free_margin) từ Orchestrator
2. Xử lý OrderIntent có intent_type = Exit trước -> nếu có reason = LIQUIDATION thì tạo Order và gắn status ACCEPTED -> gắn status REJECTED cho toàn bộ OrderIntent khác với reason: LIQUIDATION
- Xử lý OrderIntent có intent_type = Exit khác -> gắn status ACCEPTED với reason theo OrderIntent
3. Xử lý OrderIntent có intent_type = Entry:
- Gọi RequireMarginCalculator để tính require margin cho intent_type = Entry
- So sánh require margin với PortfolioSnapshot(free_margin)
- Nếu đủ điều kiện thì tạo Order -> gắn status ACCEPTED, reason tương ứng với OrderIntent
- Nếu không đủ điều kiện thì gắn status REJECTED reason: "Not enough require margin"
4. Trả Order có status ACCEPTED
5. Trả OrderSnapshot gồm cả ACCEPTED và REJECTED Order (để Audit, Logging, Debug)


Order

order_type: Exit | Entry
order_id:
position_id:
symbol:
order_side:
intent_price:
quantity:
reason: LIQUIDATION | STOP LOSS | TAKE PROFIT | STRATEGY | Not enough require margin
status: ACCEPTED | REJECTED