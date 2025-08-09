def mean(data):
    return sum(data) / len(data)

def median(data):
    s = sorted(data)
    n = len(s)
    mid = n // 2
    return (s[mid] + s[~mid]) / 2

def variance(data):
    m = mean(data)
    return sum((x - m) ** 2 for x in data) / len(data)

def standard_deviation(data):
    return variance(data) ** 0.5

def mode(data):
    from collections import Counter
    counts = Counter(data)
    max_count = max(counts.values())
    modes = [k for k, v in counts.items() if v == max_count]
    if len(modes) == 1:
        return modes[0]
    return modes  # multiple modes possible

def range_(data):
    return max(data) - min(data)

def quartiles(data):
    s = sorted(data)
    n = len(s)
    Q2 = median(s)
    Q1 = median(s[:n//2])
    Q3 = median(s[(n+1)//2:])
    return Q1, Q2, Q3

def interquartile_range(data):
    Q1, _, Q3 = quartiles(data)
    return Q3 - Q1

def covariance(data_x, data_y):
    if len(data_x) != len(data_y):
        raise ValueError("Data lists must be of equal length")
    mean_x = mean(data_x)
    mean_y = mean(data_y)
    return sum((x - mean_x)*(y - mean_y) for x, y in zip(data_x, data_y)) / len(data_x)

def correlation_coefficient(data_x, data_y):
    import math
    cov = covariance(data_x, data_y)
    std_x = standard_deviation(data_x)
    std_y = standard_deviation(data_y)
    if std_x == 0 or std_y == 0:
        raise ValueError("Standard deviation cannot be zero")
    return cov / (std_x * std_y)

def z_scores(data):
    m = mean(data)
    std = standard_deviation(data)
    if std == 0:
        raise ValueError("Standard deviation cannot be zero")
    return [(x - m) / std for x in data]

def skewness(data):
    n = len(data)
    m = mean(data)
    std = standard_deviation(data)
    return (sum((x - m) ** 3 for x in data) / n) / (std ** 3)

def kurtosis(data):
    n = len(data)
    m = mean(data)
    std = standard_deviation(data)
    return (sum((x - m) ** 4 for x in data) / n) / (std ** 4) - 3

def coefficient_of_variation(data):
    m = mean(data)
    std = standard_deviation(data)
    if m == 0:
        raise ValueError("Mean cannot be zero")
    return std / m

def sample_variance(data):
    m = mean(data)
    n = len(data)
    return sum((x - m) ** 2 for x in data) / (n - 1)

def sample_standard_deviation(data):
    return sample_variance(data) ** 0.5

def percentile(data, percent):
    s = sorted(data)
    k = (len(s)-1) * (percent / 100)
    f = int(k)
    c = k - f
    if f + 1 < len(s):
        return s[f] + (s[f+1] - s[f]) * c
    else:
        return s[f]
