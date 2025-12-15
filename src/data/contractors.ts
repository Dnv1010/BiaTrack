export type Contractor = {
  id: string;
  name: string;
  coverage?: string;
  bases: { id: string; label: string; city: string; department?: string }[];
};

export const CONTRACTORS: Contractor[] = [
  {
    id: "power-grid",
    name: "POWER GRID",
    bases: [{ id: "boyaca", label: "Base Boyacá", city: "Boyacá" }],
  },
  {
    id: "sse",
    name: "S&SE",
    bases: [{ id: "manizales", label: "Base Manizales", city: "Manizales" }],
  },
  {
    id: "gatria",
    name: "GATRIA",
    bases: [{ id: "bogota-gatria", label: "Base Bogotá", city: "Bogotá" }],
  },
  {
    id: "bia",
    name: "BIA",
    bases: [
      { id: "bogota-bia", label: "Unidad Bogotá", city: "Bogotá" },
      { id: "barranquilla-bia", label: "Unidad Barranquilla", city: "Barranquilla" },
    ],
  },
  {
    id: "dr-telemedida",
    name: "DR TELEMEDIDA",
    bases: [{ id: "medellin-drtele", label: "Base Medellín", city: "Medellín" }],
  },
  {
    id: "dtys-ingenieria",
    name: "DTYS INGENIERIA",
    bases: [{ id: "tunja", label: "Base Tunja", city: "Tunja" }],
  },
  {
    id: "jem-electrintegral",
    name: "JEM Electrintegral S.A.S",
    bases: [{ id: "ibague", label: "Base Ibagué", city: "Ibagué" }],
  },
  {
    id: "iselec",
    name: "ISELEC",
    bases: [{ id: "medellin-iselec", label: "Base Medellín", city: "Medellín" }],
  },
  {
    id: "mcr",
    name: "MCR",
    bases: [{ id: "bogota-mcr", label: "Base Bogotá", city: "Bogotá" }],
  },
  {
    id: "diselec",
    name: "DISELEC",
    bases: [{ id: "piedecuesta", label: "Base Piedecuesta", city: "Piedecuesta" }],
  },
  {
    id: "rehobot",
    name: "REHOBOT",
    bases: [{ id: "cucuta", label: "Base Cúcuta", city: "Cúcuta" }],
  },
  {
    id: "sge-energia",
    name: "SGE-ENERGIA",
    bases: [
      { id: "bucaramanga", label: "Base Bucaramanga", city: "Bucaramanga" },
      { id: "cali-sge", label: "Base Cali", city: "Cali" },
      { id: "medellin-sge", label: "Base Medellín", city: "Medellín" },
      { id: "villavicencio", label: "Base Villavicencio", city: "Villavicencio" },
      { id: "cartagena-sge", label: "Base Cartagena", city: "Cartagena" },
      { id: "pasto", label: "Base Pasto", city: "Pasto" },
    ],
  },
  {
    id: "ar-ingenieria",
    name: "AR INGENIERIA",
    bases: [{ id: "neiva-ar", label: "Base Neiva", city: "Neiva" }],
  },
  {
    id: "montajes-mte",
    name: "MONTAJES MTE",
    bases: [{ id: "neiva-mte", label: "Base Neiva", city: "Neiva" }],
  },
  {
    id: "c3-myd",
    name: "C3-MYD ingeniería",
    bases: [
      { id: "barranquilla-c3", label: "Base Barranquilla", city: "Barranquilla" },
      { id: "valledupar", label: "Base Valledupar", city: "Valledupar" },
      { id: "cartagena-c3", label: "Base Cartagena", city: "Cartagena" },
      { id: "monteria", label: "Base Montería", city: "Montería" },
      { id: "bogota-c3", label: "Base Bogotá", city: "Bogotá" },
    ],
  },
  {
    id: "isemec",
    name: "ISEMEC",
    bases: [
      { id: "bogota-isemec", label: "Base Bogotá", city: "Bogotá" },
      { id: "cali-isemec", label: "Base Cali", city: "Cali" },
    ],
  },
  {
    id: "elecproyectos",
    name: "ELECPROYECTOS",
    bases: [{ id: "cali-elecproyectos", label: "Base Cali", city: "Cali" }],
  },
  {
    id: "gmas-services",
    name: "GMAS SERVICES",
    bases: [{ id: "barranquilla-gmas", label: "Base Barranquilla", city: "Barranquilla" }],
  },
];

