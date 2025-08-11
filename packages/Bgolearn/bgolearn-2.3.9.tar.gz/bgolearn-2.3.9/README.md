# **Bgolearn** — Bayesian Global Optimization for Material Design

**Latest version:** 2.3.9 (released Aug 11, 2025) :
A lightweight, extensible Python package tailored for Bayesian global optimization in material design.

---

##  Key Features

- **Regression & Classification Support**: Implements advanced acquisition functions for regression tasks and active learning strategies like least confidence, margin sampling, and entropy-based classification.
- **Comprehensive Acquisition Functions**: Includes single-objective acquisition strategies such as Expected Improvement (EI), Expected Improvement with Plugin, Augmented EI (AEI), Expected Quantile Improvement (EQI), Reinterpolation EI (REI), Upper Confidence Bound (UCB), Probability of Improvement (PI), Predictive Entropy Search (PES), and Knowledge Gradient (KG).
- **Pipeline for Virtual Screening & Active Learning**: Enables iterative experiment → prediction → update loops to efficiently accelerate materials discovery.
- **Multi-Objective Extension via MultiBgolearn**: Supports optimization across multiple material properties using MOBO techniques; package `MultiBgolearn` (latest version 0.0.7 released December 13, 2024) significantly extends Bgolearn’s capabilities.
- **Graphical Interface with BgoFace**: Bgoface, a GUI frontend to interact with Bgolearn visually—ideal for users preferring no-code workflows.
- **Lightweight & MIT-Licensed**: Simple installation, zero dependencies beyond Python 3.5+, highly modular under the MIT License for academic and commercial use.

---


Quick Usage Example
from Bgolearn.BGOsampling import Bgolearn
import pandas as pd

# Load your data
data = pd.read_csv('data.csv')
X = data.iloc[:, :-1]
y = data.iloc[:, -1]

# (Optional) Provide virtual samples for screening
vs = pd.read_csv('virtual_data.csv')

# Create and configure optimizer
optimizer = Bgolearn()
model = optimizer.fit(data_matrix=X, Measured_response=y, virtual_samples=vs)

# Run Expected Improvement acquisition
candidates = model.EI()



### Support & Contribution
Author & Maintainer: Dr. Bin Cao (CaoBin) — email: bcao686@connect.hkust-gz.edu.cn.

### Collaboration Welcome: Open for issues, pull requests, and research partnerships.

