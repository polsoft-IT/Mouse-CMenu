import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from single_instance import SingleInstanceGuard


class SingleInstanceTests(unittest.TestCase):
    def test_only_one_guard_can_acquire_the_same_server(self) -> None:
        with TemporaryDirectory() as directory:
            lock_path = Path(directory) / "instance.lock"
            first = SingleInstanceGuard(lock_path)
            second = SingleInstanceGuard(lock_path)

            try:
                self.assertTrue(first.acquire())
                self.assertFalse(second.acquire())
                first.close()
                self.assertTrue(second.acquire())
            finally:
                first.close()
                second.close()


if __name__ == "__main__":
    unittest.main()