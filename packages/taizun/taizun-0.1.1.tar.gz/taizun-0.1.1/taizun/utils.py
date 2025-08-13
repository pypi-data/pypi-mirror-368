# utils.py

def reverse(s: str) -> str:
    """Reverses the string"""
    return s[::-1]

def greet(name: str) -> str:
    """Greets the user with their name"""
    return f"Hello, {name}!"

def calculator(a, b, operation):
    if operation == 'add':
        return a + b
    elif operation == 'subtract':
        return a - b
    elif operation == 'multiply':
        return a * b
    elif operation == 'divide':
        return a / b if b != 0 else "Cannot divide by zero"
    else:
        return "Invalid operation"

def is_even(num: int) -> bool:
    """Returns True if the number is even, else False"""
    return num % 2 == 0

def is_odd(num: int) -> bool:
    """Returns True if the number is odd, else False"""
    return num % 2 != 0

def square(num: int) -> int:
    """Returns the square of a number"""
    return num ** 2

def cube(num: int) -> int:
    """Returns the cube of a number"""
    return num ** 3

def factorial(n: int) -> int:
    """Returns the factorial of a number"""
    if n == 0:
        return 1
    return n * factorial(n - 1)

def power(base: int, exp: int) -> int:
    """Returns the result of base raised to the power of exp"""
    return base ** exp

def min_val(a: int, b: int) -> int:
    """Returns the minimum of two numbers"""
    return min(a, b)

def max_val(a: int, b: int) -> int:
    """Returns the maximum of two numbers"""
    return max(a, b)

def avg(nums: list) -> float:
    """Returns the average of a list of numbers"""
    return sum(nums) / len(nums)

def is_palindrome(s: str) -> bool:
    """Checks if a string is a palindrome"""
    return s == s[::-1]

def is_prime(n: int) -> bool:
    """Checks if a number is prime"""
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def factorial_list(nums: list) -> list:
    """Returns a list of factorials for each number"""
    return [factorial(num) for num in nums]

def get_length(s: str) -> int:
    """Returns the length of a string"""
    return len(s)

def capitalize(s: str) -> str:
    """Capitalizes the first letter of the string"""
    return s.capitalize()

def lowercase(s: str) -> str:
    """Converts a string to lowercase"""
    return s.lower()

def uppercase(s: str) -> str:
    """Converts a string to uppercase"""
    return s.upper()

def concat(s1: str, s2: str) -> str:
    """Concatenates two strings"""
    return s1 + s2

def strip_spaces(s: str) -> str:
    """Removes leading and trailing spaces from the string"""
    return s.strip()

def split_string(s: str, delimiter: str = " ") -> list:
    """Splits a string into a list by the delimiter"""
    return s.split(delimiter)

def join_list(lst: list, delimiter: str = " ") -> str:
    """Joins a list of strings into a single string"""
    return delimiter.join(lst)

def convert_to_int(s: str) -> int:
    """Converts a string to an integer"""
    try:
        return int(s)
    except ValueError:
        return None

def convert_to_float(s: str) -> float:
    """Converts a string to a float"""
    try:
        return float(s)
    except ValueError:
        return None

def check_type(val: any) -> str:
    """Returns the type of the given value"""
    return type(val).__name__

def remove_duplicates(lst: list) -> list:
    """Removes duplicates from a list"""
    return list(set(lst))

def merge_lists(lst1: list, lst2: list) -> list:
    """Merges two lists into one"""
    return lst1 + lst2
def kaptan():
    print("Taizun is an AI engineer studying in their first year, pursuing a BTech degree. Hope you have a great day ahead.")


