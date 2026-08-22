import pandas as pd


class Chart():

    def generate(self, df):
        charts = []
        numeric_columns = df.select_dtypes(
            include="number"
        ).columns.tolist()

        categorical_columns = df.select_dtypes(
            include = ["object", "category"]
        ).columns.tolist()

        datetime_columns = df.select_dtypes(
            include = "datetime"
        ).columns.tolist()

        # categorical + numeric = Bar chart

        for category in categorical_columns:
            if df[category].nunique() > 30:
                continue
            for numeric in numeric_columns:
                grouped = (
                    df.groupby(category, dropna=False)[numeric]
                    .sum()
                    .reset_index()
                )
                grouped = grouped.sort_values(
                    numeric,
                    ascending = False
                ).head(20)

                data = []

                for  _, row in grouped.iterrows():
                    value = row[numeric]

                    if pd.isna(value):
                        value = 0
                    data.append({
                        category: str(row[category]),
                        numeric: float(value)
                    })
                charts.append({
                    "id": f"{numeric}_by_{category}",
                    "type": "bar",
                    "title": f"{numeric.replace('_', ' ').title()} by "
                             f"{category.replace('_', ' ').title()}",
                    "xKey": category,
                    "series": [
                        {
                            "dataKey": numeric,
                            "label": numeric.replace('_', ' ').title()
                        }
                    ],
                    "data": data
                })
        # date time + numeric = linechart

        for date_column in datetime_columns:
            for numeric in numeric_columns:
                grouped = (
                    df.dropna(
                        subset = [date_column, numeric]
                    )
                    .groupby(date_column)[numeric]
                    .sum()
                    .reset_index()
                    .sort_values(date_column)
                )

                data = []

                for _, row in grouped.iterrows():
                    value = row[numeric]

                    if pd.isna(value):
                        value = 0
                    data.append({
                        date_column: row[date_column].isoformat(),
                        numeric: float(value)
                    })

                charts.append({
                    "id": f"{numeric}_over_{date_column}",
                    "type": "line",
                    "title": f"{numeric.replace('_', " ").title()} over time",
                    "xKey": date_column,
                    "series": [
                        {
                            "dataKey": numeric,
                            "label": numeric.replace("_", " ").title()
                        }
                    ],
                    "data": data
                })

        # numeric + numeric = scatter chart

        for i, x_column in enumerate(numeric_columns):
            for y_column in numeric_columns[i + 1:]:
                subset = df[
                    [x_column, y_column]
                ].dropna()

                data = []

                for _, row in subset.iterrows():
                    data.append({
                        "x": float(row[x_column]),
                        "y": float(row[y_column])
                    })

                charts.append({
                    "id": f"{x_column}_vs_{y_column}",
                    "type": "scatter",
                    "title": (
                        f"{x_column.replace('_', ' ').title()} vs "
                        f"{y_column.replace('_', ' ').title()}"
                    ),
                    "xKey": x_column,
                    "yKey": y_column,
                    "data": data
                })

        return charts