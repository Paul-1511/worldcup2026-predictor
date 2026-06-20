import type { ModelPrediction, UpcomingPrediction, ModelType } from "../types";

interface Props {
  predictions: UpcomingPrediction[];
  model: ModelType;
}

function ProbBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="prob-row">
      <span className="prob-label">{label}</span>
      <div className="prob-track">
        <div className="prob-fill" style={{ width: `${value * 100}%`, background: color }} />
      </div>
      <span className="prob-value">{(value * 100).toFixed(1)}%</span>
    </div>
  );
}

function ModelBlock({ pred }: { pred: ModelPrediction }) {
  const isPoisson = pred.model === "poisson";
  return (
    <div className={`model-block ${pred.model}`}>
      <div className="model-header">
        <span className="model-tag">{isPoisson ? "Poisson" : "XGBoost"}</span>
        <span className="predicted-score">{pred.predicted_score}</span>
      </div>
      <div className="xgoals">
        xG: {pred.expected_goals_home.toFixed(2)} – {pred.expected_goals_away.toFixed(2)}
      </div>
      <ProbBar label="Home" value={pred.probabilities.home_win} color="#22c55e" />
      <ProbBar label="Draw" value={pred.probabilities.draw} color="#eab308" />
      <ProbBar label="Away" value={pred.probabilities.away_win} color="#3b82f6" />
      {pred.top_scores && pred.top_scores.length > 0 && (
        <div className="top-scores">
          Top: {pred.top_scores.slice(0, 3).map((s) => `${s.home}-${s.away}`).join(", ")}
        </div>
      )}
      {pred.elo_home != null && (
        <div className="elo">ELO {pred.elo_home} vs {pred.elo_away}</div>
      )}
    </div>
  );
}

export function PredictionsPanel({ predictions, model }: Props) {
  if (predictions.length === 0) {
    return <p className="empty">No upcoming matches to predict.</p>;
  }

  return (
    <div className="predictions-list">
      {predictions.map((p) => (
        <article key={p.match.id} className="prediction-card">
          <header>
            <div className="teams">
              <strong>{p.home_team}</strong>
              <span>vs</span>
              <strong>{p.away_team}</strong>
            </div>
            <div className="pred-meta">
              {p.match.group && <span className="badge">{p.match.group}</span>}
              <span>{p.match.date}</span>
              <span>{p.match.ground}</span>
            </div>
          </header>
          <div className="models-row">
            {(model === "both" || model === "poisson") && p.poisson && (
              <ModelBlock pred={p.poisson} />
            )}
            {(model === "both" || model === "xgboost") && p.xgboost && (
              <ModelBlock pred={p.xgboost} />
            )}
          </div>
        </article>
      ))}
    </div>
  );
}
