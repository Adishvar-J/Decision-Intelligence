from ingest import Ingest
from db import Db
import re
import pandas as pd
import numpy as np

ingest = Ingest()
db = Db()

class Data():
    """1. fetch 2. Load 3. clean 4. Normalize 5. validate 6. transform"""
    def __init__(self, user_id = None):
        self.user_id = user_id
        self.data = None
        self.dt = None
        self.df = None

    def fetch(self, user_id = None):
        uid = user_id or self.user_id
        if uid is None:
            raise ValueError("No user id provided to fetch data")
        result = db.get_data(id=uid)
        if not result:
            raise LookupError(f"No data found for id={uid}")
        self.data = result
        self.user_id = uid
        return self

    def load(self):
        """uses file name and file data as bytes"""
        if self.data is None:
            raise RuntimeError("Call fetc() before load()")

        if len(self.data) < 2:
            raise ValueError(f"Expected data as (filename, file_data), got: {self.data}")
        filename, filebytes = self.data[0], self.data[1]
        self.dt = ingest.load(filename=filename, file_data=filebytes)

        return self

    def p_test(self, dff):
        if dff is None:
            raise ValueError(f"Got {dff}")
        
        print("shape: ", dff.shape)
        print("\ncolumns: ", dff.columns.to_list())
        print("\nTypes: \n", dff.dtypes)
        print("\nempty: \n", dff.isnull().sum())
        print("\nduplicates: \n", dff.duplicated().sum())

    def clean(self):
        self.dt = self.dt.dropna(how="all") # empty rows
        self.dt = self.dt.dropna(axis=1, how="all") # empty columns
        self.dt = self.dt.drop_duplicates() # duplicates

        self.dt.columns = (
            self.dt.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )


    def normalize(self, sample_size: int = 1000, threshold: float = 0.9):
        """Automatic dtypes inference, sample_size = 1000, threshold = 0.9"""
        self.clean()
        self.df = self.dt.copy()

        bool_map = {
            'true': True, 'false': False, 'yes': True, 'no': False, '1': True, '0': False, 't': True, 'f': False, 'y': True, 'n': False
        }

        for col in self.df.columns:
            series = self.df[col]

            if pd.api.types.is_numeric_dtype(series) or pd.api.types.is_datetime64_any_dtype(series) or pd.api.types.is_bool_dtype(series):
                continue

            s = series.astype(str).str.strip()
            s = s.replace(['', 'nan', 'none', 'null', 'na', 'n/a', 'NaN'], np.nan)

            sample = s.sample(min(len(s), sample_size), random_state=42)
            # bool check
            lower_sample = sample.str.lower()
            if  lower_sample.isin(bool_map.keys()).mean() >= threshold:
                self.df[col] = s.str.lower().map(bool_map)
                continue

            # numeric check
            cleaned_num = sample.str.replace(r'[,$%]', '',regex=True)
            numeric_converted = pd.to_numeric(cleaned_num, errors='coerce')
            if numeric_converted.notna().mean() >= threshold:
                full_cleaned = s.str.replace(r'[,$%]','', regex=True)
                self.df[col] = pd.to_numeric(full_cleaned, errors='coerce')
                continue

            # date time check
            date_converted = pd.to_datetime(sample, errors='coerce', format='mixed')
            if date_converted.notna().mean() >= threshold:
                self.df[col] = pd.to_datetime(s, errors='coerce')
                continue

            # categorical check (low ccardinality)
            if s.nunique() / len(s) < 0.05:
                self.df[col] = s.astype('category')
                continue

            self.df[col] = s

        return self.df


    def validate(self):
        if self.df.empty:
            raise ValueError("Dataset is empty")

        mv = self.df.duplicated().sum()
        # numeric validity check
        result = {}
        for column in self.df.select_dtypes(include='number').columns:
            result[column] = {
                "min": float(self.df[column].min()),
                "max": float(self.df[column].max()),
                "missing": int(self.df[column].isna().sum())

            }
        
        report = {
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "missing_values": int(mv),
            "numeric_columns": result,
        }

        return report


    def transform(self):
        """Transform validated data frame into analytics ready data frame"""
        df = self.df.copy()

        # handling missing vaues
        for column in df.columns:
            if df[column].dtypes == "object":
                df[column] = df[column].fillna("Unknown")
            elif pd.api.types.is_numeric_dtype(df[column]):
                if df[column].notna().any():
                    median = df[column].median()
                    df[column] = df[column].fillna(median)
            elif pd.api.types.is_datetime64_any_dtype(df[column]):
                pass

        # handling text values
        text_columns = df.select_dtypes(
            include=["object"]
        ).columns

        for columns in text_columns:
            df[columns] = (
                df[columns]
                .astype(str)
                .str.strip()
            )
            df[columns] = df[columns].replace("", "Unknown")

        # standardizing column names

        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("-", "_")
        )

        # remove duplicates and resetting index

        df = df.drop_duplicates()
        df = df.reset_index(drop=True)

        return df












# ddd = Data()
# ddd.fetch(user_id=1).load().clean()
# ddd.normalize()
# ddd.p_test(ddd.df)
# # ddd.p_test()

# # print()

# ddd.normalize()
# # # print()

# # ddd.p_test(dff=ddd.df)

# print(ddd.validate())





