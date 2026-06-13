import requests
import json
import pandas as pd
import pycps
import os
import census
import us
import datetime
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import shap
#%%
CENSUS_API_KEY = "YOUR_CENSUS_API_KEY"

# %% Import ACS data

def import_acs_2024():

    variables = ["ESR", "AGEP", "SEX", "SCHL", "MAR",
                 "RAC1P", "DREM", "DEAR", "DEYE", "DOUT", 
                 "PINCP", "POVPIP"]

    url = ("https://api.census.gov/data/2024/acs/acs1/pums")

    params = {"get": ",".join(variables),
              "for": "region:*",
              "key": CENSUS_API_KEY}

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()

    df = pd.DataFrame(data[1:], columns=data[0])
    
    for col in variables:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["YEAR"] = int("2024")

    # Data cleaning
    ## Age
    df = df[df["AGEP"] >= 16]

    ## Employment 
    df = df[~df["ESR"].isin([4, 5])]
    df = df.dropna(subset=["ESR"])
    df["EMPLOYED"] = df["ESR"].isin([1, 2]).astype(int)

    ## Sex
    df["MALE"] = (df["SEX"] == 1).astype(int)
    
    # SCHL to EDUCATION
    df["SCHL"] = pd.to_numeric(df["SCHL"], errors="coerce")
    
    df["EDUCATION"] = pd.NA
    df.loc[df["SCHL"].between(1, 15), "EDUCATION"] = 0 # Less than High School
    df.loc[df["SCHL"].between(16, 17), "EDUCATION"] = 1 # High School Diploma
    df.loc[df["SCHL"].between(18, 21), "EDUCATION"] = 2 # College level
    df.loc[df["SCHL"].between(22, 24), "EDUCATION"] = 3 # Graduate School level
    
    df["EDUCATION"] = df["EDUCATION"].astype("Int64")

    ## MAR to MARRIED
    df["MARRIED"] = (df["MAR"] == 1).astype(int)

    ## RAC1P to Race
    df["RACE_BLACK"] = (df["RAC1P"] == 2).astype(int)
    df["RACE_ASIAN"] = (df["RAC1P"] == 6).astype(int)
    df["RACE_OTHER"] = (df["RAC1P"].isin([3, 4, 5, 7, 8, 9])).astype(int)

    # Disability variables
    df["COGNITIVE_DIFF"] = (df["DREM"] == 1).astype(int)
    df["HEARING_DIFF"] = (df["DEAR"] == 1).astype(int)
    df["VISION_DIFF"] = (df["DEYE"] == 1).astype(int)
    df["INDEP_LIVING_DIFF"] = (df["DOUT"] == 1).astype(int)

    ## PINCP to Personal_Income
    df = df.dropna(subset=["PINCP"])
    df["PERSONAL_INCOME"] = df["PINCP"]

    ## POVPIP to Poverty (100% FPL)
    df = df.dropna(subset=["POVPIP"])
    df["POVERTY"] = (df["POVPIP"] < 100).astype(int)

    # Keep cleaned variables only
    final_vars = ["YEAR", "EMPLOYED", "AGEP", "MALE", "EDUCATION", 
                  "MARRIED", "RACE_BLACK", "RACE_ASIAN", "RACE_OTHER",
                  "COGNITIVE_DIFF", "HEARING_DIFF", "VISION_DIFF", 
                  "INDEP_LIVING_DIFF", "PERSONAL_INCOME", "POVERTY"]

    df = df.dropna(subset=final_vars)
    df = df[final_vars]
       
    return df

# %% Random forest model
def random_forest_by_cognitive_group(df):

    predictors = ["AGEP", "MALE", "EDUCATION", "MARRIED", "RACE_BLACK",
                  "RACE_ASIAN", "RACE_OTHER", "HEARING_DIFF", "VISION_DIFF",
                  "INDEP_LIVING_DIFF", "POVERTY"]

    results = {}

    for group_value, group_name in [(1, "Cognitive Difficulty"), 
                                    (0, "No Cognitive Difficulty")]:

        group_df = df[df["COGNITIVE_DIFF"] == group_value].copy()
        X = group_df[predictors]
        y = group_df["EMPLOYED"]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            random_state=42,
            stratify=y)

        model = RandomForestClassifier(n_estimators=500, max_depth=5,
                                       random_state=42, class_weight="balanced")

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)

        feature_importance = pd.DataFrame({
            "variable": predictors,
            "importance": model.feature_importances_
            }).sort_values("importance", ascending=False)

        results[group_name] = {
            "model": model,
            "train_score": train_score,
            "test_score": test_score,
            "feature_importance": feature_importance,
            "sample_size": len(group_df)}

    return results
#%%
def shap_by_cognitive_group(df, rf_results, sample_size=2000):

    predictors = ["AGEP", "MALE", "EDUCATION", "MARRIED", "RACE_BLACK",
                  "RACE_ASIAN", "RACE_OTHER", "HEARING_DIFF", "VISION_DIFF",
                  "INDEP_LIVING_DIFF", "POVERTY"]

    os.makedirs("images", exist_ok=True)

    groups = [(1, "Cognitive Difficulty", "cognitive_difficulty"),
              (0, "No Cognitive Difficulty", "no_cognitive_difficulty")]

    for group_value, group_label, file_name in groups:
        group_df = df[df["COGNITIVE_DIFF"] == group_value].copy()
        X = group_df[predictors]
        X_sample = X.sample(
            n=min(sample_size, len(X)),
            random_state=42)

        model = rf_results[group_label]["model"]
        explainer = shap.TreeExplainer(model)

        shap_values = explainer.shap_values(X_sample)

        if isinstance(shap_values, list):
            shap_values_class1 = shap_values[1]

        else:
            shap_values_class1 = shap_values[:, :, 1]

        shap.summary_plot(shap_values_class1, X_sample,
                          plot_type="dot", show=False)

        fig = plt.gcf()

        fig.savefig(f"images/shap_{file_name}.png",
            dpi=300, bbox_inches="tight")

        plt.show()

# %%
df = import_acs_2024()
# %%
rf_results=random_forest_by_cognitive_group(df)
# %%
shap_by_cognitive_group(df, rf_results, sample_size=2000)

# %%
