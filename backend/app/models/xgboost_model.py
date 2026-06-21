from __future__ import annotations

from math import exp

from app.services.team_names import normalize


class XGBoostPredictor:
    """Lightweight Elo/form predictor with the same response shape as XGBoost."""

    FORM_WINDOW = 5

    def __init__(self) -> None:
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

    @staticmethod
    def _mean(values: list[int]) -> float:
        return sum(values) / len(values) if values else 1.0

    def fit(self, rows: list[dict]) -> None:
        for row in sorted(rows, key=lambda item: item["date"]):
            h, a = row["home_team"], row["away_team"]
            hs, aws = float(row["home_score"]), float(row["away_score"])
            self._update_elo(h, a, hs, aws)
            self._update_form(h, int(hs), int(aws))
            self._update_form(a, int(aws), int(hs))

        self.trained = True

    def predict(self, home: str, away: str, neutral: bool = True) -> dict:
        if not self.trained:
            raise RuntimeError("Model not trained")

        home = normalize(home)
        away = normalize(away)
        rh = self._team_elo.get(home, 1500.0)
        ra = self._team_elo.get(away, 1500.0)
        home_form = self._mean(self._team_form.get(home, [1, 1, 1]))
        away_form = self._mean(self._team_form.get(away, [1, 1, 1]))
        rating_delta = (rh - ra) + (home_form - away_form) * 35
        if not neutral:
            rating_delta += 55

        home_strength = 1 / (1 + exp(-rating_delta / 240))
        draw = max(0.18, min(0.33, 0.29 - abs(rating_delta) / 1800))
        home_win = home_strength * (1 - draw)
        away_win = (1 - home_strength) * (1 - draw)

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
            "home_team": home,
            "away_team": away,
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
