"""
 Copyright Femtosense 2024
 
 By using this software package, you agree to abide by the terms and conditions
 in the license agreement found at https://femtosense.ai/legal/eula/
"""

from colorama import Fore, Style


def print_header(text: str, header_length=80, block_char="=", color_fg=Fore.GREEN):
    """
    Print a pretty header in green with a black background
    """
    length_of_text = len(text)
    left = (header_length - length_of_text - 2) // 2
    right = left
    if length_of_text % 2 == 1:
        right += 1

    print(color_fg + block_char * header_length)
    print(f"{block_char*left} {text} {block_char*right}")
    print(block_char * header_length)
    print(Style.RESET_ALL)
