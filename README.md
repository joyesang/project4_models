# project 4 models

## Comparing Predictors of Employment Among Adults With and Without Cognitive Difficulties in the United States: Using Random Forest and SHAP Analyses

### Overview
<p style="text-indent: 30px;">
This project examines factors associated with employment among adults with and without cognitive difficulties in the United States. Using data from the 2024 American Community Survey (ACS), Random Forest models were estimated separately for respondents with and without cognitive difficulties. SHapley Additive exPlanations (SHAP) were then used to interpret predictor importance and direction of effects.</p>

<br>

### Data Source

- Dataset: 2024 American Community Survey (ACS) Public Use Microdata Sample (PUMS)
- Source: U.S. Census Bureau
- Population: U.S. residents aged 16 years and older

|Group|Sample Size|
|:----|----------:|
|Respondents with Cognitive Difficulties| 204,057|
|Respondents without Cognitive Difficulties| 2,655,459|

<br>

### Variables

#### Outcome Variable: `EMPLOYED`
 - 1 = Employed
 - 0 = Unemployed or Not in Labor Force

 #### Predictor Variables
 - Age
 - Sex
 - Educational Attainment
 - Marital Status
 - Race
 - Poverty Status
 - Hearing Difficulty
 - Vision Difficulty
 - Independent Living Difficulty

<br>

### Methods

#### Random Forest

Random Forest classification models were estimated separately for respondents with and without cognitive difficulties.

Model performance was evaluated using:

* Training Accuracy
* Testing Accuracy

#### SHAP Analysis

SHapley Additive exPlanations (SHAP) were used to:

* Identify important predictors
* Examine the direction of predictor effects
* Compare predictor patterns across groups

<br>

### Key finding

Independent living difficulty was substantially more important among adults with cognitive difficulties than among those without cognitive difficulties, suggesting that functional independence may play a particularly important role in employment outcomes for this population.

<br>

### Repository Structure

project4_models/
│
├── project4_models.ipynb
├── report.qmd
├── report.html
├── images/
│   ├── shap_cognitive_difficulty.png
│   └── shap_no_cognitive_difficulty.png
│
└── README.md

<br>

### API Key
This project uses the U.S. Census Bureau API.
Obtain a free API key from: https://api.census.gov/data/key_signup.html

Replace:
`CENSUS_API_KEY = "YOUR_CENSUS_API_KEY"`
with your personal API key before running the code.