
## Unit testing

[link to course page](https://campus.datacamp.com/courses/unit-testing-for-data-science-in-python/)

- unit test = test pieces of code, e.g. a function or class
- integration test = test full code base

argumentation for implementing test
- Time savings, leading to faster development of new features.
- Improved documentation, which will help new colleagues understand the code base better.
- More user trust in the software product.
- Better user experience due to reduced downtime.

extra note on context manager

with context_manager:
    # 1. runs code on entering
    # 2. runs indented code
    # 3. runs code on exiting

test for these argument types
- bad arguments
- special arguments
- normal arguments

TDD = test driven development
    write unit test before feature
    this forces you to think about:
    - bad, special and normal arguments
    - return values
    - exceptions


pytest -x flags stops execution after first fail
pytest path_to_file.py  runs only this specific test module
pytest path_to_file.py::TestClass::test_function runs specific test function
pytest -k "TestClass"


travis CI
- add .travis.yml to root and install Travis CI via GitHub Marketplace
- check status at [travis-ci.com](https://app.travis-ci.com/github/benvliet/datacamp)
- add badge to README.md

codecov
- update .travis.yml for codecov
- install Codecov via GitHub Marketplace
- add badge to README.md
