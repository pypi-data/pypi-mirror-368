# Banca d'Italia Microdata Extractor – Indagine sui Bilanci delle Famiglie Italiane (BFI)

This project provides tools for navigating and processing the [Banca d'Italia microdata](https://www.bancaditalia.it/statistiche/tematiche/indagini-famiglie-imprese/bilanci-famiglie/index.html?dotcache=refresh) from the survey **"Bilanci delle famiglie italiane" (BFI)**. It includes a Python class `BIMicrodataExtractor` with structured methods to explore, query, and analyze the BFI dataset efficiently.

## 📦 Project Structure

The central component is the `BIMicrodataExtractor` class, which offers:

- 🚀 Simplified access to the dataset structure
- 🧠 Attribute encoding utilities
- 🔎 Filtering and pairing logic for household members
- 📊 Joint and conditional distribution tools
- 📁 Integration-ready design for larger analytical pipelines

## 📚 Dataset Overview

**Bilanci delle famiglie italiane (BFI)** is an biennial survey by Banca d'Italia capturing detailed financial aspects of Italian households. It includes information on:

- Demographics
- Employment, unemployment and pension conditions
- Families earnings, passive income and transfer income
- Housing conditions (rent, property, loan)
- Family debts
- Family wealth and assets
- Payment options
- Saving solutions
- Families expenses
- Insurance solutions

After loading the data in the `BIMicrodataExtractor` class, the information relative to the families in general will be stored in the attribute `df_families`, while the information about the single members of the families will be stored in the attribute `df_familymembers`.

## 🧩 Key Features of `BIMicrodataExtractor`

| Method/Attribute                | Description                                                                |
|---------------------------------|----------------------------------------------------------------------------|
| `load_data()`                   | Loads and prepares the AVQ microdata from raw files                        |
| `attribute_categories`          | Attribute that contains all the categories for the attributes              |
| `get_attribute_metadata()`      | Retrieves metadata/encodings for categorical variables                     |
| `get_attributes_by_categories()`| Filters attributes by categories                                           |
| `filter()`                      | Applies logical filters on individual-level records                        |
| `pair_family_members()`         | Pairs individuals within the same household according to flexible rules    |
| `joint_distribution()`          | Computes joint/marginal distributions for selected variables               |


### Installing & Setup

```bash
git clone git@github.com:Clearbox-AI/bancaitalia-microdata-extractor.git

pip install -r path/to/bancaitalia-microdata-extractor/requirements.txt

pip install -e path/to/bancaitalia-microdata-extractor
```

To setup your **AVQ ISTAT Microdata**, unzip the data folder you find [here](https://github.com/Clearbox-AI/ISTAT-microdata-extractor/tree/main/data) and provide the path to the unzipped folder to the `load_data()` method of your `BIMicrodataExtractor` class to get started!

Unlike raw data, this data was processed to allow some methods of the class `BIMicrodataExtractor` to work smoothly.

#### Updating version

To update your local version go to your local folder and run:

```bash
git pull origin main

pip install -e bancaitalia-microdata-extractor
```

### 📊 Examples
```python
from microdata_extractor import BIMicrodataExtractor

# Supposing your AVQ Microdata ISTAT is stored in "BFI_2022"
# After loading the data, the class bfi will features two attributes being:
# - bfi.df_families (with information about the families) 
# - bfi.df_familymembers (with information about the single members of the families)
mde = BIMicrodataExtractor()
mde.load_data("BFI_2022")


# Consult the available attribute categories 
mde.attribute_categories

# Filter attributes by relevant categories
_ = mde.get_attributes_by_categories("demographics","unemployment" condition="or")

# Check encodings for categorical variables
_ = mde.get_attribute_metadata("STUDIO", print_output=True)
_ = mde.get_attribute_metadata("OCCNOW", print_output=True)

# Compute the joint probability distributions of STUDIO (education level) and OCCNOW (employed/not employed)
# Compute it only for adults at the time of th esurvay (2022) -> born before 2003 (ANASC<=2003)
rules = [("ANASC","<=",2003)]
df_prob = mde.joint_distribution(attrs=["STUDIO","OCCNOW"], df=mde.df_familymembers, conditions=rules)
```

### Contacts

📧 info@clearbox.ai

🌐 [www.clearbox.ai](https://www.clearbox.ai/)