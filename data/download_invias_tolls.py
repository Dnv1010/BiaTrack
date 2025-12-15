import json
import os
import time
from typing import Dict, Any, List, Optional

import requests

BASE = "https://hermes.invias.gov.co/arcgis/rest/services/SEIV_GEIV/Peajes_INVIAS/FeatureServer/0/query"

OUTFILE = "peajes_colombia.geojson"
PAGE_SIZE = 1000

# Campos: ajusta si quieres más/menos
OUT_FIELDS = "nombre,codigo_via,administra,territoria,latsig,longsig"


def fetch_page_geojson(offset: int) -> Optional[Dict[str, Any]]:
    """
    Intenta pedir directamente GeoJSON (f=geojson).
    Devuelve un dict GeoJSON si hay features; None si no hay.
    """
    params = {
        "where": "1=1",
        "outFields": OUT_FIELDS,
        "returnGeometry": "true",
        "outSR": 4326,
        "resultRecordCount": PAGE_SIZE,
        "resultOffset": offset,
        "f": "geojson",
    }

    r = requests.get(BASE, params=params, timeout=60)
    r.raise_for_status()
    data = r.json()

    feats = data.get("features", [])
    if not feats:
        return None
    return data


def main():
    all_features: List[Dict[str, Any]] = []
    offset = 0

    while True:
        page = fetch_page_geojson(offset)
        if page is None:
            break

        feats = page.get("features", [])
        all_features.extend(feats)

        print(f"Offset {offset}: +{len(feats)} (total {len(all_features)})")
        offset += PAGE_SIZE

        # Pequeña pausa para ser amable con el servidor
        time.sleep(0.15)

    geojson = {
        "type": "FeatureCollection",
        "features": all_features,
    }

    output_path = os.path.join(os.path.dirname(__file__), OUTFILE)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Guardado: {output_path}")
    print(f"[OK] Total features: {len(all_features)}")


if __name__ == "__main__":
    main()

