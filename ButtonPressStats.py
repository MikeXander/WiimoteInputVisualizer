from WiimoteDataParser import WiimoteData
from collections import defaultdict

input_filename = "./Sample Data/_inputs.csv"

data = [] # read file
with open(input_filename, 'r') as f:
    data = f.readlines()

button_press_stats = defaultdict(int)
last_inputs = WiimoteData("-1,0")
for line in data[1:]:
    inputs = WiimoteData(line)
    for btn in set(inputs.buttons) - set(last_inputs.buttons):
        button_press_stats[btn] += 1
    last_inputs = inputs

print("Button : Press Count")
for btn in button_press_stats.keys():
    print(btn, ':', button_press_stats[btn])
