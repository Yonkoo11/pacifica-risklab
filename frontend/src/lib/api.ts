const API_BASE = 'http://localhost:8000';

export interface Market {
  symbol: string;
  max_leverage: number;
  mark: number;
  oracle: number;
  open_interest: number;
  volume_24h: number;
  funding: number;
  next_funding: number;
}

export interface Scenario {
  id: string;
  name: string;
  description: string;
  severity: string;
  cached: boolean;
}

export interface SimulationRequest {
  symbol: string;
  scenario: string;
  oi_override?: number;
  leverage_override?: number;
  long_ratio?: number;
  num_positions?: number;
}

export interface CascadeStep {
  time_step: number;
  round: number;
  price_before: number;
  price_after: number;
  liquidated_count: number;
  liquidated_volume_usd: number;
  remaining_positions: number;
  remaining_oi_usd: number;
}

export interface FundingStressPoint {
  time_step: number;
  round: number;
  long_oi: number;
  short_oi: number;
  imbalance: number;
  funding_rate: number;
  at_cap: boolean;
}

export interface SimulationResult {
  summary: {
    total_liquidated: number;
    total_liquidated_volume_usd: number;
    total_positions: number;
    cascade_rounds: number;
    max_drawdown_pct: number;
    price_start: number;
    price_end: number;
    survival_score: number;
    oi_wipe_pct: number;
  };
  cascade_data: CascadeStep[];
  funding_stress: FundingStressPoint[];
  parameters: Record<string, unknown>;
}

export async function fetchMarkets(): Promise<Market[]> {
  const res = await fetch(`${API_BASE}/api/markets`);
  if (!res.ok) throw new Error('Failed to fetch markets');
  return res.json();
}

export async function fetchScenarios(): Promise<Scenario[]> {
  const res = await fetch(`${API_BASE}/api/scenarios`);
  if (!res.ok) throw new Error('Failed to fetch scenarios');
  return res.json();
}

export async function runSimulation(req: SimulationRequest): Promise<SimulationResult> {
  const res = await fetch(`${API_BASE}/api/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Simulation failed');
  }
  return res.json();
}
