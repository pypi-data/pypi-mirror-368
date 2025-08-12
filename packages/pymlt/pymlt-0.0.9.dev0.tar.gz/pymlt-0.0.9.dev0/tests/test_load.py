"""
example commands:

pytest . -v  # verbose
pytest . -q  # quiet
pytest . -x  # stops execution after first fail
pytest path_to_file.py  # runs only this specific test module
pytest path_to_file.py::TestClass::test_function  # runs specific test function
pytest -k "TestClass"  # search for function with keyword

"""


def test_pytest():
    """test pytest is working"""
    assert 1 == 1, "should be 1"


# from pymlt import load


# def test_one():
#     assert 1 == 1, "should be 1"
#
#
# class TestPenguins(object):
#     def test_size(self):
#
#         df = load.penguins(30)
#         X = df.filter(like="feature_")
#         y = df["label"]
#
#         assert len(X) > 0, "X is empty"
#         assert len(y) > 0, "y is empty"
#         assert len(X) == len(y), "X and y do not have same length"
#
#     def test_missing(self):
#
#         df = load.penguins(30)
#         X = df.filter(like="feature_")
#         y = df["label"]
#
#         assert X.isna().values.sum() == 0, "X contains missings"
#         assert y.isna().values.sum() == 0, "y contains missings"
#
#         assert "feature_bill_length_mm" in X.columns
#         assert len(X.columns) > 2
#
#     @pytest.mark.xfail(reason="using tdd; function not yet implemented")
#     def test_expect_to_fail(self):
#         """ """
#         assert 1 == 2
#
#     @pytest.mark.skipif(True, reason="e.g. skip if user has old py version")
#     def test_skipp(self):
#         assert 1 == 2


# class TestData(object):
#     # bundle tests per function in a class
#     #  use Test..., CamelCase, and object as argument
#
#     def test_columns(self):
#         df = make_data()
#         assert "feature_0" in df.columns
#         assert len(df.columns) > 2
#
#     def test_missing(self):
#         df = make_data(missing_data=True)
#         assert df.isna().sum().sum() > 0
#

#
#
# def test_approx():
#     actual = np.array([0.2 + 0.2])
#     expected = np.array([0.1 + 0.3])
#     message = f"test should return {expected}, but returned {actual}"
#     # use pytest.approx to mitigate rounding errors
#     assert actual == pytest.approx(expected), message
#     assert isinstance(1, int)
#
#
# def test_exception_error():
#     # check if a function raises the appropriate ValueError
#     # context manager passes if ValueError is raised
#     # context manager fails if no ValueError is raised
#     with pytest.raises(ValueError) as exception_info:  # store exception
#         raise ValueError("Silence me!")
#     assert exception_info.match("Silence me!")  # check expected error message
#
#     with pytest.raises(AssertionError):
#         assert 2 + 2 == 5
#
#
# # @pytest.mark.xfail(reason="using tdd; function not yet implemented")
# # def test_expect_to_fail():
# #     assert 1 == 2
#
#
# # @pytest.mark.skipif(True, reason="e.g. skip if user has old py version")
# # def test_skipp():
# #     assert 1 == 2
#
#
# # Add a decorator to make this function a fixture
# @pytest.fixture
# def path_to_csv(tmpdir):  # tmpdir argument to setup and teardown a temp dir
#     # setup
#     df = pd.DataFrame({"a": [1, 2, 3, 4]})
#     path = tmpdir.join("bla.csv")
#     df.to_csv(path, sep=",", header=True)
#     yield path
#     # teardown after asserts
#     del df
#     # no need to delete tmpdir
#
#
# def bar(df):
#     df["b"] = df["a"] * 2
#     return df
#
#
# def test_add_column(path_to_csv):
#     df = pd.read_csv(path_to_csv)
#     result = bar(df)
#     assert result["b"].max() == 8
#
#
# def times_two(x):
#     return x * 2
#
#
# # check for normal, bad, and special / boundary arguments
# @pytest.mark.parametrize(
#     "bla, bly",
#     [
#         (1, 2),
#         (2, 4),
#         (3, 6),
#     ],
# )
# def test_times_two(bla, bly):
#     actual = times_two(bla)
#     expected = bly
#     message = f"test should return {expected}, but returned {actual}"
#     assert actual == expected, message
