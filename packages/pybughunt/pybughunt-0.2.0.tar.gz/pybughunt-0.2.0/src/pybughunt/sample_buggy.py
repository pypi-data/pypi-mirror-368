# sample_buggy.py
def calculate_average(numbers):
    total = 0
    count = 0
    unused_var = 42

    for i in range(len(numbers)):
        total += numbers[i]
        count += 1

    # Potential division by zero if numbers is empty
    return total / count


def infinite_function():
    while True:
        print("This will run forever")
        # No break statement


def unreachable_code():
    print("This will run")
    return "Result"
    print("This will never run")  # Unreachable code
