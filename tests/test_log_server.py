import tempfile
import unittest
from pathlib import Path

from log_server import LogController, LogStream


class LogControllerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / "Cobotta.log").write_text("a\nb\nc\n", encoding="utf-8")
        (root / "Cobotta.log.2026-09-24").write_text("old1\nold2\n", encoding="utf-8")
        (root / "Cobotta.log.invalid").write_text("x", encoding="utf-8")
        self.controller = LogController(root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_tail(self):
        self.assertEqual(self.controller.tail("Cobotta", 2), "b\nc\n")

    def test_rotated_tail(self):
        self.assertEqual(
            self.controller.tail("Cobotta", 1, "2026-09-24"),
            "old2\n",
        )

    def test_dates(self):
        self.assertEqual(self.controller.dates("Cobotta"), ["2026-09-24"])

    def test_exists(self):
        self.assertTrue(self.controller.exists("Cobotta"))
        self.assertTrue(self.controller.exists("Cobotta", "2026-09-24"))
        self.assertFalse(self.controller.exists("Cobotta", "2026-09-23"))

    def test_reject_path(self):
        self.assertFalse(self.controller.exists("../Cobotta"))

    def test_stream_read(self):
        stream = LogStream(self.controller, chunk_size=3)
        self.assertEqual("".join(stream.read("Cobotta")), "a\nb\nc\n")
        self.assertEqual(
            "".join(stream.read("Cobotta", "2026-09-24")),
            "old1\nold2\n",
        )


if __name__ == "__main__":
    unittest.main()
