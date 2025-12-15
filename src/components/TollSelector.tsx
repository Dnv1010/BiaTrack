'use client';

import { Toll } from "@/data/tolls";
import { formatCOP } from "@/lib/format";
import { useMemo, useState } from "react";

type TollSelectorProps = {
  tolls: Toll[];
  selectedIds: string[];
  onChange: (ids: string[]) => void;
};

const statusStyles: Record<Toll["status"], string> = {
  ACTIVE: "bg-green-100 text-green-700 border border-green-200",
  REMOVED: "bg-red-100 text-red-700 border border-red-200",
  SUSPENDED: "bg-amber-100 text-amber-800 border border-amber-200",
};

export default function TollSelector({
  tolls,
  selectedIds,
  onChange,
}: TollSelectorProps) {
  const [search, setSearch] = useState("");
  const [department, setDepartment] = useState("");

  const departments = useMemo(
    () => Array.from(new Set(tolls.map((toll) => toll.department))).sort(),
    [tolls],
  );

  const filtered = useMemo(
    () =>
      tolls.filter((toll) => {
        const matchesDept = department ? toll.department === department : true;
        const matchesSearch = toll.name.toLowerCase().includes(search.toLowerCase());
        return matchesDept && matchesSearch;
      }),
    [tolls, department, search],
  );

  const toggle = (id: string) => {
    if (selectedIds.includes(id)) {
      onChange(selectedIds.filter((value) => value !== id));
    } else {
      onChange([...selectedIds, id]);
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div className="flex flex-1 gap-3">
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Buscar peaje por nombre"
            className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm shadow-sm outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
          />
          <select
            value={department}
            onChange={(event) => setDepartment(event.target.value)}
            className="w-48 rounded-md border border-slate-200 px-3 py-2 text-sm shadow-sm outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
          >
            <option value="">Todos los departamentos</option>
            {departments.map((dept) => (
              <option key={dept} value={dept}>
                {dept}
              </option>
            ))}
          </select>
        </div>
        <span className="text-xs text-slate-500">
          Peajes con estado desmontado/suspendido muestran tarifa $0.
        </span>
      </div>

      <div className="overflow-hidden rounded-lg border border-slate-200 shadow-sm">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">
            <tr>
              <th className="px-4 py-3">Seleccionar</th>
              <th className="px-4 py-3">Nombre</th>
              <th className="px-4 py-3">Departamento</th>
              <th className="px-4 py-3">Tarifa (COP)</th>
              <th className="px-4 py-3">Estado</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 bg-white">
            {filtered.length === 0 ? (
              <tr>
                <td className="px-4 py-4 text-center text-slate-500" colSpan={5}>
                  No hay peajes que coincidan con el filtro.
                </td>
              </tr>
            ) : (
              filtered.map((toll) => (
                <tr key={toll.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3">
                    <input
                      type="checkbox"
                      className="h-4 w-4 accent-sky-600"
                      checked={selectedIds.includes(toll.id)}
                      onChange={() => toggle(toll.id)}
                    />
                  </td>
                  <td className="px-4 py-3">
                    <div className="font-medium text-slate-800">{toll.name}</div>
                    <div className="text-xs text-slate-500">{toll.operator ?? ""}</div>
                  </td>
                  <td className="px-4 py-3 text-slate-700">{toll.department}</td>
                  <td className="px-4 py-3 font-medium text-slate-800">
                    {formatCOP(toll.fareCOP)}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`rounded-full px-2 py-1 text-xs font-semibold ${statusStyles[toll.status]}`}
                    >
                      {toll.status}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

