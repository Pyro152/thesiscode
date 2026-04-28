import matplotlib.pyplot as plt

data = []

with open("3le.txt", "r") as f:
    for i, line in enumerate(f):
        # Read lines 2, 5, 8, ... (i % 3 == 2)
        if i % 3 == 2:
            # Extract characters 9–16 (Python slice 8:16)
            chunk = line[8:16]

            # Convert to float after stripping whitespace
            value = float(chunk.strip())

            data.append(value)

#print(data)


# ---- Plot histogram with bin size 1 ----
plt.hist(data, bins=range(int(min(data)), int(max(data)) + 2, 2), edgecolor='black')
plt.xlabel("Inclination (deg)")
plt.ylabel("Frequency")
plt.title("Histogram of Inclination Values, 9 Feb 2024 (bin size = 1)")
plt.show()
