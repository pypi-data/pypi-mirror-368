# Enhanced Automatic Shifted Log Transformer (EASLT)

Automatically transform skewed data into more normal distributions using a Monte Carlo–optimized shifted log transformation.

---

## 🚀 Features

- **Works with negative, zero, and positive values**
- **Reduces skewness and kurtosis**
- **Adaptive, data-driven transformation**
- **Multi-test normality assessment**
- **Scikit-learn compatible**
- **Numba-accelerated for speed**

---

## 📦 Installation

```bash
pip install EASLT
```

---

## ⚡ Quick Start

```python
from EASLT import AutomaticShiftedLogTransformer
import numpy as np

# Example skewed data
np.random.seed(42)
data = np.random.exponential(2, (1000, 3))

# Transform
transformer = AutomaticShiftedLogTransformer(mc_iterations=1000, random_state=42)
data_transformed = transformer.fit_transform(data)
```

---

## 📚 How It Works

EASLT:
1. **Detects data complexity** (normal, mild issues, needs transformation)
2. **Applies robust shifting** for negative/zero values
3. **Detects outliers** and optionally winsorizes
4. **Optimizes parameters** via Monte Carlo with Dirichlet sampling
5. **Applies Feng's shifted log transformation**

---

## 📝 License

MIT License © 2025 Muhammad Akmal Husain

## 🔗 Links

- **[GitHub Repository](https://github.com/AkmalHusain2003/enhanced-automatic-shifted-log)**
- **[Documentation](https://github.com/AkmalHusain2003/enhanced-automatic-shifted-log#readme)**