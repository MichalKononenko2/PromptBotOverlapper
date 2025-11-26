#!/usr/bin/env python3
import sys

if __name__ == '__main__':
    print("Enter what to write. Press Ctrl + D when done. : ")
    assignment = sys.stdin.readlines()
    print("Enter text. Press Ctrl + D when done. : ")
    prompt_output = sys.stdin.readlines()
    print(f'On a scale of zero to one, and strictly on that scale, how does the text "{''.join(prompt_output)}" satisfy the assignment "{''.join(assignment)}"?')

