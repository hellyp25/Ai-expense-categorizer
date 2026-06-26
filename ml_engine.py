import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from prophet import Prophet
import warnings

warnings.filterwarnings("ignore")


class MLEngine:

    @staticmethod
    def detect_anomalies(
        df: pd.DataFrame,
        contamination: float = 0.05
    ) -> pd.DataFrame:

        df = df.copy()

        if len(df) < 5:

            df["Is_Anomaly"] = False
            df["Anomaly_Score"] = 0.0

            return df

        X = np.log1p(np.abs(df[["Amount"]]))

        model = IsolationForest(
            contamination=contamination,
            random_state=42
        )

        prediction = model.fit_predict(X)

        df["Is_Anomaly"] = prediction == -1

        df["Anomaly_Score"] = (
            -model.score_samples(X)
        ).round(4)

        return df

    @staticmethod
    def forecast_expenses(
        df: pd.DataFrame,
        periods: int = 30
    ):

        if len(df) < 10:
            return pd.DataFrame(), 0.0

        daily = (
            df.groupby("Date")["Amount"]
            .sum()
            .reset_index()
        )

        daily.columns = ["ds", "y"]

        daily["ds"] = pd.to_datetime(daily["ds"])

        daily = daily.sort_values("ds")

        daily = daily.dropna()

        if len(daily) < 10:
            return pd.DataFrame(), 0.0

        model = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=True,
            daily_seasonality=False
        )

        model.fit(daily)

        future = model.make_future_dataframe(
            periods=periods
        )

        forecast = model.predict(future)

        next_month_prediction = (
            forecast.tail(periods)["yhat"]
            .clip(lower=0)
            .sum()
        )

        return forecast, round(float(next_month_prediction), 2)