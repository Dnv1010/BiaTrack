'use client';

import { TripResult } from "@/lib/calc";
import { formatCOP, formatNumber } from "@/lib/format";

type TripDetailsProps = {
  trip: TripResult;
  onClose: () => void;
};

export default function TripDetails({ trip, onClose }: TripDetailsProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/50 p-4 backdrop-blur-sm">
      <div className="w-full max-w-3xl rounded-xl bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-500">Detalle</p>
            <h2 className="text-xl font-semibold text-slate-900">Cálculo guardado</h2>
            <p className="text-xs text-slate-500">
              {typeof window !== "undefined"
                ? new Date(trip.createdAtISO).toLocaleString("es-CO")
                : trip.createdAtISO}
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded-md border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
          >
            Cerrar
          </button>
        </div>

        <div className="grid gap-4 border-b border-slate-100 px-6 py-4 md:grid-cols-2">
          <DetailLine label="Contratista" value={trip.contractorName} />
          <DetailLine label="Base / Unidad" value={trip.baseLabel} />
          <DetailLine label="Origen (ciudad)" value={trip.originCity} />
          <DetailLine label="Destino" value={trip.destinationText} />
        </div>

        <div className="grid gap-6 px-6 py-4 md:grid-cols-2">
          <DetailCard
            title="Ruta y tiempos"
            items={[
              ["Distancia ida", `${formatNumber(trip.oneWayDistanceKm, 2)} km`],
              ["Distancia total", `${formatNumber(trip.roundTripDistanceKm, 2)} km`],
              ["ETA ida", `${formatNumber(trip.oneWayEtaMinutes, 1)} min`],
              ["ETA hora pico", `${formatNumber(trip.peakEtaMinutes, 0)} min`],
            ]}
          />
          <DetailCard
            title="Combustible"
            items={[
              ["Tipo", trip.fuelType],
              ["Precio galón", formatCOP(trip.fuelPricePerGallonCOP)],
              ["Rendimiento", `${formatNumber(trip.kmPerGallon, 2)} km/gal`],
              ["Galones ida", formatNumber(trip.fuelGallonsOneWay, 3)],
              ["Galones totales", formatNumber(trip.fuelGallonsRoundTrip, 3)],
              ["Costo total combustible", formatCOP(trip.fuelCostRoundTripCOP)],
            ]}
          />
          <DetailCard
            title="Peajes"
            items={[
              ["Peajes ida", `${trip.tollCountOneWay}`],
              ["Costo peajes ida", formatCOP(trip.tollCostOneWayCOP)],
              ["Peajes totales", `${trip.tollCountRoundTrip}`],
              ["Costo peajes totales", formatCOP(trip.tollCostRoundTripCOP)],
            ]}
          />
          <DetailCard
            title="Total"
            items={[
              ["Total ida y regreso", formatCOP(trip.totalRoundTripCOP)],
              ["ID interno", trip.id],
            ]}
          />
        </div>
      </div>
    </div>
  );
}

function DetailLine({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="text-base font-semibold text-slate-900">{value}</p>
    </div>
  );
}

function DetailCard({ title, items }: { title: string; items: [string, string][] }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3">
      <h3 className="text-sm font-semibold text-slate-800">{title}</h3>
      <div className="mt-2 space-y-1 text-sm text-slate-700">
        {items.map(([label, value]) => (
          <div key={label} className="flex justify-between gap-4">
            <span className="text-slate-500">{label}</span>
            <span className="font-medium">{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

