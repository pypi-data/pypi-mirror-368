"""
Example usage of VibeIsEven
"""
from vibeiseven import vibeiseven, vibeiseven_batch

if __name__ == "__main__":
    number = 42
    print(f"Is {number} even? {vibeiseven(number)}")

    numbers = [1, 2, 3, 4, 5]
    print(f"Batch results: {vibeiseven_batch(numbers)}")
