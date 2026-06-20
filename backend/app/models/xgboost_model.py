from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

from app.services.team_names import normalize


class XGBoostPredictor:
    """XGBoost classifier for match outcomes (H/D/A)."""

    FORM_WINDOW = 5

    def __init__(self) -> None:
        self.model: XGBClassifier | None = None
        self.team_encoder = LabelEncoder()
        self.trained = False
        self._team_elo: dict[str, float] = {}
        self._team_form: dict[str, list[int]] = {}

    def _outcome(self, hs: float, aws: float) -> int:
        if hs > aws:
            return 2  # home win
        if hs == aws:
            return 1  # draw
        return 0  # away win

    def _update_elo(
        self, home: str, away: str, hs: float, aws: float, k: float = 20.0
    ) -> None:
        rh = self._team_elo.get(home, 1500.0)
        ra = self._team_elo.get(away, 1500.0)
        exp_h = 1 / (1 + 10 ** ((ra - rh) / 400))
        if hs > aws:
            score_h = 1.0
        elif hs == aws:
            score_h = 0.5
        else:
            score_h = 0.0
        self._team_elo[home] = rh + k * (score_h - exp_h)
        self._team_elo[away] = ra + k * ((1 - score_h) - (1 - exp_h))

    def _update_form(self, team: str, goals_for: int, goals_against: int) -> None:
        pts = 3 if goals_for > goals_against else (1 if goals_for == goals_against else 0)
        form = self._team_form.setdefault(team, [])
        form.append(pts)
        if len(form) > self.FORM_WINDOW:
            form.pop(0)

    def _build_features(
        self,
        home: str,
        away: str,
        neutral: bool,
        date_ord: float,
    ) -> np.ndarray:
        home = normalize(home)
        away = normalize(away)
        rh = self._team_elo.get(home, 1500.0)
        ra = self._team_elo.get(away, 1500.0)
        hf = self._team_form.get(home, [1, 1, 1])
        af = self._team_form.get(away, [1, 1, 1])
        return np.array(
            [
                rh,
                ra,
                rh - ra,
                np.mean(hf),
                np.mean(af),
                np.mean(hf) - np.mean(af),
                0.0 if neutral else 1.0,
                date_ord,
            ],
            dtype=np.float32,
        )

    def fit(self, df: pd.DataFrame) -> None:
        df = df.sort_values("date").reset_index(drop=True)
        all_teams = sorted(set(df["home_team"]) | set(df["away_team"]))
        self.team_encoder.fit(all_teams)

        X_list: list[np.ndarray] = []
        y_list: list[int] = []

        for _, row in df.iterrows():
            h, a = row["home_team"], row["away_team"]
            hs, aws = float(row["home_score"]), float(row["away_score"])
            neutral = bool(row.get("neutral", True))
            date_ord = pd.Timestamp(row["date"]).toordinal()

            feat = self._build_features(h, a, neutral, date_ord)
            X_list.append(feat)
            y_list.append(self._outcome(hs, aws))

            self._update_elo(h, a, hs, aws)
            self._update_form(h, int(hs), int(aws))
            self._update_form(a, int(aws), int(hs))

        X = np.vstack(X_list)
        y = np.array(y_list)

        self.model = XGBClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.08,
            subsample=0.85,
            colsample_bytree=0.85,
            objective="multi:softprob",
            num_class=3,
            random_state=42,
            verbosity=0,
        )
        self.model.fit(X, y)
        self.trained = True

    def predict(self, home: str, away: str, neutral: bool = True) -> dict:
        if self.model is None:
            raise RuntimeError("Model not trained")

        date_ord = float(pd.Timestamp.now().toordinal())
        feat = self._build_features(home, away, neutral, date_ord).reshape(1, -1)
        probs = self.model.predict_proba(feat)[0]
        # classes: 0=away win, 1=draw, 2=home win
        away_win, draw, home_win = probs

        rh = self._team_elo.get(normalize(home), 1500.0)
        ra = self._team_elo.get(normalize(away), 1500.0)
        exp_h = max(0.5, 1.2 + (rh - ra) / 400)
        exp_a = max(0.5, 1.2 + (ra - rh) / 400)

        if home_win >= draw and home_win >= away_win:
            pred_h, pred_a = round(exp_h), max(0, round(exp_a * 0.7))
        elif away_win >= draw:
            pred_h, pred_a = max(0, round(exp_h * 0.7)), round(exp_a)
        else:
            pred_h, pred_a = round(exp_h * 0.8), round(exp_a * 0.8)

        return {
            "model": "xgboost",
            "home_team": normalize(home),
            "away_team": normalize(away),
            "predicted_score": f"{pred_h}-{pred_a}",
            "expected_goals_home": round(exp_h, 2),
            "expected_goals_away": round(exp_a, 2),
            "probabilities": {
                "home_win": round(float(home_win), 4),
                "draw": round(float(draw), 4),
                "away_win": round(float(away_win), 4),
            },
            "elo_home": round(rh, 1),
            "elo_away": round(ra, 1),
        }
