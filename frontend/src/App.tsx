import { useCallback, useEffect, useState } from "react";
import { getScoreboard, getUpcomingPredictions, refreshData } from "./api/client";
import { MatchCard } from "./components/MatchCard";
import { PredictionsPanel } from "./components/PredictionsPanel";
import { StandingsTable } from "./components/StandingsTable";
import type { ModelType, Scoreboard, UpcomingPrediction } from "./types";

type Tab = "scoreboard" | "predictions" | "standings";

export default function App() {
  const [tab, setTab] = useState<Tab>("scoreboard");
  const [model, setModel] = useState<ModelType>("both");
  const [scoreboard, setScoreboard] = useState<Scoreboard | null>(null);
  const [predictions, setPredictions] = useState<UpcomingPrediction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const load = useCallback(async () => {
    try {
      setError(null);
      const [sb, preds] = await Promise.all([
        getScoreboard(),
        getUpcomingPredictions(model),
      ]);
      setScoreboard(sb);
      setPredictions(preds.predictions);
      setLastUpdate(new Date());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load data");
    } finally {
      setLoading(false);
    }
  }, [model]);

  useEffect(() => {
    load();
    const interval = setInterval(load, 60_000);
    return () => clearInterval(interval);
  }, [load]);

  const handleRefresh = async () => {
    setLoading(true);
    try {
      await refreshData();
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Refresh failed");
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="hero">
        <div className="hero-content">
          <div className="hero-badge">FIFA World Cup 2026</div>
          <h1>Match Predictor</h1>
          <p>
            Live scoreboard and match predictions powered by Poisson regression
            and XGBoost — trained on 49,000+ international results.
          </p>
          {scoreboard && (
            <div className="hero-stats">
              <div className="stat">
                <span className="stat-value">{scoreboard.stats.finished}</span>
                <span className="stat-label">Played</span>
              </div>
              <div className="stat">
                <span className="stat-value">{scoreboard.stats.remaining}</span>
                <span className="stat-label">Remaining</span>
              </div>
              <div className="stat">
                <span className="stat-value">{scoreboard.stats.total_matches}</span>
                <span className="stat-label">Total</span>
              </div>
            </div>
          )}
        </div>
      </header>

      <nav className="tabs">
        <button className={tab === "scoreboard" ? "active" : ""} onClick={() => setTab("scoreboard")}>
          Scoreboard
        </button>
        <button className={tab === "predictions" ? "active" : ""} onClick={() => setTab("predictions")}>
          Predictions
        </button>
        <button className={tab === "standings" ? "active" : ""} onClick={() => setTab("standings")}>
          Standings
        </button>
        <div className="nav-actions">
          {tab === "predictions" && (
            <select value={model} onChange={(e) => setModel(e.target.value as ModelType)}>
              <option value="both">Both Models</option>
              <option value="poisson">Poisson Only</option>
              <option value="xgboost">XGBoost Only</option>
            </select>
          )}
          <button className="refresh-btn" onClick={handleRefresh} disabled={loading}>
            {loading ? "Updating…" : "Refresh"}
          </button>
        </div>
      </nav>

      <main className="content">
        {error && <div className="error-banner">{error}</div>}

        {loading && !scoreboard ? (
          <div className="loading">Loading tournament data…</div>
        ) : (
          <>
            {tab === "scoreboard" && scoreboard && (
              <div className="scoreboard-layout">
                <section>
                  <h2>Recent Results</h2>
                  <div className="match-list">
                    {scoreboard.recent_results.length === 0 ? (
                      <p className="empty">No results yet.</p>
                    ) : (
                      scoreboard.recent_results.map((m) => (
                        <MatchCard key={m.id} match={m} />
                      ))
                    )}
                  </div>
                </section>
                <section>
                  <h2>Upcoming Fixtures</h2>
                  <div className="match-list">
                    {scoreboard.upcoming.map((m) => (
                      <MatchCard key={m.id} match={m} compact />
                    ))}
                  </div>
                </section>
              </div>
            )}

            {tab === "predictions" && (
              <section>
                <h2>Upcoming Match Predictions</h2>
                <p className="section-desc">
                  Predictions use historical international match data (2018–2026) from{" "}
                  <a href="https://github.com/martj42/international_results" target="_blank" rel="noreferrer">
                    martj42/international_results
                  </a>
                  . Scores update from{" "}
                  <a href="https://github.com/openfootball/worldcup.json" target="_blank" rel="noreferrer">
                    openfootball/worldcup.json
                  </a>.
                </p>
                <PredictionsPanel predictions={predictions} model={model} />
              </section>
            )}

            {tab === "standings" && scoreboard && (
              <section>
                <h2>Group Standings</h2>
                <StandingsTable standings={scoreboard.standings} />
              </section>
            )}
          </>
        )}
      </main>

      <footer className="footer">
        <span>
          Data: openfootball/worldcup.json · martj42/international_results
        </span>
        {lastUpdate && (
          <span>Last updated: {lastUpdate.toLocaleTimeString()}</span>
        )}
      </footer>
    </div>
  );
}
