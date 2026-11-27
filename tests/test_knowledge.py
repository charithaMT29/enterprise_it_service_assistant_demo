
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import knowledge


class KnowledgeTests(unittest.TestCase):

    def test_load_guide_chunks(self):
        guide_text = """
# IT Operations Guide

## VPN Troubleshooting

Check your internet connection.

## Software Installation

Use approved software only.
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            guide_path = Path(temp_dir) / "guide.md"
            guide_path.write_text(guide_text, encoding="utf-8")

            with patch.object(knowledge, "GUIDE_FILE", guide_path):
                chunks = knowledge.load_guide_chunks()

        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0]["title"], "VPN Troubleshooting")
        self.assertEqual(chunks[1]["title"], "Software Installation")

    def test_cosine_similarity(self):
        score = knowledge.cosine_similarity(
            [1, 0],
            [1, 0]
        )

        self.assertAlmostEqual(score, 1.0)

    def test_cosine_similarity_for_opposite_vectors(self):
        score = knowledge.cosine_similarity(
            [1, 0],
            [-1, 0]
        )

        self.assertAlmostEqual(score, -1.0)

    def test_cosine_similarity_with_zero_vector(self):
        score = knowledge.cosine_similarity(
            [0, 0],
            [1, 0]
        )

        self.assertEqual(score, 0.0)

    def test_retrieve_knowledge_returns_relevant_section(self):
        guide_text = """
## VPN Troubleshooting

Check your internet connection.

## Software Installation

Use approved software only.
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            guide_path = Path(temp_dir) / "guide.md"
            guide_path.write_text(guide_text, encoding="utf-8")

            def fake_embed(text):
                if text == "VPN question":
                    return [1, 0]

                if "VPN Troubleshooting" in text:
                    return [1, 0]

                return [0, 1]

            with patch.object(knowledge, "GUIDE_FILE", guide_path):
                with patch.object(knowledge, "embed", side_effect=fake_embed):
                    results = knowledge.retrieve_knowledge(
                        "VPN question",
                        top_k=2
                    )

        self.assertGreater(len(results), 0)
        self.assertEqual(
            results[0]["title"],
            "VPN Troubleshooting"
        )

    def test_retrieve_knowledge_returns_empty_when_no_match(self):
        guide_text = """
## Software Installation

Use approved software only.
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            guide_path = Path(temp_dir) / "guide.md"
            guide_path.write_text(guide_text, encoding="utf-8")

            def fake_embed(text):
                return [1, 0] if text == "unrelated question" else [0, 1]

            with patch.object(knowledge, "GUIDE_FILE", guide_path):
                with patch.object(knowledge, "embed", side_effect=fake_embed):
                    results = knowledge.retrieve_knowledge(
                        "unrelated question"
                    )

        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
