import unittest


def test_main() -> None:
    suite = unittest.TestLoader().discover("tests")
    _ = unittest.TextTestRunner().run(suite)


if __name__ == "__main__":
    test_main()
