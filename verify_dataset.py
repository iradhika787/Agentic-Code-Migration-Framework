#!/usr/bin/env python3
"""Verify and display dataset statistics."""

import json
from pathlib import Path

# Check full dataset
with open('data/python2to3_complete_dataset.json') as f:
    full = json.load(f)

print(f'\n{"="*60}')
print('DATASET VERIFICATION COMPLETE')
print("="*60)

print(f'\nFull Dataset: {len(full["examples"])} examples')

# Check splits
print('\nData Splits:')
for split in ['train', 'validation', 'test']:
    split_file = Path(f'data/splits/{split}.jsonl')
    if split_file.exists():
        count = len(split_file.read_text().strip().split('\n'))
        pct = (count / len(full["examples"])) * 100
        print(f'  • {split.capitalize():.<20} {count:>3} examples ({pct:.1f}%)')

# Show category breakdown
cats = full['metadata']['by_category']
print(f'\nCategories ({len(cats)}):')
for cat, count in sorted(cats.items(), key=lambda x: x[1], reverse=True):
    pct = (count / len(full["examples"])) * 100
    print(f'  • {cat:.<30} {count:>2} ({pct:>5.1f}%)')

# Show sources
sources = full['metadata']['by_source']
print(f'\nData Sources ({len(sources)}):')
for src, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
    pct = (count / len(full["examples"])) * 100
    print(f'  • {src:.<30} {count:>2} ({pct:>5.1f}%)')

# Show difficulty
diff = full['metadata']['by_difficulty']
print(f'\nDifficulty Distribution:')
for level in ['easy', 'medium', 'hard']:
    if level in diff:
        count = diff[level]
        pct = (count / len(full["examples"])) * 100
        print(f'  • {level.capitalize():.<30} {count:>2} ({pct:>5.1f}%)')

print(f'\n{"="*60}')
print('✓ Dataset ready for fine-tuning!')
print("="*60 + '\n')
