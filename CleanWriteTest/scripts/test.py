import os

print(os.path.isfile('../../data/MANIFEST.txt'))

with open('../../data/MANIFEST.txt') as f:
    lines = f.readlines()

existing_ids = []

for i in lines[1:]:
	existing_ids.append(i[0:36])

print(existing_ids)