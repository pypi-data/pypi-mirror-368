# Noise-Aware Cluster Validity Indices (NACVI)

 This repository contains a Python implementation of internal cluster validity indices specifically designed for **noise-aware Clusterings** (e.g. DBSCAN). The validity indices presented here explicitly consider **unassigned data points (noise)**, which makes them particularly suitable for realistic, unsupervised settings.

> This is based on the scientific publication:  
> **Lea Eileen Brauner, Frank Höppner, Frank Klawonn**  
> *Cluster Validity for Noise-Aware Clusterings*, Intelligent Data Analysis Journal, IOS Press (2025)

---

## Content

You can find the implementations of the following NACVIs:

- `sil+`: noise-aware Silhouette Coefficient
- `dbi+`: noise-aware Davies-Bouldin Index
- `gD33+`: noise-aware Dunn-Index-Variant
- `sf+`: noise-aware Score Function
- `grid+`: grid-based noise-validity index
- `nr+`: neighbourhood-based Noise-validity index

---

## Motivation

Conventional validity measures treat **all data points as belonging to a cluster**, even if noise is explicitly labelled in DBSCAN, for example. This leads to distorted evaluations.

This package:
- takes noise into account correctly,
- enables a separate evaluation of the **cluster structure** and the **noise delimitation**,
- offers an **integrated metric** for both with the `B+` score.

---

## Installation

```bash
pip install nacvi
```

## Usage

In examples/usage_miniexample.py you can find a minimal example for the usage with numpy arrays as inputs.

In examples/usage_example.ipynb you can find a comprehensive example with:
- data generation,
- execution of the DBSCAN clustering algorithm,
- visualisation,
- calculation of the NACVIs
