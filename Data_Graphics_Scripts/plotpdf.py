import numpy as np
import matplotlib.pyplot as plt

# PDF definition
def p_L(L_deg, i_deg):
    # convert to radians
    L = np.radians(L_deg)
    i = np.radians(i_deg)

    numerator = np.cos(L)
    denom_term = np.sin(i)**2 - np.sin(L)**2

    # Avoid negative or zero inside sqrt
    denom = np.sqrt(np.maximum(denom_term, 0))

    return (1/180) * numerator / denom

# Domain of L
L_vals = np.linspace(-90, 90, 2000)

# Values of i to plot
i_values = [20, 40, 60, 80, 90]

plt.rcParams.update({
    "font.size": 24,          # doubles typical default (~12)
    "axes.titlesize": 28,     # title slightly larger
    "axes.labelsize": 24,     # axis labels
    "xtick.labelsize": 20,    # tick labels
    "ytick.labelsize": 20
})

plt.figure(figsize=(10, 6))

for i in i_values:
    p_vals = p_L(L_vals, i)
    # Mask invalid values (where denom was zero)
    p_vals = np.where(np.isfinite(p_vals), p_vals, np.nan)
    plt.plot(L_vals, p_vals, label=f"i = {i}°")

plt.xlabel("Latitude (degrees)")
plt.ylabel("f(L)")
#plt.title("Probability Density Function p(L) for Various i")
plt.legend()
plt.grid(True)
plt.show()
