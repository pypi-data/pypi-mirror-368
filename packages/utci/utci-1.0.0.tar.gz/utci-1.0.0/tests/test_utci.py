import numpy as np

from utci import es, rh_to_vp, utci_approx


class TestSaturationVaporPressure:
    """Test saturation vapor pressure calculation."""

    def test_es_at_zero_celsius(self):
        """Test es at 0°C (should be ~6.112 hPa)."""
        result = es(0.0)
        expected = 6.112  # hPa at 0°C
        assert abs(result - expected) < 0.01

    def test_es_at_20_celsius(self):
        """Test es at 20°C (should be ~23.388 hPa)."""
        result = es(20.0)
        expected = 23.388  # hPa at 20°C
        assert abs(result - expected) < 0.1

    def test_es_at_100_celsius(self):
        """Test es at 100°C (should be ~1013.25 hPa)."""
        result = es(100.0)
        expected = 1013.25  # hPa at 100°C (1 atm)
        assert abs(result - expected) < 1.0

    def test_es_at_negative_40_celsius(self):
        """Test es at -40°C."""
        result = es(-40.0)
        expected = 0.1903  # hPa at -40°C (Hardy ITS-90)
        assert abs(result - expected) < 0.01

    def test_es_array_input(self):
        """Test es with array input."""
        temps = np.array([0.0, 10.0, 20.0, 30.0])
        results = [es(t) for t in temps]
        expected = [6.112, 12.281, 23.388, 42.455]  # Approximate values
        for r, e in zip(results, expected):
            assert abs(r - e) < 0.5


class TestUTCIApprox:
    """Test UTCI approximation function."""

    def test_utci_neutral_conditions(self):
        """Test UTCI under neutral conditions."""
        # Comfortable conditions: 20°C, 50% RH, no wind, Tmrt = Ta
        ta = 20.0
        tmrt = 20.0
        va = 1.0  # 1 m/s wind
        rh = 50.0
        vp = es(ta) * rh / 100.0  # Convert RH to vapor pressure

        result = utci_approx(ta, vp, tmrt, va)
        # UTCI should be close to air temperature under neutral conditions
        assert abs(result - ta) < 5.0

    def test_utci_hot_conditions(self):
        """Test UTCI under hot conditions."""
        ta = 35.0
        tmrt = 45.0  # High radiant temperature
        va = 0.5  # Low wind
        rh = 70.0  # High humidity
        vp = es(ta) * rh / 100.0

        result = utci_approx(ta, vp, tmrt, va)
        # UTCI should be significantly higher than air temperature
        assert result > ta + 5.0

    def test_utci_cold_conditions(self):
        """Test UTCI under cold conditions."""
        ta = -10.0
        tmrt = -15.0  # Lower radiant temperature
        va = 10.0  # High wind
        rh = 80.0
        vp = es(ta) * rh / 100.0

        result = utci_approx(ta, vp, tmrt, va)
        # UTCI should be significantly lower than air temperature
        assert result < ta - 5.0

    def test_utci_parameter_bounds(self):
        """Test UTCI with parameters at their bounds."""
        # Test minimum air temperature
        ta = -50.0
        tmrt = -50.0
        va = 0.5
        vp = 0.1
        result = utci_approx(ta, vp, tmrt, va)
        assert isinstance(result, float)

        # Test maximum air temperature
        ta = 50.0
        tmrt = 50.0
        va = 17.0
        vp = 50.0
        result = utci_approx(ta, vp, tmrt, va)
        assert isinstance(result, float)

    def test_utci_tmrt_range(self):
        """Test UTCI with Tmrt at its allowed range."""
        ta = 20.0
        va = 2.0
        vp = 10.0

        # Test Tmrt 30°C below Ta
        tmrt = ta - 30.0
        result = utci_approx(ta, vp, tmrt, va)
        assert isinstance(result, float)

        # Test Tmrt 70°C above Ta
        tmrt = ta + 70.0
        result = utci_approx(ta, vp, tmrt, va)
        assert isinstance(result, float)

    def test_utci_specific_values(self):
        """Test UTCI with specific known values."""
        # Test case from literature or validation data
        ta = 25.0
        tmrt = 30.0
        va = 3.0
        rh = 60.0
        vp = es(ta) * rh / 100.0

        result = utci_approx(ta, vp, tmrt, va)
        # This should produce a specific UTCI value
        # Exact value would need to be verified against Fortran output
        assert 20.0 < result < 35.0  # Reasonable range


class TestHelperFunctions:
    """Test helper functions."""

    def test_rh_to_vp(self):
        """Test relative humidity to vapor pressure conversion."""
        ta = 20.0
        rh = 50.0

        vp = rh_to_vp(ta, rh)
        expected = es(ta) * rh / 100.0
        assert abs(vp - expected) < 0.001

    def test_rh_to_vp_edge_cases(self):
        """Test RH to VP conversion at edge cases."""
        # 0% humidity
        vp = rh_to_vp(20.0, 0.0)
        assert vp == 0.0

        # 100% humidity
        ta = 20.0
        vp = rh_to_vp(ta, 100.0)
        assert abs(vp - es(ta)) < 0.001

    def test_rh_to_vp_extreme_temperatures(self):
        """Test RH to VP conversion at extreme temperatures."""
        # Very cold
        ta = -40.0
        rh = 50.0
        vp = rh_to_vp(ta, rh)
        assert vp > 0 and vp < es(ta)

        # Very hot
        ta = 50.0
        rh = 30.0
        vp = rh_to_vp(ta, rh)
        assert vp > 0 and vp < es(ta)
