<div style="background-color: white; display: inline-block; padding: 10px; border-radius: 5px;">
  <img src="./docs/source/_static/assets/200x150/light_logo.svg" alt="Phenotypic Logo" style="width: 200px; height: auto;">
</div>

# PhenoTypic: A Python Framework for Bio-Image Analysis
![Development Status](https://img.shields.io/badge/status-Pre--Alpha-red)

A modular image processing framework developed at the NSF Ex-FAB BioFoundry.

---

*Documentation* @ https://wheeldon-lab.github.io/PhenoTypic/

## Overview
PhenoTypic provides a modular toolkit designed to simplify and accelerate the development of bio-image analysis pipelines. 
Its structured architecture allows researchers and developers to seamlessly integrate custom computer vision modules, avoiding 
the need to build entirely new packages from scratch. Additionally, PhenoTypic supports incorporating components from 
other existing image analysis tools into a cohesive, unified ecosystem.


## Installation

### Pip
```
pip install phenotypic
```
Note: may not always be the most up-to-date version. Install from repo when latest update is needed

### Manual Installation
```  
git clone https://github.com/Wheeldon-Lab/PhenoTypic.git
cd PhenoTypic
pip install -e .
```  

### Dev Installation
```  
git clone https://github.com/Wheeldon-Lab/PhenoTypic.git
cd PhenoTypic
pip install -e ".[dev]"
```  

## Acknowledgements

### CellProfiler

**Reference:**
- [CellProfiler GitHub Repository](https://github.com/CellProfiler/CellProfiler)
- [CellProfiler Official Website](https://cellprofiler.org/)