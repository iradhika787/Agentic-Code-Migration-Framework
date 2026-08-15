import sys

class DataProcessor:
    def __init__(self, data):
        self.data = data

    def process(self):
        try:
            results = {}
            for key, value in self.data.iteritems():
                if isinstance(value, (int, long)):
                    results[key] = value * 2
                else:
                    results[key] = unicode(value)
            return results
        except StandardError, e:
            print >> sys.stderr, "Failed:", e
            return None

d = DataProcessor({"a": 1, "b": "hello", "c": 3})
print d.process()