export interface Match {
  id: number;
  round: string;
  date: string;
  time: string;
  home_team: string;
  away_team: string;
  home_score: number | null;
  away_score: number | null;
  ht_home: number | null;
  ht_away: number | null;
  group: string | null;
  ground: string;
  status: "finished" | "scheduled";
  goals_home: Goal[];
  goals_away: Goal[];
}

export interface Goal {
  name: string;
  minute: string;
  penalty?: boolean;
  owngoal?: boolean;
}

export interface StandingRow {
  position: number;
  team: string;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  gf: number;
  ga: number;
  gd: number;
  points: number;
}

export interface ModelPrediction {
  model: string;
  home_team: string;
  away_team: string;
  predicted_score: string;
  expected_goals_home: number;
  expected_goals_away: number;
  probabilities: {
    home_win: number;
    draw: number;
    away_win: number;
  };
  top_scores?: { home: number; away: number; probability: number }[];
  elo_home?: number;
  elo_away?: number;
}

export interface UpcomingPrediction {
  home_team: string;
  away_team: string;
  poisson?: ModelPrediction;
  xgboost?: ModelPrediction;
  match: {
    id: number;
    date: string;
    time: string;
    group: string | null;
    round: string;
    ground: string;
  };
}

export interface Scoreboard {
  tournament: string;
  last_updated: string | null;
  recent_results: Match[];
  live: Match[];
  upcoming: Match[];
  standings: Record<string, StandingRow[]>;
  stats: {
    total_matches: number;
    finished: number;
    remaining: number;
  };
}

export type ModelType = "both" | "poisson" | "xgboost";
