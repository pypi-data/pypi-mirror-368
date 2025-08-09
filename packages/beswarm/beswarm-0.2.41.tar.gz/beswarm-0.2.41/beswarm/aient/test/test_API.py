def replace_with_asterisk(string, start=15, end=40):
    return string[:start] + '*' * (end - start) + string[end:]

original_string = "sk-bvgiugvigycycyrfctdyxdxrts"
result = replace_with_asterisk(original_string)
print(result)
