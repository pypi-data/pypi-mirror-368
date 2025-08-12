# Neuber Correction 💥

[![PyPI version](https://badge.fury.io/py/neuber-correction.svg)](https://badge.fury.io/py/neuber-correction)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://manuel1618.github.io/neuber-correction/)

A Python tool that corrects elastic FEA results for plastic yielding using Neuber's rule. No more manual iterations or Excel spreadsheets - just plug in your material properties and get accurate stress corrections.

## 🚀 Quick Start

```python
from neuber_correction import NeuberCorrection, MaterialForNeuberCorrection

# Set up your material (Aluminum 6061-T6 example)
material = MaterialForNeuberCorrection(
    yield_strength=240,      # MPa
    sigma_u=290,    # MPa  
    elastic_mod=68900, # MPa (69 GPa)
    eps_u=0.10     # 10%
)

neuber = NeuberCorrection(material)

# Get your corrected stress
elastic_stress = 500  # MPa
corrected_stress = neuber.correct_stress_values([elastic_stress])[0]
print(f"Elastic: {elastic_stress} MPa → Corrected: {corrected_stress:.1f} MPa")
# Output: Elastic: 500 MPa → Corrected: 260.0 MPa
```

## 📖 What's the Deal?

When your elastic FEA gives you stresses above the yield strength, those values are unrealistic because they don't account for plastic yielding. Neuber correction fixes that by finding the intersection between the Neuber hyperbola and your material's actual stress-strain curve.

**Example**: Aluminum 6061-T6 with 500 MPa elastic stress → 260 MPa corrected stress (48% reduction!)

## ✨ What You Get

✅ **Accurate stress corrections** - No more overestimating elastic stresses  
✅ **Material-specific calculations** - Uses Ramberg-Osgood model  
✅ **Visual analysis** - Plot the curves and see what's happening  
✅ **Batch processing** - Handle multiple stress values at once  
✅ **Robust convergence** - Newton-Raphson with fallback methods  
✅ **Performance optimized** - Caching and memoization for repeated calculations  

## 🎯 Perfect For

- **FEA result correction** when stresses exceed yield
- **Fatigue analysis** with plastic yielding
- **Material testing** data analysis
- **Design validation** and optimization

## 📦 Installation

```bash
pip install neuber-correction
```

Or if you're using uv (recommended):
```bash
uv add neuber-correction
```

## 🔧 Usage Examples

### Basic Stress Correction
```python
from neuber_correction import NeuberCorrection, MaterialForNeuberCorrection

# Steel S355
material = MaterialForNeuberCorrection(
    yield_strength=315,
    sigma_u=470,
    elastic_mod=210000,
    eps_u=0.12
)

neuber = NeuberCorrection(material)

# Correct your FEA results
elastic_stresses = [400, 500, 600]  # MPa
corrected_stresses = neuber.correct_stress_values(elastic_stresses)
```

### Visual Analysis
```python
# Create a plot showing the correction
fig, ax = neuber.plot_neuber_diagram(500, show_plot=True)
```

### Advanced Settings
```python
from neuber_correction import NeuberSolverSettings

# Custom convergence settings
settings = NeuberSolverSettings(
    tolerance=1e-8,        # More precise
    max_iterations=1000    # More iterations
)

neuber = NeuberCorrection(material, settings)
```

### Performance Features
```python
# Automatic caching for repeated calculations
result1 = neuber.correct_stress_values([500])[0]  # Computes
result2 = neuber.correct_stress_values([500])[0]  # Uses cache (fast!)

# Clear cache if needed
NeuberCorrection.clear_all_instances()
```

## 📚 Documentation

📖 **[Full Documentation](https://manuel1618.github.io/neuber-correction/)**

- **[Quick Start Guide](https://manuel1618.github.io/neuber-correction/quick_start/)** - Get up and running fast
- **[Theory](https://manuel1618.github.io/neuber-correction/theory/)** - The math behind the magic
- **[FAQ](https://manuel1618.github.io/neuber-correction/faq/)** - Common questions and answers

## 🔬 Theory

Neuber's rule states that the product of stress and strain remains constant:

$$\sigma \cdot \varepsilon = \frac{\sigma_e^2}{E}$$

Where:
- $\sigma$ = actual (corrected) stress
- $\varepsilon$ = actual strain  
- $\sigma_e$ = elastic stress (from FEA)
- $E$ = Young's modulus

The tool finds the intersection between the Neuber hyperbola and the Ramberg-Osgood material curve to determine the corrected stress.

## 🛠️ Development

### Setup
```bash
git clone https://github.com/manuel1618/neuber-correction.git
cd neuber-correction
uv sync
```

### Testing
```bash
uv run pytest
```

### Linting
```bash
uv run task lint
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📖 Sources

This tool is based on [Neuber's rule for stress concentration analysis](https://doi.org/10.1016/j.prostr.2017.07.116)

---

**Made with ❤️ for engineers who need accurate stress analysis**

