import unittest

from knowledge.knowledge_base import KnowledgeBase
from knowledge.memory_store import MemoryStore


class KnowledgeMemoryTest(unittest.TestCase):
    def test_knowledge_base_searches_by_category(self):
        kb = KnowledgeBase()
        kb.add_entry("python3", "use print()")
        self.assertEqual(kb.search("python3")[0]["rule"], "use print()")

    def test_memory_store_recalls_values(self):
        memory = MemoryStore()
        memory.remember("repair", "use // for integer division")
        self.assertIn("use // for integer division", memory.recall("repair"))


if __name__ == "__main__":
    unittest.main()
