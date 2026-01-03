from app.operations.financial import calculate_bond, calculate_wacc

def test_bond_logic():
    # Premium Bond: Coupon (5%) > Market (4%) -> Price > 1000
    price = calculate_bond(1000, 0.05, 0.04, 10)
    assert price > 1000.0

def test_wacc_logic():
    # Simple WACC: 50/50 split, 10% equity cost, 0% debt cost
    # WACC should be 5%
    wacc = calculate_wacc(100, 100, 0.10, 0.0, 0.0)
    assert wacc == 0.05
