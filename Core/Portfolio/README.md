#=======================
# Portfolio Module
#=======================
Chức năng chính: Quản lý toàn bộ kế toán
Import:
Input: PositionSnapshot, TimeSlice, UserConfig
Output: PortfolioSnapshot

Pipeline: tại bar t
1. Nhận PositionSnapshot, TimeSlice từ Orchestrator
2. Update realized_pnl
3. Update balance
4. Update equity
5. Update used_margin
6. Update free_margin
7. Trả PortfolioSnapshot


Portfolio

realized_pnl
balance:
equity:
used_margin:
free_margin:
