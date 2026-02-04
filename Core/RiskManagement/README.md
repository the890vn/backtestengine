
#=======================
# Risk Management Module
#=======================
Chức năng chính: kiểm tra Liquidation, Stop Loss, Take Profit của position
Import:
Input: PositionSnapshot, PortfolioSnapshot, StrategySpec (sl_price, tp_price), TimeSlice, RunConfig
Output: OrderIntent, RiskSnapshot

Pipeline: tại bar t:
1. Nhận PositionSnapshot, PortfolioSnapshot, StrategySpec (sl_price, tp_price), TimeSlice, RunConfig từ Orchestrator
2. Tính maintenance_margin
3. So sánh nếu equity <= maintenance_margin thì trả OrderInten intent_type = Exit, reason = LIQUIDATION
4. Nếu Liquidation bị trigger thì không cần xét sl_price và tp_price nữa
5. Gắn True cho is_liquidation ở bar tiếp theo -> Orchestrator sẽ kiểm tra nếu is_liquidation = True sẽ dừng backtest
6. Update sl_price, tp_price theo StrategySpec
7. Kiểm tra sl_price nếu hit thì trả OrderIntent intent_type = Exit, reason = STOP LOSS nếu sl_price bị trigger thì không cần xét tp_price nữa (nếu entry_order_side = BUY thì trigger = low - spread/2. Nếu entry_order_side = SELL thì trigger = high + spread/2)
8. Kiểm tra tp_price nếu hit thì trả OrderIntent intent_type = Exit, reason = TAKE PROFIT (nếu entry_order_side = BUY thì trigger = high 


RiskSnapshot

timestamp:
maintenance_margin_ratio: RunConfig
maintenance_margin:
equity:
is_liquidation: bool
sl_price:
tp_price:


OrderIntent

intent_type: Exit
intent_id:
position_id: nhận từ PositionSnapshot
symbol: nhận từ PositionSnapshot
order_side: ngược lại với entry_order_side từ PositionSnapshot
intent_price: = sl_price hoặc tp_price hoặc để trống nếu reason là LIQUIDATION
quantity: nhận từ PositionSnapshot
reason: LIQUIDATION | STOP LOSS | TAKE PROFIT