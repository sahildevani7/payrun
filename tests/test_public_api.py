import payrun


def test_version_is_exported():
    assert payrun.__version__ == "0.1.0"


def test_top_level_exports_are_the_documented_surface():
    assert set(payrun.__all__) == {
        "CURRENCY_EXPONENTS",
        "Clock",
        "FixedClock",
        "Hours",
        "Money",
        "Rate",
        "RoundingMode",
        "SystemClock",
        "__version__",
        "allocate",
        "round_half_even",
        "round_half_up",
    }


def test_every_exported_name_is_importable_from_top_level():
    for name in payrun.__all__:
        assert hasattr(payrun, name)
