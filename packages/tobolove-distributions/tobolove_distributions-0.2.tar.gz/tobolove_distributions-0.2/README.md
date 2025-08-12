# Distributions Package

A Python package for working with Gaussian (Normal) distributions and general probability distributions.

## Description

This package provides classes for calculating and visualizing Gaussian distributions with object-oriented programming principles. It includes functionality for statistical calculations, data visualization, and distribution operations.

## Installation

```bash
pip install distributions
```

## Features

- **Distribution**: Base class for probability distributions
- **Gaussian**: Specialized class for Gaussian (Normal) distributions
- Calculate mean and standard deviation from data
- Read data from text files
- Generate histograms and probability density plots
- Combine distributions using operator overloading
- Clean string representations of distribution objects

## Quick Start

```python
from distributions import Gaussian

# Create a Gaussian distribution
gaussian = Gaussian(mean=25, stdev=2)

# Load data from file
gaussian.read_data_file('data.txt')

# Calculate statistics
mean = gaussian.calculate_mean()
stdev = gaussian.calculate_stdev()

# Plot histogram
gaussian.plot_histogram()

# Calculate probability density function
pdf_value = gaussian.pdf(25)

# Combine distributions
gaussian1 = Gaussian(20, 3)
gaussian2 = Gaussian(30, 4)
combined = gaussian1 + gaussian2
print(combined)  # mean 50, standard deviation 5.0
```

## API Reference

### Gaussian Class

#### Constructor

```python
Gaussian(mu=0, sigma=1)
```

- `mu`: Mean of the distribution (default: 0)
- `sigma`: Standard deviation of the distribution (default: 1)

#### Methods

**`calculate_mean()`**

- Calculate the mean from loaded data
- Returns: float

**`calculate_stdev(sample=True)`**

- Calculate standard deviation from loaded data
- `sample`: Whether to use sample standard deviation (default: True)
- Returns: float

**`read_data_file(file_name, sample=True)`**

- Read data from a text file (one number per line)
- `file_name`: Path to the data file
- `sample`: Whether to calculate sample statistics (default: True)

**`plot_histogram()`**

- Display histogram of the data using matplotlib

**`pdf(x)`**

- Calculate probability density function at point x
- `x`: Point to evaluate
- Returns: float

**`plot_histogram_pdf(n_spaces=50)`**

- Plot normalized histogram and PDF curve
- `n_spaces`: Number of points for PDF curve (default: 50)
- Returns: tuple of (x_values, y_values)

#### Magic Methods

**`__add__(other)`**

- Add two Gaussian distributions
- Returns: New Gaussian object with combined mean and variance

**`__repr__()`**

- String representation of the distribution
- Returns: Formatted string with mean and standard deviation

## Requirements

- Python ≥ 3.6
- matplotlib ≥ 3.0
- math (standard library)

## File Format

Data files should contain one number per line:

```
23.4
25.1
22.8
24.6
```

## Example

```python
from distributions import Gaussian
import matplotlib.pyplot as plt

# Create and configure distribution
dist = Gaussian()
dist.read_data_file('sample_data.txt')

# Display statistics
print(f"Mean: {dist.calculate_mean():.2f}")
print(f"Standard Deviation: {dist.calculate_stdev():.2f}")

# Visualize
dist.plot_histogram_pdf()
plt.show()

# Combine with another distribution
dist2 = Gaussian(30, 2)
combined = dist + dist2
print(f"Combined distribution: {combined}")
```

## License

Open Source - Educational purposes

## Author

Educational package for learning object-oriented programming concepts with statistical distributions.
