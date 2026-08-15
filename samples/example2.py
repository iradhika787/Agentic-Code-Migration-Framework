def process(items):
    try:
        for item in items:
            print "Processing:", item
    except Exception, e:
        print "Error occurred:", e

def greet(name):
    message = unicode("Hello, ") + name
    print message

greet(u"World")
process([1, 2, 3])