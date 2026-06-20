from __future__ import annotations

from app.models.poisson import PoissonPredictor
from app.models.xgboost_model import XGBoostPredictor
from app.services.data_loader import loader


class PredictionEngine:
    def __init__(self) -> None:
        self.poisson = PoissonPredictor()
        self.xgboost = XGBoostPredictor()
        self._ready = False

    def train(self) -> None:
        df = loader.get_training_data(since="2018-01-01")
        wc_teams = loader.get_teams()
        df_wc = df[
            df["home_team"].isin(wc_teams) | df["away_team"].isin(wc_teams)
        ]
        train_df = df_wc if len(df_wc) > 500 else df

        self.poisson.fit(train_df)
        self.xgboost.fit(train_df)
        self._ready = True

    @property
    def ready(self) -> bool:
        return self._ready

    def predict_match(
        self, home: str, away: str, model: str = "both", neutral: bool = True
    ) -> dict:
        if not self._ready:
            self.train()

        result: dict = {"home_team": home, "away_team": away}
        if model in ("poisson", "both"):
            result["poisson"] = self.poisson.predict(home, away, neutral)
        if model in ("xgboost", "both"):
            result["xgboost"] = self.xgboost.predict(home, away, neutral)
        return result

    def predict_upcoming(self, model: str = "both") -> list[dict]:
        if not self._ready:
            self.train()

        upcoming = [
            m
            for m in loader.get_matches()
            if m["status"] == "scheduled"
        ]
        predictions = []
        for m in upcoming[:20]:
            pred = self.predict_match(
                m["home_team"], m["away_team"], model=model, neutral=True
            )
            pred["match"] = {
                "id": m["id"],
                "date": m["date"],
                "time": m["time"],
                "group": m["group"],
                "round": m["round"],
                "ground": m["ground"],
            }
            predictions.append(pred)
        return predictions


engine = PredictionEngine()
