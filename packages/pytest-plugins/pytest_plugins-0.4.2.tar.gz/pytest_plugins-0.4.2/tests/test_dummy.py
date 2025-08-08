import pytest

parametrize = pytest.mark.parametrize(
    "param1, param2", [("A", "A"), (2, 2), (3, 3), (4, 5)]
)


class TestDummy:
    @pytest.mark.test_pass
    def test_pass(self):
        assert True

    @pytest.mark.test_fail
    def test_false(self):
        assert False, {"message": "This test is expected to fail."}

    @pytest.mark.fail2skip(reason="This test is expected to fail and be skipped.")
    def test_fail2skip(self):
        assert False, {"message": "This test is expected to fail."}

    @parametrize
    def test_with_parameters_1(self, param1, param2):
        assert param1 != param2, {
            "expected_value": param1,
            "actual_value": param2,
            "diagnostic_info": {"param1": param1, "param2": param2},
        }

    @pytest.mark.parametrize("param1, param2", [(1, 1), (2, 2), (3, 3), (4, 5)])
    def test_with_parameters_2(self, param1, param2):
        assert param1 != param2
