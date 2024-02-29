input_string = "pythonnojjjjjjjjhtyppy"

count = {}
for char in input_string:
    if char in count:
        count[char] += 1
    else:
        count[char] = 1
for char, count in count.items():
    print(f"{char}:{count}")
