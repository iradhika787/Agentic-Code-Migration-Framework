"""
Extended Dataset Collectors

Additional sources:
- Stack Overflow common Python 2→3 issues
- Large-scale code patterns
- Real-world edge cases
"""

from data.dataset_manager import MigrationExample, DatasetManager


class StackOverflowCollector:
    """Collects common Python 2→3 issues from Stack Overflow."""
    
    def __init__(self):
        self.manager = DatasetManager()
    
    def collect(self) -> DatasetManager:
        """Collect Stack Overflow Python 2→3 issues."""
        examples = [
            # Print function most common
            MigrationExample(
                id="so_print_001",
                python2_code="print 'Hello %s' % name",
                python3_code="print('Hello %s' % name)",
                pattern_type="print_statement",
                category="syntax",
                difficulty="easy",
                confidence=1.0,
                source="stackoverflow",
                tags=["print", "string_formatting", "common"],
                explanation="Print with string formatting"
            ),
            MigrationExample(
                id="so_print_002",
                python2_code="print variable",
                python3_code="print(variable)",
                pattern_type="print_statement",
                category="syntax",
                difficulty="easy",
                confidence=1.0,
                source="stackoverflow",
                tags=["print", "simple", "very_common"],
                explanation="Most common migration: simple print without parentheses"
            ),
            
            # Division
            MigrationExample(
                id="so_div_001",
                python2_code="total = 10 / 3  # expects 3",
                python3_code="total = 10 // 3  # still 3",
                pattern_type="division_semantics",
                category="semantics",
                difficulty="hard",
                confidence=0.85,
                source="stackoverflow",
                tags=["division", "arithmetic", "subtle_bug"],
                explanation="Division semantics change is subtle and often missed"
            ),
            MigrationExample(
                id="so_div_002",
                python2_code="result = 1.0 / 2  # Python 2 & 3 both 0.5",
                python3_code="result = 1.0 / 2",
                pattern_type="division_semantics",
                category="semantics",
                difficulty="medium",
                confidence=1.0,
                source="stackoverflow",
                tags=["division", "float", "compatible"],
                explanation="Float division works in both versions"
            ),
            
            # Unicode/String most common in SO
            MigrationExample(
                id="so_unicode_001",
                python2_code="s = 'hello'\nprint type(s)  # <type 'str'>",
                python3_code="s = 'hello'\nprint(type(s))  # <class 'str'>",
                pattern_type="string_type",
                category="string",
                difficulty="medium",
                confidence=0.9,
                source="stackoverflow",
                tags=["string", "unicode", "type", "semantic"],
                explanation="In Python 2 str is bytes, in Python 3 str is unicode"
            ),
            MigrationExample(
                id="so_unicode_002",
                python2_code="s.decode('utf-8')",
                python3_code="s.encode('latin-1').decode('utf-8')",
                pattern_type="string_encoding",
                category="string",
                difficulty="hard",
                confidence=0.7,
                source="stackoverflow",
                tags=["encoding", "decode", "complex"],
                explanation="String encoding/decoding behavior differs significantly"
            ),
            MigrationExample(
                id="so_unicode_003",
                python2_code="if isinstance(x, basestring):",
                python3_code="if isinstance(x, str):",
                pattern_type="type_check",
                category="builtin_change",
                difficulty="easy",
                confidence=1.0,
                source="stackoverflow",
                tags=["isinstance", "basestring", "type_check"],
                explanation="basestring removed, use str for string type checking"
            ),
            
            # Range/iteration very common
            MigrationExample(
                id="so_iter_001",
                python2_code="for i in xrange(1000000):",
                python3_code="for i in range(1000000):",
                pattern_type="builtin_renamed",
                category="builtin_change",
                difficulty="easy",
                confidence=1.0,
                source="stackoverflow",
                tags=["xrange", "range", "iteration", "memory"],
                explanation="xrange() removed, range() is lazy in Python 3"
            ),
            MigrationExample(
                id="so_iter_002",
                python2_code="items = map(func, list1, list2)",
                python3_code="items = list(map(func, list1, list2))",
                pattern_type="iterator_return",
                category="semantics",
                difficulty="medium",
                confidence=0.95,
                source="stackoverflow",
                tags=["map", "multiple_args", "iterator"],
                explanation="map() returns iterator, need list() for list result"
            ),
            MigrationExample(
                id="so_iter_003",
                python2_code="for i in dict.keys():",
                python3_code="for i in dict.keys():",
                pattern_type="dict_keys",
                category="compatible",
                difficulty="easy",
                confidence=1.0,
                source="stackoverflow",
                tags=["dict", "keys", "compatible"],
                explanation="dict.keys() works in both versions (but returns view in Python 3)"
            ),
            
            # Exception handling
            MigrationExample(
                id="so_except_001",
                python2_code="except (IOError, OSError), e:",
                python3_code="except (IOError, OSError) as e:",
                pattern_type="except_as",
                category="syntax",
                difficulty="easy",
                confidence=1.0,
                source="stackoverflow",
                tags=["exception", "multiple", "as"],
                explanation="Multiple exception handling with 'as' syntax"
            ),
            MigrationExample(
                id="so_except_002",
                python2_code="raise IOError, 'message'",
                python3_code="raise IOError('message')",
                pattern_type="raise_syntax",
                category="syntax",
                difficulty="easy",
                confidence=1.0,
                source="stackoverflow",
                tags=["raise", "exception", "constructor"],
                explanation="Raise with exception instance (not string)"
            ),
            MigrationExample(
                id="so_except_003",
                python2_code="raise ValueError()",
                python3_code="raise ValueError()",
                pattern_type="raise_call",
                category="compatible",
                difficulty="easy",
                confidence=1.0,
                source="stackoverflow",
                tags=["raise", "modern", "compatible"],
                explanation="Modern raise syntax compatible in both versions"
            ),
            
            # Dictionary methods
            MigrationExample(
                id="so_dict_001",
                python2_code="for k in d.iterkeys():",
                python3_code="for k in d.keys():",
                pattern_type="dict_iterator",
                category="method_change",
                difficulty="easy",
                confidence=1.0,
                source="stackoverflow",
                tags=["dict", "iterkeys", "keys"],
                explanation="iterkeys() renamed to keys()"
            ),
            MigrationExample(
                id="so_dict_002",
                python2_code="for v in d.itervalues():",
                python3_code="for v in d.values():",
                pattern_type="dict_iterator",
                category="method_change",
                difficulty="easy",
                confidence=1.0,
                source="stackoverflow",
                tags=["dict", "itervalues", "values"],
                explanation="itervalues() renamed to values()"
            ),
            MigrationExample(
                id="so_dict_003",
                python2_code="if d.has_key(key):",
                python3_code="if key in d:",
                pattern_type="dict_has_key",
                category="method_removal",
                difficulty="easy",
                confidence=1.0,
                source="stackoverflow",
                tags=["dict", "has_key", "in"],
                explanation="has_key() removed, use 'in' operator"
            ),
            
            # Import statements
            MigrationExample(
                id="so_import_001",
                python2_code="from urllib2 import urlopen",
                python3_code="from urllib.request import urlopen",
                pattern_type="import_reorganization",
                category="import",
                difficulty="medium",
                confidence=0.95,
                source="stackoverflow",
                tags=["urllib", "import", "reorganization"],
                explanation="urllib reorganized in Python 3"
            ),
            MigrationExample(
                id="so_import_002",
                python2_code="from urllib import urlencode",
                python3_code="from urllib.parse import urlencode",
                pattern_type="import_reorganization",
                category="import",
                difficulty="medium",
                confidence=0.95,
                source="stackoverflow",
                tags=["urllib", "urlencode", "import"],
                explanation="urllib.parse contains URL utilities"
            ),
            MigrationExample(
                id="so_import_003",
                python2_code="from ConfigParser import SafeConfigParser",
                python3_code="from configparser import ConfigParser",
                pattern_type="import_change",
                category="import",
                difficulty="medium",
                confidence=0.95,
                source="stackoverflow",
                tags=["ConfigParser", "configparser", "rename"],
                explanation="ConfigParser module renamed to configparser"
            ),
            
            # Metaclass definition
            MigrationExample(
                id="so_meta_001",
                python2_code="class MyClass(object):\n    __metaclass__ = Meta",
                python3_code="class MyClass(metaclass=Meta):",
                pattern_type="metaclass_syntax",
                category="syntax",
                difficulty="hard",
                confidence=0.85,
                source="stackoverflow",
                tags=["metaclass", "syntax", "advanced"],
                explanation="Metaclass syntax changed in Python 3"
            ),
            
            # Common function changes
            MigrationExample(
                id="so_func_001",
                python2_code="enumerate(d.items())",
                python3_code="enumerate(d.items())",
                pattern_type="compatible",
                category="compatible",
                difficulty="easy",
                confidence=1.0,
                source="stackoverflow",
                tags=["enumerate", "compatible"],
                explanation="enumerate() works with both versions"
            ),
            MigrationExample(
                id="so_func_002",
                python2_code="zip(list1, list2)",
                python3_code="list(zip(list1, list2))",
                pattern_type="iterator_return",
                category="semantics",
                difficulty="medium",
                confidence=0.95,
                source="stackoverflow",
                tags=["zip", "iterator", "list"],
                explanation="zip() returns iterator in Python 3"
            ),
            
            # Backticks and operators
            MigrationExample(
                id="so_op_001",
                python2_code="`x`",
                python3_code="repr(x)",
                pattern_type="backtick_repr",
                category="syntax",
                difficulty="easy",
                confidence=1.0,
                source="stackoverflow",
                tags=["backtick", "repr", "syntax"],
                explanation="Backticks removed, use repr() function"
            ),
            MigrationExample(
                id="so_op_002",
                python2_code="if x <> y:",
                python3_code="if x != y:",
                pattern_type="operator_change",
                category="syntax",
                difficulty="easy",
                confidence=1.0,
                source="stackoverflow",
                tags=["operator", "inequality", "syntax"],
                explanation="<> operator removed, use !="
            ),
        ]
        
        self.manager.add_examples(examples)
        return self.manager


class RealWorldCollector:
    """Collects real-world edge cases and complex patterns."""
    
    def __init__(self):
        self.manager = DatasetManager()
    
    def collect(self) -> DatasetManager:
        """Collect real-world complex patterns."""
        examples = [
            # Nested conversions
            MigrationExample(
                id="rw_nested_001",
                python2_code="d = {k: v for k, v in zip(keys, map(int, values))}",
                python3_code="d = {k: v for k, v in zip(keys, map(int, values))}",
                pattern_type="compatible_complex",
                category="compatible",
                difficulty="medium",
                confidence=1.0,
                source="real_world",
                tags=["complex", "comprehension", "compatible"],
                explanation="Complex but compatible pattern"
            ),
            
            # File handling
            MigrationExample(
                id="rw_file_001",
                python2_code="f = file('data.txt')\ndata = f.read()",
                python3_code="f = open('data.txt')\ndata = f.read()",
                pattern_type="builtin_renamed",
                category="builtin_change",
                difficulty="easy",
                confidence=1.0,
                source="real_world",
                tags=["file", "open", "io"],
                explanation="file() replaced by open()"
            ),
            
            # Print with newline
            MigrationExample(
                id="rw_print_001",
                python2_code="sys.stdout.write('message')",
                python3_code="sys.stdout.write('message')",
                pattern_type="compatible",
                category="compatible",
                difficulty="easy",
                confidence=1.0,
                source="real_world",
                tags=["io", "stdout", "compatible"],
                explanation="sys.stdout.write() compatible in both versions"
            ),
            
            # Bytes vs strings
            MigrationExample(
                id="rw_bytes_001",
                python2_code="data = '\\x00\\x01\\x02'",
                python3_code="data = b'\\x00\\x01\\x02'",
                pattern_type="bytes_literal",
                category="string",
                difficulty="hard",
                confidence=0.75,
                source="real_world",
                tags=["bytes", "string", "binary"],
                explanation="Byte string literals need b prefix in Python 3"
            ),
            
            # String methods
            MigrationExample(
                id="rw_str_001",
                python2_code="s.strip()",
                python3_code="s.strip()",
                pattern_type="compatible",
                category="compatible",
                difficulty="easy",
                confidence=1.0,
                source="real_world",
                tags=["string", "method", "compatible"],
                explanation="String methods compatible across versions"
            ),
            
            # Dict get with default
            MigrationExample(
                id="rw_dict_001",
                python2_code="d.get('key', default)",
                python3_code="d.get('key', default)",
                pattern_type="compatible",
                category="compatible",
                difficulty="easy",
                confidence=1.0,
                source="real_world",
                tags=["dict", "get", "compatible"],
                explanation="dict.get() compatible in both versions"
            ),
        ]
        
        self.manager.add_examples(examples)
        return self.manager


def collect_extended_datasets() -> DatasetManager:
    """Collect from all extended sources."""
    combined_manager = DatasetManager()
    
    print("\n" + "="*60)
    print("COLLECTING EXTENDED DATASETS")
    print("="*60)
    
    # Stack Overflow
    print("\n[1/2] Collecting Stack Overflow patterns...")
    so = StackOverflowCollector().collect()
    combined_manager.add_examples(so.examples)
    print(f"✓ Added {len(so.examples)} Stack Overflow examples")
    
    # Real-world
    print("\n[2/2] Collecting real-world edge cases...")
    rw = RealWorldCollector().collect()
    combined_manager.add_examples(rw.examples)
    print(f"✓ Added {len(rw.examples)} real-world examples")
    
    return combined_manager


if __name__ == "__main__":
    manager = collect_extended_datasets()
    manager.print_stats()
