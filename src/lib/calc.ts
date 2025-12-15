import { Contractor } from "@/data/contractors";
import { Toll } from "@/data/tolls";

export type FuelType = "GASOLINA" | "ACPM";

export type TripInput = {
  contractorId: string;
  baseId: string;
  originCity: string;
  destinationText: string;
  fuelType: FuelType;
  fuelPricePerGallonCOP: number;
  kmPerGallon: number;
  oneWayDistanceKm: number;
  oneWayEtaMinutes: number;
  selectedTollIds: string[];
};

export type TripResult = {
  id: string;
  createdAtISO: string;

  contractorName: string;
  baseLabel: string;

  originCity: string;
  destinationText: string;

  fuelType: FuelType;
  fuelPricePerGallonCOP: number;
  kmPerGallon: number;

  oneWayDistanceKm: number;
  roundTripDistanceKm: number;

  oneWayEtaMinutes: number;
  peakEtaMinutes: number;

  tollCountOneWay: number;
  tollCostOneWayCOP: number;
  tollCountRoundTrip: number;
  tollCostRoundTripCOP: number;

  fuelGallonsOneWay: number;
  fuelGallonsRoundTrip: number;
  fuelCostRoundTripCOP: number;

  totalRoundTripCOP: number;
};

const uuid = () =>
  typeof crypto !== "undefined" && typeof crypto.randomUUID === "function"
    ? crypto.randomUUID()
    : `trip_${Date.now().toString(36)}_${Math.random().toString(16).slice(2)}`;

export function computeTripResult(
  input: TripInput,
  contractors: Contractor[],
  tolls: Toll[],
): TripResult {
  const contractor = contractors.find((c) => c.id === input.contractorId);
  const base = contractor?.bases.find((b) => b.id === input.baseId);

  const selectedTolls = tolls.filter((t) => input.selectedTollIds.includes(t.id));
  const tollCostOneWayCOP = Math.round(
    selectedTolls.reduce((acc, toll) => acc + (toll.fareCOP || 0), 0),
  );
  const tollCountOneWay = selectedTolls.length;
  const tollCostRoundTripCOP = tollCostOneWayCOP * 2;
  const tollCountRoundTrip = tollCountOneWay * 2;

  const roundTripDistanceKm = input.oneWayDistanceKm * 2;
  const peakEtaMinutes = Math.round(input.oneWayEtaMinutes * 3.5);

  const fuelGallonsOneWay = input.oneWayDistanceKm / input.kmPerGallon;
  const fuelGallonsRoundTrip = fuelGallonsOneWay * 2;
  const fuelCostRoundTripCOP = Math.round(
    fuelGallonsRoundTrip * input.fuelPricePerGallonCOP,
  );

  const totalRoundTripCOP = fuelCostRoundTripCOP + tollCostRoundTripCOP;

  return {
    id: uuid(),
    createdAtISO: new Date().toISOString(),
    contractorName: contractor?.name ?? "Contratista",
    baseLabel: base?.label ?? "Base",
    originCity: input.originCity,
    destinationText: input.destinationText,
    fuelType: input.fuelType,
    fuelPricePerGallonCOP: input.fuelPricePerGallonCOP,
    kmPerGallon: input.kmPerGallon,
    oneWayDistanceKm: input.oneWayDistanceKm,
    roundTripDistanceKm,
    oneWayEtaMinutes: input.oneWayEtaMinutes,
    peakEtaMinutes,
    tollCountOneWay,
    tollCostOneWayCOP,
    tollCountRoundTrip,
    tollCostRoundTripCOP,
    fuelGallonsOneWay,
    fuelGallonsRoundTrip,
    fuelCostRoundTripCOP,
    totalRoundTripCOP,
  };
}

