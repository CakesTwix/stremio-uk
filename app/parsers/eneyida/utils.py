import re

def extract_numbers(input_string):
    numbers = re.findall(r'\d+', input_string)

    numbers = [int(num) for num in numbers]
    return numbers
