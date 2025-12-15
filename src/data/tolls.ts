export type Toll = {
  id: string;
  name: string;
  department: string;
  operator?: string;
  fareCOP: number; // 0 si desmontado/suspendido
  status: "ACTIVE" | "REMOVED" | "SUSPENDED";
};

// Nota: el cliente indicó cargar primero los peajes de Tolima y Valle del Cauca.
// No se incluyeron los datos concretos en la solicitud, así que el arreglo queda
// listo para ser completado con la información oficial sin tocar la lógica.
export const TOLLS: Toll[] = [];

