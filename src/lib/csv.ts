import { TripResult } from "@/lib/calc";

const HEADERS: (keyof TripResult)[] = [
  "createdAtISO",
  "contractorName",
  "baseLabel",
  "originCity",
  "destinationText",
  "fuelType",
  "fuelPricePerGallonCOP",
  "kmPerGallon",
  "oneWayDistanceKm",
  "roundTripDistanceKm",
  "oneWayEtaMinutes",
  "peakEtaMinutes",
  "tollCountOneWay",
  "tollCostOneWayCOP",
  "tollCountRoundTrip",
  "tollCostRoundTripCOP",
  "fuelGallonsRoundTrip",
  "fuelCostRoundTripCOP",
  "totalRoundTripCOP",
];

const escapeCsv = (value: unknown) => {
  if (value === null || value === undefined) return "";
  const str = String(value);
  if (str.includes('"') || str.includes(",") || str.includes("\n")) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
};

export function exportTripsToCSV(trips: TripResult[]): string {
  const headerRow = HEADERS.join(",");
  const dataRows = trips.map((trip) =>
    HEADERS.map((key) => escapeCsv(trip[key])).join(","),
  );
  return [headerRow, ...dataRows].join("\n");
}

