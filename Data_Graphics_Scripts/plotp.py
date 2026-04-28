# Creating a plot of the function f(l) = cos(l)/180/sqrt(sin(50)^2 - sin(l)^2) from l = -49 to 49 degrees
import numpy as np
import matplotlib.pyplot as plt

# Use ggplot style for better aesthetics
plt.style.use('ggplot')

# Define the function f(l)
def f(l_deg):
    l_rad = np.radians(l_deg)
    sin_50 = np.sin(np.radians(50))
    denominator = np.sqrt(sin_50**2 - np.sin(l_rad)**2)
    return np.cos(l_rad) / 180 / denominator

# Generate l values from -49 to 49 degrees
l_values = np.linspace(-49, 49, 1000)
# Compute f(l) values, handling invalid values due to sqrt of negative numbers
f_values = np.full_like(l_values, np.nan)
valid_indices = np.abs(np.sin(np.radians(l_values))) < np.sin(np.radians(50))
f_values[valid_indices] = f(l_values[valid_indices])

# Plot the function
plt.figure(figsize=(10, 6))
plt.plot(l_values, f_values, label=r'$f(\ell) = \frac{\cos(\ell)}{180\sqrt{\sin^2(50^\circ) - \sin^2(\ell)}}$')
plt.xlabel(r'$\ell$ (degrees)')
plt.ylabel(r'$f(\ell)$')
plt.title('Plot of the function $f(\ell)$ from -49° to 49°')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Save the plot
output_path = "/mnt/data/plot_function_f_l.png"
#plt.savefig(output_path)

print(f"Plot of the function f(l) saved as {output_path}")

