#=======================
# Fill Module
#=======================
Chức năng chính: nhận Order từ Orchestrator -> Fill -> trả OrderFill
Import: SpreadModel, SlippageModel, RoundModel, SymbolMetadata
Input: Order, TimeSlice
Output: OrderFill, OrderFillSnapshot

Pipeline: tại bar t
1. Nhận Order, TimeSlice từ Orchestrator
2. Xử lý Order có order_type = Exit trước theo quy tắc:
reason: LIQUIDATION | STOP LOSS | STRATEGY
- BUY fill_price = intent_price hoặc open (nếu có gap qua intent_price hoặc intent_price của Order để trống) + spread/2 + slippage
- SELL fill_price = intent_price hoặc open (nếu có gap qua intent_price hoặc intent_price của Order để trống) - spread/2 - slippage

reason: TAKE PROFIT
- fill_price = intent_price hoặc open (nếu có gap qua intent_price) không spread không slippage

3. Xử lý Order có intent_type = Entry
- BUY fill_price = open + spread/2 + slippage
- SELL fill_price = open - spread/2 - slippage

4. Gọi RoundModel để round fill_price theo SymbolMetadata
5. Trả OrderFill


OrderFill

order_type: Exit | Entry
order_id:
position_id:
symbol:
order_side: BUY | SELL
fill_price:
quantity: