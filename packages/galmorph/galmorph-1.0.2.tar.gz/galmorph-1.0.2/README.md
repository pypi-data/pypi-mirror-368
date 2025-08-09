# GalMorph

**GalMorph** is a Python package for classifying simulated galaxies into elliptical, spiral, or irregular based on their morphology probability in the TNG simulation ([TNG Project](https://www.tng-project.org/)).  

This tool is designed to work with `.pkl` files containing specific probability columns and enables basic classification, filtering, and visualization of galaxy morphologies.


---

## Expected Data Format

The input should be a **Pickle file (`.pkl`)** that can be loaded as a Pandas DataFrame, containing the following columns:

### Required Columns

| Column Name   |Description                                         | Type   |
|---------------|----------------------------------------------------|--------|
| `Snapshot`    | Simulation snapshot number                         | int    |
| `SubhaloID`   | Unique identifier for the galaxy/subhalo           | int or str |
| `P_irr`       | Probability the galaxy is irregular                | float (0–1) |
| `P_disk`      | Probability the galaxy is a disk                   | float (0–1) |
| `P_spheroid`  | Probability the galaxy is a spheroid               | float (0–1) |

### Notes:
- Each probability should be a float between `0` and `1`.

---
## Installation

```bash
git clone https://github.com/ImPriyatam/galmorph.git
cd galmorph
pip install .
```
To follow the steps, see the documentation [here](https://ImPriyatam.github.io/galmorph/).

> _(If you're working locally, you can also open `docs/_build/html/index.html` in your browser.)_


---

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.


[def]: docs/_build/html/index.html