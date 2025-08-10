import timeit
import random
from typing import Callable
from itertools import islice

from wcwidth import wcwidth

all_ascii = [chr(i) for i in range(128)]

length = 1024

line = ''.join(random.choices(all_ascii, k=length))

end = len(line)

width = 128

tab_width = 4

number = 1000000

def top(
        func: Callable, use_list: bool = False, use_slice: bool = False,
        use_islice: bool = False,
    ):
    # line = ''.join(random.choices(all_ascii, k=length))
    start = 0
    result_list = []

    if use_list:
        line_local = list(line)
    else:
        line_local = line

    if use_slice:
        if use_islice:
            while True:
                index, visualized_string = func(islice(line_local, start, None), width)
                if visualized_string == '':
                    break
                else:
                    result_list.append(visualized_string)
                    start += index
        else:
            while True:
                index, visualized_string = func(line_local[start:], width)
                if visualized_string == '':
                    break
                else:
                    result_list.append(visualized_string)
                    start += index
    else:
        while True:
            index, visualized_string = func(line_local, start, width)
            if visualized_string == '':
                break
            else:
                result_list.append(visualized_string)
                start = index

    return result_list


def visualize_string_1(string: str, start: int, width: int):
    accumulate = 0
    result_list = []
    for index, char in enumerate(string):
        if index < start:
            continue
        if char == '\t':
            char_width = tab_width
            next_accumulate = accumulate + char_width
            if next_accumulate > width:
                return index, ''.join(result_list)
            else:
                accumulate = next_accumulate
                result_list.extend(' ' for index in range(tab_width))
        else:
            char_width = wcwidth(char)
            if char_width > 0:
                next_accumulate = accumulate + char_width
                if next_accumulate > width:
                    return index, ''.join(result_list)
                else:
                    accumulate = next_accumulate
                    result_list.append(char)
    return index + 1, ''.join(result_list)

def visualize_string_2(string: str, width: int):
    accumulate = 0
    result_list = []
    index = 0

    for char in string:
        if char == '\t':
            char_width = tab_width
            next_accumulate = accumulate + char_width
            if next_accumulate > width:
                break
            else:
                accumulate = next_accumulate
                result_list.extend(' ' for index in range(tab_width))
        else:
            char_width = wcwidth(char)
            if char_width > 0:
                next_accumulate = accumulate + char_width
                if next_accumulate > width:
                    break
                else:
                    accumulate = next_accumulate
                    result_list.append(char)
        index += 1
    return index, ''.join(result_list)

def visualize_string_3(string: list[str], start: int, width: int):
    accumulate = 0
    result_list = []
    for index in range(start, end):
        char = string[index]
        if char == '\t':
            char_width = tab_width
            next_accumulate = accumulate + char_width
            if next_accumulate > width:
                return index, ''.join(result_list)
            else:
                accumulate = next_accumulate
                result_list.extend(' ' for index in range(tab_width))
        else:
            char_width = wcwidth(char)
            if char_width > 0:
                next_accumulate = accumulate + char_width
                if next_accumulate > width:
                    return index, ''.join(result_list)
                else:
                    accumulate = next_accumulate
                    result_list.append(char)
    return end, ''.join(result_list)

def visualize_string_4(string: list[str], width: int):
    accumulate = 0
    result_list = []
    index = 0

    for char in string:
        if char == '\t':
            char_width = tab_width
            next_accumulate = accumulate + char_width
            if next_accumulate > width:
                break
            else:
                accumulate = next_accumulate
                result_list.extend(' ' for index in range(tab_width))
        else:
            char_width = wcwidth(char)
            if char_width > 0:
                next_accumulate = accumulate + char_width
                if next_accumulate > width:
                    break
                else:
                    accumulate = next_accumulate
                    result_list.append(char)
        index += 1
    return index, ''.join(result_list)

def visualize_string_5(string: str, width: int):
    accumulate = 0
    result_list = []
    index = 0

    for char in string:
        if char == '\t':
            char_width = tab_width
            next_accumulate = accumulate + char_width
            if next_accumulate > width:
                break
            else:
                accumulate = next_accumulate
                result_list.extend(' ' for index in range(tab_width))
        else:
            if char.isascii():
                char_width = 1 if char.isprintable() else 0
            else:
                char_width = wcwidth(char)
            if char_width > 0:
                next_accumulate = accumulate + char_width
                if next_accumulate > width:
                    break
                else:
                    accumulate = next_accumulate
                    result_list.append(char)
        index += 1
    return index, ''.join(result_list)


lambda_dict = {
    'Method1': lambda: top(visualize_string_1, use_list = False, use_slice = False),
    'Method2': lambda: top(visualize_string_2, use_list = False, use_slice = True),
    'Method3': lambda: top(visualize_string_3, use_list = True, use_slice = False),
    'Method4': lambda: top(visualize_string_4, use_list = True, use_slice = True),
    'Method5': lambda: top(visualize_string_4, use_list = True, use_slice = True, use_islice = True),
    'Method6': lambda: top(visualize_string_5, use_list = False, use_slice = True),
}

result_dict = {name: func() for name, func in lambda_dict.items()}

for name, result in result_dict.items():
    same = result == result_dict['Method1']
    print(f'Method1 == {name}: {same}')

for name, func in lambda_dict.items():
    time = timeit.timeit(func, number=number)
    print(f"{name}: {time:.6f} seconds")
