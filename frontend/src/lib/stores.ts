import { writable } from 'svelte/store';
import type { Market, Scenario, SimulationResult } from './api';

export const markets = writable<Market[]>([]);
export const scenarios = writable<Scenario[]>([]);
export const selectedMarket = writable<string>('BTC');
export const selectedScenario = writable<string>('oct_2025_crash');
export const oiOverride = writable<number>(100_000_000);
export const leverageOverride = writable<number | null>(null);
export const longRatio = writable<number>(0.6);
export const isSimulating = writable<boolean>(false);
export const result = writable<SimulationResult | null>(null);
export const compareResult = writable<SimulationResult | null>(null);
export const compareMode = writable<boolean>(false);
