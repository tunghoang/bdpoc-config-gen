import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--aValue", required=True)
parser.add_argument("-b", "--bValue", required=False)

args = parser.parse_args()

print("avalue", args.aValue)
print("bvalue", args.bValue)
