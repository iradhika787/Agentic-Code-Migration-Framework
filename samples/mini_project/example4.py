def average(numbers):
    total = 0
    for i in xrange(len(numbers)):
        total += numbers[i]
    return total / len(numbers)

def describe(n):
    if n % 2 == 0:
        print "%d is even" % n
    else:
        print "%d is odd" % n

nums = [1, 2, 3, 4, 5]
print "Average:", average(nums)
for i in xrange(1, 6):
    describe(i)