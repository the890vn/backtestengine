#=======================
# Position Module
#=======================
Chức năng chính: Quản lý Position
Import: RunConfig, SymbolMetadata
Input: OrderFill, TimeSlice
Output: PositionSnapshot

Pipeline: tại bar t
1. Nhận OrderFill, TimeSlice từ Orchestrator
2. Xử lý order_type = Exit trước
- Trừ quantity theo quantity của OrderFill order_type = Exit
3. Xử lý order_type = Entry
- Cộng quantity theo quantity của OrderFill order_type = Entry
4. Lấy giá open của TimeSlice để tính unrealized_pnl
5. Trả PositionSnapshot


Position

position_id:
position_side: LONG | SHORT áp dụng từ RunConfig trước khi vào backtest loop
entry_order_side: BUY | SELL
symbol:
net_quantity:
avg_entry_price:
unrealized_pnl:
realized_pnl_delta: