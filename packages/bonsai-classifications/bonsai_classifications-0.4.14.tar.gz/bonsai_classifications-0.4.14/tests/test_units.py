from decimal import Decimal

from classifications._pint_units import get_unit_registry


def test_units():
    def decimal_almost_equal(
        a: Decimal, b: Decimal, tol: Decimal = Decimal("1e-6")
    ) -> bool:
        return abs(a - b) <= tol

    ureg = get_unit_registry()

    a = 1000000 * ureg.DKK_2017
    a_result = a.to("Meuro_2016")

    b = 1 * ureg.t
    b_result = b.to("tonnes")

    c = 1 * ureg.kWh
    c_result = c.to("TJ")

    assert (
        decimal_almost_equal(a_result.m, Decimal(0.1416874676815668658358755478))
        == True
    )
    assert a_result.u == "Meuro_2016"
    assert decimal_almost_equal(b_result.m, Decimal(1)) == True
    assert b_result.u == "tonnes"
    assert decimal_almost_equal(c_result.m, Decimal(0.000003600)) == True
    assert c_result.u == "terajoule"
