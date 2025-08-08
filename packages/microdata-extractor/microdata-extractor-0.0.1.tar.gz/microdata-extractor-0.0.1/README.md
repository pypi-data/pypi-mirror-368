# ISTAT Microdata Extractor – Aspetti della Vita Quotidiana (AVQ)

This project provides tools for navigating and processing the **ISTAT microdata**. It includes the Python class `ISTATMicrodataExtractor` with structured methods to explore, query, and analyze the microdata efficiently.

Available microdata:
- [AVQ](https://www.istat.it/microdati/aspetti-della-vita-quotidiana/): Indagine sugli Aspetti della Vita Quotidiana (AVQ) delle famiglie italiane
- [HBS](https://www.istat.it/microdati/indagine-sulle-spese-delle-famiglie-uso-pubblico/): Indagine sulle spese delle famiglie italiane

## 📦 Project Structure

The central component is the `ISTATMicrodataExtractor` class, which offers:

- 🚀 Simplified access to the dataset structure
- 🧠 Attribute encoding utilities
- 🔎 Filtering and pairing logic for household members
- 📊 Joint and conditional distribution tools
- 📁 Integration-ready design for larger analytical pipelines

## 📚 Dataset Overview

**Aspetti della Vita Quotidiana (AVQ)** is an annual survey by ISTAT capturing detailed aspects of daily life in Italian households. It includes information on:

- Demographics
- Education and employment
- Health and access to services
- Household composition and living conditions
- Digital device usage and internet access
- Family dynamics and caregiving
- Purchase habits

## 🧩 Key Features of `ISTATMicrodataExtractor`

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
git clone git@github.com:Clearbox-AI/ISTAT-microdata-extractor.git

pip install -r path/to/ISTAT-microdata-extractor/requirements.txt

pip install -e path/to/ISTAT-microdata-extractor
```

#### Updating version

To update your local version go to your local folder and run:

```bash
git pull origin main

pip install -e ISTAT-microdata-extractor
```

To setup the data, unzip the data folder you need [here](https://github.com/Clearbox-AI/ISTAT-microdata-extractor/tree/main/data) and provide the path to the unzipped folder to the `load_data()` method of your `ISTATMicrodataExtractor` class.

Unlike raw data, this data was processed to allow some methods of the class `BIMicrodataExtractor` to work smoothly.

### 📊 Examples
```python
from microdata_extractor import ISTATMicrodataExtractor

# Supposing your AVQ Microdata ISTAT is stored in "AVQ_2023_IT"
mde = ISTATMicrodataExtractor(df_name="AVQ",year=2023)
mde.load_data("AVQ_2023_IT")

# Consult the available attribute categories 
mde.attribute_categories

# Filter attributes by relevant categories
_ = mde.get_attributes_by_categories("demographics","sport", "health_conditions", condition="or")

# Check encodings for categorical variables
encoding = mde.get_attribute_metadata("FREQSPO", print_output=True)

# Filter main dataset based on user-defined rules
# Tuples within the same inner list are AND-ed, tuples belonging to different inner lists are OR-ed
# The following rules express: (age>=18 AND BMI<=3)  OR  (age<18 AND BMIMIN==1)
rules = [
    [("ETAMi",">=",7),("BMI","<=",3)],  # Adults (age>=18) AND BMI==[1,2,3]
                                        # OR
    [("ETAMi","<",7),("BMIMIN","==",1)] # minors (age<18) AND BMIMIN==1
]

df_filtered = mde.filter(rules)
```

Check out the [Examples folder](https://github.com/Clearbox-AI/ISTAT-microdata-extractor/tree/main/Examples) for more!

### Contacts

📧 info@clearbox.ai

🌐 [www.clearbox.ai](https://www.clearbox.ai/)