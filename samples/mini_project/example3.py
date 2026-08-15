class Inventory(object):
    def __init__(self):
        self.items = {"apple": 10, "banana": 5}

    def report(self):
        for name, count in self.items.iteritems():
            print "%s: %d" % (name, count)

    def low_stock(self):
        result = []
        for name, count in self.items.iteritems():
            if count < 10:
                result.append(name)
        return result

inv = Inventory()
inv.report()
print inv.low_stock()