'use client';

import TollSelector from "@/components/TollSelector";
import TripDetails from "@/components/TripDetails";
import { CONTRACTORS } from "@/data/contractors";
import { TOLLS } from "@/data/tolls";
import { computeTripResult, FuelType, TripResult } from "@/lib/calc";
import { exportTripsToCSV } from "@/lib/csv";
import { formatCOP, formatNumber } from "@/lib/format";
import { loadTrips, saveTrips } from "@/lib/storage";
import { DEFAULT_KM_PER_GALLON_VALUE } from "@/lib/maps";
import { useEffect, useMemo, useState } from "react";

type FormState = {
  contractorId: string;
  baseId: string;
  destinationText: string;
  fuelType: FuelType;
  fuelPricePerGallonCOP: string;
  kmPerGallon: string;
  oneWayDistanceKm: string;
  oneWayEtaMinutes: string;
  selectedTollIds: string[];
};

const defaultContractor = CONTRACTORS.length > 0 ? CONTRACTORS[0] : null;
const defaultBase = defaultContractor?.bases?.[0] ?? null;

export default function Home() {
  const [form, setForm] = useState<FormState>(() => ({
    contractorId: defaultContractor?.id ?? "",
    baseId: defaultBase?.id ?? "",
    destinationText: "",
    fuelType: "GASOLINA",
    fuelPricePerGallonCOP: "",
    kmPerGallon: String(DEFAULT_KM_PER_GALLON_VALUE),
    oneWayDistanceKm: "",
    oneWayEtaMinutes: "",
    selectedTollIds: [],
  }));
  const [errors, setErrors] = useState<string[]>([]);
  const [trips, setTrips] = useState<TripResult[]>([]);
  const [selectedTrip, setSelectedTrip] = useState<TripResult | null>(null);
  const [showForm, setShowForm] = useState(true);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setTrips(loadTrips());
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (hydrated) saveTrips(trips);
  }, [trips, hydrated]);

  useEffect(() => {
    const contractor = CONTRACTORS.find((c) => c.id === form.contractorId);
    if (!contractor) return;
    const baseExists = contractor.bases.some((b) => b.id === form.baseId);
    if (!baseExists) {
      setForm((prev) => ({
        ...prev,
        baseId: contractor.bases[0]?.id ?? "",
      }));
    }
  }, [form.contractorId, form.baseId]);

  const selectedContractor = CONTRACTORS.find((c) => c.id === form.contractorId);
  const selectedBase = selectedContractor?.bases.find((b) => b.id === form.baseId);
  const originCity = selectedBase?.city ?? "";

  const selectedTolls = useMemo(
    () => TOLLS.filter((t) => form.selectedTollIds.includes(t.id)),
    [form.selectedTollIds],
  );

  const tollCostOneWayCOP = useMemo(
    () => Math.round(selectedTolls.reduce((acc, toll) => acc + (toll.fareCOP || 0), 0)),
    [selectedTolls],
  );

  const tollCountOneWay = selectedTolls.length;

  const livePreview = useMemo(() => {
    const fuelPrice = Number(form.fuelPricePerGallonCOP);
    const kmPerGallon = Number(form.kmPerGallon);
    const distance = Number(form.oneWayDistanceKm);
    const eta = Number(form.oneWayEtaMinutes);
    if (
      !originCity ||
      !form.destinationText.trim() ||
      [fuelPrice, kmPerGallon, distance, eta].some((v) => !v || v <= 0)
    ) {
      return null;
    }
    return computeTripResult(
      {
        contractorId: form.contractorId,
        baseId: form.baseId,
        originCity,
        destinationText: form.destinationText.trim(),
        fuelType: form.fuelType,
        fuelPricePerGallonCOP: fuelPrice,
        kmPerGallon,
        oneWayDistanceKm: distance,
        oneWayEtaMinutes: eta,
        selectedTollIds: form.selectedTollIds,
      },
      CONTRACTORS,
      TOLLS,
    );
  }, [form, originCity]);

  const handleInputChange = <K extends keyof FormState>(field: K, value: FormState[K]) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    const newErrors: string[] = [];
    const fuelPrice = Number(form.fuelPricePerGallonCOP);
    const kmPerGallon = Number(form.kmPerGallon);
    const distance = Number(form.oneWayDistanceKm);
    const eta = Number(form.oneWayEtaMinutes);

    if (!form.contractorId) newErrors.push("Selecciona el contratista.");
    if (!form.baseId) newErrors.push("Selecciona la base/unidad.");
    if (!originCity) newErrors.push("El origen no está disponible para la base seleccionada.");
    if (!form.destinationText.trim()) newErrors.push("Ingresa el destino.");
    if (!fuelPrice || fuelPrice <= 0) newErrors.push("Precio por galón inválido.");
    if (!kmPerGallon || kmPerGallon <= 0) newErrors.push("Rendimiento km/galón inválido.");
    if (!distance || distance <= 0) newErrors.push("Distancia ida inválida. Ingresa el valor desde Google Maps/Waze.");
    if (!eta || eta <= 0) newErrors.push("Tiempo ida inválido. Ingresa el valor desde Google Maps/Waze.");

    if (newErrors.length > 0) {
      setErrors(newErrors);
      return;
    }

    const result = computeTripResult(
      {
        contractorId: form.contractorId,
        baseId: form.baseId,
        originCity,
        destinationText: form.destinationText.trim(),
        fuelType: form.fuelType,
        fuelPricePerGallonCOP: fuelPrice,
        kmPerGallon,
        oneWayDistanceKm: distance,
        oneWayEtaMinutes: eta,
        selectedTollIds: form.selectedTollIds,
      },
      CONTRACTORS,
      TOLLS,
    );

    setTrips((prev) => [result, ...prev]);
    setErrors([]);
    setForm((prev) => ({
      ...prev,
      destinationText: "",
      fuelPricePerGallonCOP: "",
      oneWayDistanceKm: "",
      oneWayEtaMinutes: "",
      selectedTollIds: [],
    }));
    setShowForm(false);
  };

  const handleDeleteTrip = (id: string) => {
    const filtered = trips.filter((trip) => trip.id !== id);
    setTrips(filtered);
  };

  const handleDownloadCsv = () => {
    const csv = exportTripsToCSV(trips);
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "biatrack_trips.csv");
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  };


  return (
    <div className="min-h-screen bg-slate-50 pb-12">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-6 py-5 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-500">BiaTrack</p>
            <h1 className="text-2xl font-semibold text-slate-900">
              Calculadora de traslados (Categoría I, Colombia)
          </h1>
            <p className="text-sm text-slate-600">
              Sin login, datos en localStorage. Distancia/tiempo ingresados manualmente.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setShowForm((prev) => !prev)}
              className="rounded-md bg-sky-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-sky-700"
            >
              {showForm ? "Ocultar formulario" : "Nuevo cálculo"}
            </button>
            <button
              onClick={handleDownloadCsv}
              disabled={trips.length === 0}
              className="rounded-md border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Descargar CSV (registros actuales)
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto mt-6 flex max-w-7xl flex-col gap-6 px-6">
        {showForm && (
          <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-200 px-6 py-4">
              <h2 className="text-lg font-semibold text-slate-900">Nuevo cálculo</h2>
              <p className="text-sm text-slate-600">
                Ingresar distancia y tiempo desde Google Maps/Waze, seleccionar peajes manualmente.
              </p>
            </div>
            <form className="space-y-6 px-6 py-5" onSubmit={handleSubmit}>
              {errors.length > 0 && (
                <div className="rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
                  <p className="font-semibold">Revisa los campos:</p>
                  <ul className="list-disc pl-5">
                    {errors.map((err) => (
                      <li key={err}>{err}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-800">Contratista</label>
                  <select
                    value={form.contractorId}
                    onChange={(e) => handleInputChange("contractorId", e.target.value)}
                    className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm shadow-sm outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                    required
                  >
                    <option value="">Selecciona</option>
                    {CONTRACTORS.map((contractor) => (
                      <option key={contractor.id} value={contractor.id}>
                        {contractor.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-800">Base / Unidad</label>
                  <select
                    value={form.baseId}
                    onChange={(e) => handleInputChange("baseId", e.target.value)}
                    className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm shadow-sm outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                    required
                  >
                    <option value="">Selecciona</option>
                    {selectedContractor?.bases.map((base) => (
                      <option key={base.id} value={base.id}>
                        {base.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-800">Origen (ciudad)</label>
                  <input
                    type="text"
                    value={originCity}
                    readOnly
                    className="w-full rounded-md border border-slate-200 bg-slate-100 px-3 py-2 text-sm text-slate-700 shadow-inner"
                    placeholder="Ciudad de origen"
                  />
                </div>
                <div className="md:col-span-2 space-y-2">
                  <label className="text-sm font-medium text-slate-800">Destino</label>
                  <input
                    type="text"
                    value={form.destinationText}
                    onChange={(e) => handleInputChange("destinationText", e.target.value)}
                    className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm shadow-sm outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                    placeholder="Ciudad, punto de interés o dirección"
                    required
                  />
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-800">Tipo de combustible</label>
                  <select
                    value={form.fuelType}
                    onChange={(e) => handleInputChange("fuelType", e.target.value as FuelType)}
                    className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm shadow-sm outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                  >
                    <option value="GASOLINA">Gasolina</option>
                    <option value="ACPM">ACPM</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-800">
                    Precio por galón (COP)
                  </label>
                  <input
                    type="number"
                    min="0"
                    inputMode="decimal"
                    value={form.fuelPricePerGallonCOP}
                    onChange={(e) => handleInputChange("fuelPricePerGallonCOP", e.target.value)}
                    className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm shadow-sm outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-800">Rendimiento (km/gal)</label>
                  <input
                    type="number"
                    min="0"
                    inputMode="decimal"
                    value={form.kmPerGallon}
                    onChange={(e) => handleInputChange("kmPerGallon", e.target.value)}
                    className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm shadow-sm outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                    required
                  />
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-800">Distancia ida (km)</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    inputMode="decimal"
                    value={form.oneWayDistanceKm}
                    onChange={(e) => handleInputChange("oneWayDistanceKm", e.target.value)}
                    className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm shadow-sm outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                    placeholder="Ej: 245.5"
                    required
                  />
                  <div className="flex items-start gap-2 rounded-md border border-blue-200 bg-blue-50 px-3 py-2">
                    <div className="mt-0.5">
                      <svg className="h-4 w-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" suppressHydrationWarning>
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <p className="text-xs text-blue-800">
                      <strong>Consulta en Google Maps o Waze:</strong> Abre{" "}
                      <a href="https://maps.google.com" target="_blank" rel="noopener noreferrer" className="underline font-semibold">Google Maps</a>{" "}
                      o <a href="https://www.waze.com" target="_blank" rel="noopener noreferrer" className="underline font-semibold">Waze</a>, busca la ruta desde <strong>{originCity || "origen"}</strong> hasta tu destino, y copia la distancia en kilómetros (ruta por carretera, no distancia lineal).
                    </p>
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-800">Tiempo ida (min)</label>
                  <input
                    type="number"
                    min="0"
                    step="1"
                    inputMode="numeric"
                    value={form.oneWayEtaMinutes}
                    onChange={(e) => handleInputChange("oneWayEtaMinutes", e.target.value)}
                    className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm shadow-sm outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                    placeholder="Ej: 180"
                    required
                  />
                  <div className="flex items-start gap-2 rounded-md border border-blue-200 bg-blue-50 px-3 py-2">
                    <div className="mt-0.5">
                      <svg className="h-4 w-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" suppressHydrationWarning>
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <p className="text-xs text-blue-800">
                      <strong>Tiempo estimado:</strong> Usa el tiempo que muestra Google Maps/Waze en condiciones normales (no hora pico). Convierte horas:minutos a minutos totales si es necesario.
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold text-slate-900">Peajes (selección asistida)</p>
                    <p className="text-xs text-slate-600">
                      No se detectan automáticamente. Selecciona solo los que apliquen en la ida.
                    </p>
                  </div>
                  <div className="text-right text-sm text-slate-700">
                    <p>
                      Peajes ida: <strong>{tollCountOneWay}</strong> / {formatCOP(tollCostOneWayCOP)}
                    </p>
                    <p>
                      Ida + regreso: <strong>{tollCountOneWay * 2}</strong> /{" "}
                      {formatCOP(tollCostOneWayCOP * 2)}
                    </p>
                  </div>
                </div>
                <TollSelector
                  tolls={TOLLS}
                  selectedIds={form.selectedTollIds}
                  onChange={(ids) => handleInputChange("selectedTollIds", ids)}
                />
              </div>

              <div className="grid gap-4 md:grid-cols-[2fr_1fr]">
                <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3">
                  <p className="text-sm font-semibold text-slate-800">Resumen en vivo</p>
                  {livePreview ? (
                    <div className="mt-2 grid gap-2 text-sm text-slate-700 sm:grid-cols-2">
                      <SummaryLine label="Distancia total" value={`${formatNumber(livePreview.roundTripDistanceKm, 2)} km`} />
                      <SummaryLine label="ETA hora pico" value={`${formatNumber(livePreview.peakEtaMinutes, 0)} min`} />
                      <SummaryLine
                        label="Combustible total"
                        value={`${formatNumber(livePreview.fuelGallonsRoundTrip, 3)} gal (${formatCOP(livePreview.fuelCostRoundTripCOP)})`}
                      />
                      <SummaryLine
                        label="Peajes totales"
                        value={`${livePreview.tollCountRoundTrip} / ${formatCOP(livePreview.tollCostRoundTripCOP)}`}
                      />
                      <SummaryLine
                        label="Total ida y regreso"
                        value={formatCOP(livePreview.totalRoundTripCOP)}
                      />
                    </div>
                  ) : (
                    <p className="mt-2 text-sm text-slate-500">
                      Completa los campos numéricos para ver el cálculo en vivo.
                    </p>
                  )}
                </div>
                <div className="flex items-end justify-end">
                  <button
                    type="submit"
                    className="w-full rounded-md bg-emerald-600 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-700"
                  >
                    Guardar cálculo
                  </button>
                </div>
              </div>
            </form>
          </section>
        )}

        <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 px-6 py-4">
            <h2 className="text-lg font-semibold text-slate-900">Dashboard de cálculos</h2>
            <p className="text-sm text-slate-600">
              Registros almacenados en localStorage. Puedes eliminarlos o exportar CSV.
            </p>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">
                <tr>
                  <th className="px-4 py-3">Fecha</th>
                  <th className="px-4 py-3">Contratista</th>
                  <th className="px-4 py-3">Base</th>
                  <th className="px-4 py-3">Origen</th>
                  <th className="px-4 py-3">Destino</th>
                  <th className="px-4 py-3">Total COP</th>
                  <th className="px-4 py-3">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 bg-white">
                {trips.length === 0 ? (
                  <tr>
                    <td className="px-4 py-5 text-center text-slate-500" colSpan={7}>
                      No hay cálculos guardados todavía.
                    </td>
                  </tr>
                ) : (
                  trips.map((trip) => (
                    <tr key={trip.id} className="hover:bg-slate-50">
                      <td className="px-4 py-3 text-slate-700">
                        {hydrated
                          ? new Date(trip.createdAtISO).toLocaleString("es-CO")
                          : trip.createdAtISO}
                      </td>
                      <td className="px-4 py-3 font-medium text-slate-900">
                        {trip.contractorName}
                      </td>
                      <td className="px-4 py-3 text-slate-700">{trip.baseLabel}</td>
                      <td className="px-4 py-3 text-slate-700">{trip.originCity}</td>
                      <td className="px-4 py-3 text-slate-700">{trip.destinationText}</td>
                      <td className="px-4 py-3 font-semibold text-slate-900">
                        {formatCOP(trip.totalRoundTripCOP)}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2">
                          <button
                            onClick={() => setSelectedTrip(trip)}
                            className="rounded-md border border-slate-200 px-3 py-1 text-xs font-semibold text-slate-700 transition hover:bg-slate-50"
                          >
                            Ver
                          </button>
                          <button
                            onClick={() => handleDeleteTrip(trip.id)}
                            className="rounded-md border border-rose-200 bg-rose-50 px-3 py-1 text-xs font-semibold text-rose-700 transition hover:bg-rose-100"
                          >
                            Eliminar
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 px-6 py-4">
            <h2 className="text-lg font-semibold text-slate-900">Instrucciones</h2>
            <p className="text-sm text-slate-600">
              Consulta Google Maps o Waze para obtener distancia y tiempo reales por carretera.
            </p>
          </div>
          <div className="px-6 py-5 space-y-4">
            <div className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3">
              <p className="text-sm font-semibold text-amber-900 mb-2">
                📍 Cómo obtener distancia y tiempo:
              </p>
              <ol className="list-decimal list-inside space-y-2 text-xs text-amber-800">
                <li>Abre <a href="https://maps.google.com" target="_blank" rel="noopener noreferrer" className="underline font-semibold">Google Maps</a> o <a href="https://www.waze.com" target="_blank" rel="noopener noreferrer" className="underline font-semibold">Waze</a> en otra pestaña</li>
                <li>Ingresa el origen (ciudad de la base seleccionada) y el destino</li>
                <li>Selecciona la ruta por carretera (no distancia lineal)</li>
                <li>Copia la <strong>distancia en kilómetros</strong> y el <strong>tiempo estimado en minutos</strong></li>
                <li>Pega los valores en los campos correspondientes del formulario</li>
              </ol>
            </div>
            <div className="rounded-md border border-green-200 bg-green-50 px-4 py-3">
              <p className="text-sm font-semibold text-green-900 mb-1">
                ✅ Recordatorio:
              </p>
              <p className="text-xs text-green-800">
                Usa el tiempo en condiciones normales (no hora pico). El sistema calculará automáticamente el tiempo en hora pico multiplicando por 3.5x.
              </p>
            </div>
        </div>
        </section>
      </main>

      {selectedTrip && (
        <TripDetails
          trip={selectedTrip}
          onClose={() => setSelectedTrip(null)}
        />
      )}
    </div>
  );
}

function SummaryLine({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-md bg-white px-3 py-2 shadow-sm">
      <span className="text-slate-600">{label}</span>
      <span className="font-semibold text-slate-900">{value}</span>
    </div>
  );
}
