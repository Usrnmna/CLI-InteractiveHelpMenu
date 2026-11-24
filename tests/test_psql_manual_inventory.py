"""Compare the bundled client with the reviewed PostgreSQL option declarations."""

import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PsqlInventoryTests(unittest.TestCase):
    def test_every_client_spelling_and_arity(self):
        """Keep the glob alias searchable and the optional help topic attached."""
        profile = json.loads((ROOT / "profiles/psql.json").read_text())
        rows = {row["flag"]: row for c in profile["categories"] for row in c["options"]}
        expected = {}
        with (ROOT / "tests/fixtures/psql-manual/declarations.tsv").open() as stream:
            for record in csv.DictReader(stream, delimiter="\t"):
                for name in (record["long"], record["short"]):
                    if name and name != "-?":
                        expected[name] = record["operand"]
        # Ubuntu's /usr/bin/psql launcher consumes this option before handing
        # the remaining arguments to the versioned upstream client.
        expected["--cluster"] = "required"
        self.assertIn("pg_wrapper", rows["--cluster"]["detail"])
        self.assertEqual(rows.keys(), expected.keys())
        for name, row in rows.items():
            with self.subTest(name=name):
                self.assertEqual(bool(row.get("argument")), expected[name] != "no")
                self.assertEqual(row.get("argument_optional", False), expected[name] == "optional")
        self.assertIn("'-?'", rows["--help"]["detail"])
        self.assertEqual(rows["--help"]["argument_style"], "equals")
        self.assertIn("ON_ERROR_STOP", rows["-1"]["detail"])
        self.assertIn("execution order", rows["--file"]["detail"])
