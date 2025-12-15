export const formatCOP = (value: number) =>
  new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(value);

export const formatNumber = (value: number, maximumFractionDigits = 2) =>
  new Intl.NumberFormat("es-CO", {
    maximumFractionDigits,
  }).format(value);

