# NUVA Python SDK

The **Unified Vaccine Nomenclature (NUVA)** Python SDK provides a comprehensive interface for working with vaccine nomenclature data. It's designed to aggregate vaccination histories from both digital and physical sources and build interpretable vaccination records for information systems.

## Installation

```bash
pip install nuva-sdk
```

## Quick Start

```python
from nuva import Nuva

# Load the latest NUVA database
nuva = Nuva.load(lang='en')

# Access repositories
vaccines = nuva.repositories.vaccines.all()
valences = nuva.repositories.valences.all()
diseases = nuva.repositories.diseases.all()

# Find specific items
vaccine = nuva.repositories.vaccines.find('vaccine_id')
valence = nuva.repositories.valences.find('valence_id')
disease = nuva.repositories.diseases.find('disease_id')

# Use queries for advanced searches
valences_for_vaccine = nuva.queries.valences_by_vaccine.call(vaccine)
vaccines_for_disease = nuva.queries.vaccines_by_disease.call(disease)
```

## Core Concepts

### Repositories

The library provides three main repositories:

- **vaccines**: Access to vaccine data
- **valences**: Access to valence (functional units) data  
- **diseases**: Access to target disease data

Each repository exposes two methods:
- `all()`: Retrieve the entire collection
- `find(id)`: Retrieve a specific element by its identifier

### Queries

For advanced searches, the library provides query objects:

- `valences_by_vaccine`: Find valences for a given vaccine
- `vaccines_by_disease`: Find vaccines targeting a specific disease
- `vaccines_by_valence`: Find vaccines containing a specific valence
- `valences_by_disease`: Find valences targeting a specific disease
- `diseases_by_vaccine`: Find diseases targeted by a vaccine
- `diseases_by_valence`: Find diseases targeted by a valence

### Loading Data

You can load NUVA data in two ways:

1. **From CDN** (recommended):
```python
nuva = Nuva.load(lang='en')  # Supports: en and fr
```

2. **From local file**:
```python
nuva = Nuva.load_from_file('path/to/database.db')
```

## License

This project is licensed under the MIT License.

## Contributing

Please see the main NUVA repository for contribution guidelines.
