# analytics and feature discovery
import pandas as pd
from data import Data


class Analyzer():
    def analyze(self, df):
        result = {
            "rows": len(df),
            "columns": len(df.columns),
            "numeric": {},
            "categorical": {},
            "datetime": {}
        }

        for  column in df.columns:
            series = df[column]

            if pd.api.types.is_numeric_dtype(series):
                result["numeric"][column] = {
                    "min": float(series.min()),
                    "max": float(series.max()),
                    "mean": float(series.mean()),
                    "medain": float(series.median()),
                    "sum": float(series.sum())
                }
            elif pd.api.types.is_datetime64_any_dtype(series):
                result["datetime"][column] = {
                    "min": str(series.min()),
                    "max": str(series.max())
                }
            else:
                result["categorical"][column] = {
                    "unique_values": int(series.nunique()),
                    "top_values": (
                        series
                        .value_counts()
                        .head(10)
                        .to_dict()
                    )
                }

        return result



# from tests import Test
# tst = Test()

# analy = Analyzer()

# dta = Data(user_id=2)
# dta.fetch().load().clean()
# dta.normalize()
# dta.validate()
# dt = dta.transform()
# # rept = analy.analyze(dt)
# # print(rept)

# # from chart_engine import Chart

# # cc = Chart()

# # chrts = cc.generate(df=dt)

# tst.sales_by_product(df=dt)

