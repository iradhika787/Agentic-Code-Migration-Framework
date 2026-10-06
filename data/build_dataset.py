"""
Master Dataset Collection Script

Combines all data sources into a single comprehensive dataset
with train/val/test splits ready for model training.
"""

import json
from pathlib import Path
from data.dataset_manager import DatasetManager, MigrationExample
from data.collectors import (
    Lib2to3Collector,
    SyntheticCollector,
    GitHubCollector,
    collect_all_datasets
)
from data.collectors_extended import (
    StackOverflowCollector,
    RealWorldCollector,
    collect_extended_datasets
)


def build_complete_dataset() -> DatasetManager:
    """Build complete dataset from all sources."""
    combined = DatasetManager()
    
    print("\n" + "="*70)
    print("BUILDING COMPLETE PYTHON 2→3 MIGRATION DATASET")
    print("="*70)
    
    # Phase 1: Core patterns
    print("\n" + "-"*70)
    print("PHASE 1: Core lib2to3, Synthetic, and GitHub patterns")
    print("-"*70)
    core_manager = collect_all_datasets()
    combined.add_examples(core_manager.examples)
    print(f"✓ Added {len(core_manager.examples)} core examples")
    
    # Phase 2: Extended patterns
    print("\n" + "-"*70)
    print("PHASE 2: Stack Overflow and Real-world patterns")
    print("-"*70)
    extended_manager = collect_extended_datasets()
    combined.add_examples(extended_manager.examples)
    print(f"✓ Added {len(extended_manager.examples)} extended examples")
    
    return combined


def create_dataset_summary(manager: DatasetManager, output_file: str = "data/DATASET_SUMMARY.md"):
    """Create a summary markdown file."""
    stats = manager.get_stats()
    
    summary = f"""# Python 2→3 Migration Dataset Summary

Generated: {manager.metadata['created']}
Version: {manager.metadata['version']}

## Statistics

### Total Examples: {stats['total']}

### By Category
"""
    
    for cat in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True):
        summary += f"- {cat[0]}: {cat[1]} examples\n"
    
    summary += "\n### By Difficulty\n"
    for diff in ["easy", "medium", "hard"]:
        if diff in stats['by_difficulty']:
            count = stats['by_difficulty'][diff]
            summary += f"- {diff.capitalize()}: {count} examples\n"
    
    summary += "\n### By Source\n"
    for src in sorted(stats['by_source'].items(), key=lambda x: x[1], reverse=True):
        summary += f"- {src[0]}: {src[1]} examples\n"
    
    summary += "\n## Dataset Files\n\n"
    summary += "- `data/python2to3_complete_dataset.json` - Full dataset in JSON format\n"
    summary += "- `data/splits/train.jsonl` - Training set (70%)\n"
    summary += "- `data/splits/validation.jsonl` - Validation set (15%)\n"
    summary += "- `data/splits/test.jsonl` - Test set (15%)\n"
    
    summary += "\n## How to Use\n\n"
    summary += """### Load Full Dataset
```python
from data.dataset_manager import DatasetManager

manager = DatasetManager()
manager.load_json('data/python2to3_complete_dataset.json')
print(f"Loaded {len(manager.examples)} examples")
```

### Load Train/Val/Test Splits
```python
import json

# Load training set
with open('data/splits/train.jsonl') as f:
    train = [json.loads(line) for line in f]

# Load validation set
with open('data/splits/validation.jsonl') as f:
    val = [json.loads(line) for line in f]

# Load test set
with open('data/splits/test.jsonl') as f:
    test = [json.loads(line) for line in f]
```

### Example Format
```json
{
  "id": "lib2to3_001",
  "python2_code": "print 'hello'",
  "python3_code": "print('hello')",
  "pattern_type": "print_statement",
  "category": "syntax",
  "difficulty": "easy",
  "confidence": 1.0,
  "source": "lib2to3",
  "tags": ["print", "syntax", "statement"],
  "explanation": "Python 3 requires parentheses for print()"
}
```

## Next Steps

1. **Fine-tune LLM** on this dataset using the training set
2. **Validate** using the validation set during training
3. **Test** model performance on the held-out test set
4. **Monitor** metrics: accuracy, F1-score, precision, recall

## Pattern Categories Covered

- Syntax changes (print, exceptions, operators)
- Built-in function changes (renamed, removed)
- Dictionary method changes
- String/Unicode handling
- Division semantics
- Iterator behavior
- Import reorganization
- And more...
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"\n✓ Created dataset summary: {output_file}")


def main():
    """Main entry point."""
    # Build dataset
    manager = build_complete_dataset()
    
    # Print statistics
    print("\n" + "="*70)
    print("DATASET STATISTICS")
    print("="*70)
    manager.print_stats()
    
    # Save dataset
    print("\n" + "-"*70)
    print("SAVING DATASET")
    print("-"*70)
    
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Save full dataset
    dataset_file = data_dir / "python2to3_complete_dataset.json"
    manager.save_json(str(dataset_file))
    
    # Create and save splits
    splits_dir = data_dir / "splits"
    manager.save_splits(str(splits_dir))
    
    # Create summary
    create_dataset_summary(manager)
    
    print("\n" + "="*70)
    print("✓ DATASET BUILDING COMPLETE!")
    print("="*70)
    print(f"\nTotal Examples Collected: {len(manager.examples)}")
    print(f"Dataset Location: {data_dir}")
    print(f"\nFiles Created:")
    print(f"  - {dataset_file}")
    print(f"  - {splits_dir}/train.jsonl")
    print(f"  - {splits_dir}/validation.jsonl")
    print(f"  - {splits_dir}/test.jsonl")
    print(f"  - {data_dir}/DATASET_SUMMARY.md")
    print("\n" + "="*70)
    
    return manager


if __name__ == "__main__":
    manager = main()
