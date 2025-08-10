"""
Example script for vibeisodd package.
"""
from vibeisodd import vibeisodd, vibeisodd_batch

if __name__ == "__main__":
    print("Let's see if 7 is odd:")
    print(vibeisodd(7))  # True

    print("Let's see if 8 is odd:")
    print(vibeisodd(8))  # False

    print("Batch check: [1, 2, 3.0, 4.5]")
    print(vibeisodd_batch([1, 2, 3.0, 4.5]))
