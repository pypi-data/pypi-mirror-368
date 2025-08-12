# Enhanced Automatic Shifted Log Transformer

**Automatically transform skewed data into more normal distributions using Monte Carlo optimized shifted log transformation.**

---

## 📌 Overview

This transformer improves data normality by applying an **automatically tuned shifted log transformation**. It uses **Monte Carlo optimization** with Dirichlet sampling to find the best shift parameters for each feature.

✅ **Reduces skewness**  
✅ **Stabilizes variance**  
✅ **Scikit-learn compatible**  
✅ **Fast** (Numba-accelerated)

---

## 🔧 Installation

```bash
pip install enhanced-automatic-shifted-log
```

Or from source:

```bash
git clone https://github.com/AkmalHusain2003/enhanced-automatic-shifted-log.git
cd enhanced-automatic-shifted-log
pip install -e .
```

---

## 🚀 Quick Start

```python
from enhanced_aslt import AutomaticShiftedLogTransformer

# Fit & transform
transformer = AutomaticShiftedLogTransformer(mc_iterations=1000, random_state=42)
transformed_data = transformer.fit_transform(your_data)
```

---

## 📊 Example: Before vs After

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Create side-by-side comparison plots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

# Plot original data
sns.histplot(original_data, ax=ax1, color='red')
ax1.set_title('Before Transformation')

# Plot transformed data
sns.histplot(transformed_data, ax=ax2, color='green')
ax2.set_title('After Transformation')

plt.tight_layout()
plt.show()
```

---

## ⚙️ Key Parameters

| Parameter                | Description                                   | Default |
|--------------------------|-----------------------------------------------|---------|
| `mc_iterations`          | Monte Carlo iterations                        | 1000    |
| `random_state`           | Random seed                                   | None    |
| `min_improvement_skewed` | Minimum skewness improvement for skewed data  | 0.02    |
| `normality_threshold`    | Shapiro-Wilk threshold to skip transformation | 0.9     |

---

## 🔬 How It Works

The Enhanced Automatic Shifted Log Transformer uses Monte Carlo optimization to automatically find the optimal shift parameter for each feature:

1. **Skewness Detection**: Identifies features that would benefit from transformation
2. **Monte Carlo Optimization**: Uses Dirichlet sampling to explore shift parameter space
3. **Normality Assessment**: Applies Shapiro-Wilk test to evaluate transformation quality
4. **Adaptive Processing**: Only transforms features that show significant improvement

---

## 📈 Performance Benefits

- **Automatic Parameter Tuning**: No manual hyperparameter selection required
- **Feature-Wise Optimization**: Each column gets individually optimized parameters
- **Computational Efficiency**: Numba acceleration for fast processing
- **Robust Statistics**: Uses multiple normality metrics for reliable results

---

## 🧪 Advanced Usage

```python
from enhanced_aslt import AutomaticShiftedLogTransformer
import numpy as np

# Generate sample skewed data
np.random.seed(42)
skewed_data = np.random.exponential(2, (1000, 3))

# Initialize transformer with custom parameters
transformer = AutomaticShiftedLogTransformer(
    mc_iterations=2000,
    random_state=42,
    min_improvement_skewed=0.05,
    normality_threshold=0.95
)

# Fit and transform
X_transformed = transformer.fit_transform(skewed_data)

# Access transformation parameters
print("Optimal shift parameters:", transformer.shift_params_)
print("Features transformed:", transformer.features_transformed_)

# Inverse transform (if needed)
X_original = transformer.inverse_transform(X_transformed)
```

---

## 📚 References

- Feng, Q., Hannig, J., & Marron, J. S. (2016). *A Note on Automatic Data Transformation*. arXiv:1601.01986 [stat.ME]. https://arxiv.org/abs/1601.01986
- Tukey, J. W. (1977). *Exploratory Data Analysis*. Addison-Wesley.
- Box, G. E. P., & Cox, D. R. (1964). *An analysis of transformations*. Journal of the Royal Statistical Society, 26(2), 211-252.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 🐛 Issues

If you encounter any issues or have suggestions for improvements, please open an issue on the [GitHub repository](https://github.com/AkmalHusain2003/enhanced-automatic-shifted-log/issues).

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Muhammad Akmal Husain**

- GitHub: [@AkmalHusain2003](https://github.com/AkmalHusain2003)
- Email: [akmalhusain2003@gmail.com](mailto:akmalhusain2003@gmail.com)

---

## 🌟 Show Your Support

If this project helped you, please consider giving it a ⭐️ on GitHub!

---

*Built with ❤️ for the data science community*