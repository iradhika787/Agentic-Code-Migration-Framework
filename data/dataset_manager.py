"""
Dataset Manager for Python 2→3 Migration Training Data

Handles:
- Collection from multiple sources
- Validation and normalization
- Train/test/val splits
- Versioning and metadata
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class MigrationExample:
    """Single Python 2→3 migration example."""
    
    id: str
    python2_code: str
    python3_code: str
    pattern_type: str
    category: str
    difficulty: str  # easy, medium, hard
    confidence: float  # 0.0-1.0
    source: str  # github, lib2to3, stackoverflow, synthetic
    tags: List[str]
    explanation: str
    language: str = "python"
    version_added: str = "1.0"
    
    def validate(self) -> tuple[bool, str]:
        """Validate the example."""
        if not self.python2_code or not self.python3_code:
            return False, "Empty code"
        if len(self.python2_code) > 5000:
            return False, "Code too long"
        if not self.pattern_type:
            return False, "Missing pattern type"
        if not self.category:
            return False, "Missing category"
        if not 0 <= self.confidence <= 1:
            return False, "Invalid confidence"
        if self.difficulty not in ["easy", "medium", "hard"]:
            return False, "Invalid difficulty"
        return True, "Valid"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    def get_hash(self) -> str:
        """Get unique hash of this example."""
        content = f"{self.python2_code}|{self.python3_code}"
        return hashlib.md5(content.encode()).hexdigest()[:8]


class DatasetManager:
    """Manages Python 2→3 migration dataset."""
    
    def __init__(self, data_dir: str = "data/raw_dataset"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.examples: List[MigrationExample] = []
        self.metadata = {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "total_examples": 0,
            "by_category": {},
            "by_difficulty": {},
            "by_source": {},
        }
    
    def add_example(self, example: MigrationExample) -> bool:
        """Add a single example to dataset."""
        valid, msg = example.validate()
        if not valid:
            print(f"Invalid example: {msg}")
            return False
        
        # Check for duplicates
        if self._is_duplicate(example):
            print(f"Duplicate example found, skipping")
            return False
        
        self.examples.append(example)
        self._update_metadata(example)
        return True
    
    def add_examples(self, examples: List[MigrationExample]) -> int:
        """Add multiple examples, return count added."""
        count = 0
        for example in examples:
            if self.add_example(example):
                count += 1
        return count
    
    def _is_duplicate(self, example: MigrationExample) -> bool:
        """Check if example already exists."""
        new_hash = example.get_hash()
        for existing in self.examples:
            if existing.get_hash() == new_hash:
                return True
        return False
    
    def _update_metadata(self, example: MigrationExample):
        """Update metadata statistics."""
        self.metadata["total_examples"] = len(self.examples)
        
        # By category
        cat = example.category
        self.metadata["by_category"][cat] = self.metadata["by_category"].get(cat, 0) + 1
        
        # By difficulty
        diff = example.difficulty
        self.metadata["by_difficulty"][diff] = self.metadata["by_difficulty"].get(diff, 0) + 1
        
        # By source
        src = example.source
        self.metadata["by_source"][src] = self.metadata["by_source"].get(src, 0) + 1
    
    def save_json(self, filepath: str):
        """Save dataset as JSON."""
        data = {
            "metadata": self.metadata,
            "examples": [ex.to_dict() for ex in self.examples]
        }
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Saved {len(self.examples)} examples to {filepath}")
    
    def load_json(self, filepath: str):
        """Load dataset from JSON."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.metadata = data.get("metadata", {})
        self.examples = [
            MigrationExample(**ex) for ex in data.get("examples", [])
        ]
        print(f"Loaded {len(self.examples)} examples from {filepath}")
    
    def create_splits(self, train_ratio: float = 0.7, val_ratio: float = 0.15):
        """Create train/val/test splits."""
        test_ratio = 1.0 - train_ratio - val_ratio
        
        import random
        random.shuffle(self.examples)
        
        n = len(self.examples)
        train_idx = int(n * train_ratio)
        val_idx = train_idx + int(n * val_ratio)
        
        train = self.examples[:train_idx]
        val = self.examples[train_idx:val_idx]
        test = self.examples[val_idx:]
        
        return {
            "train": train,
            "validation": val,
            "test": test,
            "sizes": {
                "train": len(train),
                "validation": len(val),
                "test": len(test),
            }
        }
    
    def save_splits(self, output_dir: str = "data/splits"):
        """Save train/val/test splits."""
        splits = self.create_splits()
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        for split_name, examples in splits.items():
            if split_name == "sizes":
                continue
            
            filepath = Path(output_dir) / f"{split_name}.jsonl"
            with open(filepath, 'w') as f:
                for ex in examples:
                    f.write(json.dumps(ex.to_dict()) + '\n')
            
            print(f"Saved {len(examples)} {split_name} examples to {filepath}")
    
    def get_stats(self) -> Dict:
        """Get dataset statistics."""
        return {
            "total": len(self.examples),
            "by_category": self.metadata.get("by_category", {}),
            "by_difficulty": self.metadata.get("by_difficulty", {}),
            "by_source": self.metadata.get("by_source", {}),
        }
    
    def print_stats(self):
        """Print dataset statistics."""
        stats = self.get_stats()
        print("\n" + "="*60)
        print(f"DATASET STATISTICS")
        print("="*60)
        print(f"Total Examples: {stats['total']}")
        print(f"\nBy Category:")
        for cat, count in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat:.<40} {count:>4}")
        print(f"\nBy Difficulty:")
        for diff, count in sorted(stats['by_difficulty'].items()):
            print(f"  {diff:.<40} {count:>4}")
        print(f"\nBy Source:")
        for src, count in sorted(stats['by_source'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {src:.<40} {count:>4}")
        print("="*60 + "\n")


if __name__ == "__main__":
    # Test dataset manager
    manager = DatasetManager()
    
    # Add sample examples
    examples = [
        MigrationExample(
            id="1",
            python2_code="print 'hello'",
            python3_code="print('hello')",
            pattern_type="print_statement",
            category="syntax",
            difficulty="easy",
            confidence=1.0,
            source="lib2to3",
            tags=["print", "syntax"],
            explanation="Python 3 requires parentheses for print()"
        ),
        MigrationExample(
            id="2",
            python2_code="d.has_key('x')",
            python3_code="'x' in d",
            pattern_type="dict_has_key",
            category="method_removal",
            difficulty="easy",
            confidence=1.0,
            source="lib2to3",
            tags=["dictionary", "method"],
            explanation="has_key() removed in Python 3"
        ),
    ]
    
    manager.add_examples(examples)
    manager.print_stats()
    manager.save_json("data/test_dataset.json")
