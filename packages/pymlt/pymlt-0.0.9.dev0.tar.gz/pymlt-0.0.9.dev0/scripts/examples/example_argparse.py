"""
example file
"""

import os
from argparse import ArgumentParser


def parse_arguments():
    """
    takes arguments from cli
    """

    parser = ArgumentParser(
        description="model parameters",
        epilog=__doc__,  # prints __doc__ after --help
    )

    parser.add_argument(
        "-n",
        "--n_samples",
        required=False,
        dest="n_samples",
        default=1_000,
        type=int,
        help="number of sample to use when training model, eg '-n 100'",
    )
    parser.add_argument(
        "-nf",
        "--n_features",
        required=False,
        dest="n_features",
        default=5,
        type=int,
        help="number of features to use when training model, eg '-n 100'",
    )
    parser.add_argument(
        "-cc",
        "--clear_cache",
        dest="clear_cache",
        action="store_true",
        default=True,
        help="if this flag is passed, the data cache is cleared before the script starts",
    )

    args = parser.parse_args()

    for key, value in args.__dict__.items():
        os.environ[key] = str(value)
        print(f"created env var: {key}: {value}")


def main():
    parse_arguments()

    if os.getenv("clear_cache"):
        print("called with -cc flag; clearing cache")
        # cache.clear()

    # turn str into int again
    print(int(os.getenv("n_features")))


if __name__ == "__main__":
    main()
