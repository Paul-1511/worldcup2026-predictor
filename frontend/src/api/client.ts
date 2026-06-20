import type { Scoreboard, UpcomingPrediction, ModelType } from "../types";

const API = "/api";

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export function getScoreboard(): Promise<Scoreboard> {
  return fetchJson(`${API}/scoreboard`);
}

export function getUpcomingPredictions(model: ModelType): Promise<{
  count: number;
  predictions: UpcomingPrediction[];
}> {
  return fetchJson(`${API}/predictions/upcoming?model=${model}&limit=24`);
}

export function refreshData(): Promise<{ status: string }> {
  return fetch(`${API}/refresh`, { method: "POST" }).then((r) => r.json());
}
