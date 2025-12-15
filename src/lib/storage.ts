import { TripResult } from "@/lib/calc";

const TRIPS_KEY = "biatrack_trips_v1";
const SETTINGS_KEY = "biatrack_settings_v1";

export type Settings = {
  mapsApiKey?: string;
};

const safeParse = <T>(raw: string | null): T | null => {
  if (!raw) return null;
  try {
    return JSON.parse(raw) as T;
  } catch (error) {
    console.warn("No se pudo parsear localStorage", error);
    return null;
  }
};

export const loadTrips = (): TripResult[] => {
  if (typeof window === "undefined") return [];
  return safeParse<TripResult[]>(localStorage.getItem(TRIPS_KEY)) ?? [];
};

export const saveTrips = (trips: TripResult[]) => {
  if (typeof window === "undefined") return;
  localStorage.setItem(TRIPS_KEY, JSON.stringify(trips));
};

export const loadSettings = (): Settings => {
  if (typeof window === "undefined") return {};
  return safeParse<Settings>(localStorage.getItem(SETTINGS_KEY)) ?? {};
};

export const saveSettings = (settings: Settings) => {
  if (typeof window === "undefined") return;
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
};

