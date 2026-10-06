# Python 2→3 Migration Dataset Summary

Generated: 2026-08-31T13:16:05.960573
Version: 1.0

## Statistics

### Total Examples: 64

### By Category
- syntax: 19 examples
- builtin_change: 9 examples
- semantics: 8 examples
- compatible: 8 examples
- method_change: 6 examples
- string: 6 examples
- import: 6 examples
- method_removal: 2 examples

### By Difficulty
- Easy: 38 examples
- Medium: 19 examples
- Hard: 7 examples

### By Source
- lib2to3: 23 examples
- stackoverflow: 23 examples
- synthetic: 8 examples
- real_world: 6 examples
- github_django: 2 examples
- github_flask: 1 examples
- github_requests: 1 examples

## Dataset Files

- `data/python2to3_complete_dataset.json` - Full dataset in JSON format
- `data/splits/train.jsonl` - Training set (70%)
- `data/splits/validation.jsonl` - Validation set (15%)
- `data/splits/test.jsonl` - Test set (15%)

## How to Use

### Load Full Dataset
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
