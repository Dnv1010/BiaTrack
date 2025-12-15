"""
Script para cargar datos de peajes desde formato Waze o texto estructurado
Uso: python load_tolls.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from data.tolls_parser import parse_waze_template, parse_toll_data_from_text, normalize_toll
import json

def main():
    print("=" * 60)
    print("Cargador de Peajes - BiaTrack")
    print("=" * 60)
    print("\nOpciones:")
    print("1. Pegar datos desde formato Waze template")
    print("2. Pegar datos en formato texto estructurado")
    print("3. Cargar desde archivo")
    print("4. Ver peajes actuales")
    
    choice = input("\nSelecciona una opción (1-4): ").strip()
    
    if choice == "1":
        print("\nPega el contenido del template Waze:")
        print("Formato: [wzTemplate topic=X post=Y]...[/wzTemplate]")
        print("Presiona Ctrl+Z (Windows) o Ctrl+D (Linux/Mac) seguido de Enter para terminar:")
        
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        text = '\n'.join(lines)
        template_data = parse_waze_template(text)
        
        if template_data:
            print(f"\nTemplate encontrado:")
            print(f"Topic: {template_data['topic']}")
            print(f"Post: {template_data['post']}")
            print(f"\nContenido:")
            print(template_data['content'])
            
            # Intentar parsear como datos de peajes
            tolls = parse_toll_data_from_text(template_data['content'])
            if tolls:
                print(f"\n✓ Se encontraron {len(tolls)} peajes:")
                for toll in tolls:
                    print(f"  - {toll['name']} ({toll['department']}): ${toll['fare_cop']:,} - {toll['status']}")
                
                save = input("\n¿Guardar en tolls_data.json? (s/n): ").strip().lower()
                if save == 's':
                    save_tolls_to_json(tolls)
            else:
                print("\nNo se pudieron parsear peajes del contenido. Revisa el formato.")
        else:
            print("\n✗ No se encontró un template Waze válido")
    
    elif choice == "2":
        print("\nPega los datos de peajes en formato texto:")
        print("Formato esperado:")
        print("Nombre del Peaje")
        print("Departamento: Nombre")
        print("Operador: Nombre (opcional)")
        print("Tarifa: 15000 COP")
        print("Estado: ACTIVE")
        print("\nPresiona Ctrl+Z (Windows) o Ctrl+D (Linux/Mac) seguido de Enter para terminar:")
        
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        text = '\n'.join(lines)
        tolls = parse_toll_data_from_text(text)
        
        if tolls:
            print(f"\n✓ Se encontraron {len(tolls)} peajes:")
            for i, toll in enumerate(tolls, 1):
                normalized = normalize_toll(toll, i)
                print(f"  {i}. {normalized['name']} ({normalized['department']}): ${normalized['fare_cop']:,} - {normalized['status']}")
            
            save = input("\n¿Guardar en tolls_data.json? (s/n): ").strip().lower()
            if save == 's':
                save_tolls_to_json(tolls)
        else:
            print("\n✗ No se encontraron peajes. Revisa el formato.")
    
    elif choice == "3":
        file_path = input("\nRuta del archivo (JSON o TXT): ").strip()
        if os.path.exists(file_path):
            if file_path.endswith('.json'):
                from data.tolls_parser import load_tolls_from_json
                tolls = load_tolls_from_json(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    tolls = parse_toll_data_from_text(f.read())
            
            if tolls:
                print(f"\n✓ Se cargaron {len(tolls)} peajes")
                save = input("¿Guardar en tolls_data.json? (s/n): ").strip().lower()
                if save == 's':
                    save_tolls_to_json(tolls)
            else:
                print("\n✗ No se encontraron peajes en el archivo")
        else:
            print("\n✗ Archivo no encontrado")
    
    elif choice == "4":
        from data.tolls import TOLLS
        print(f"\nPeajes actuales cargados: {len(TOLLS)}")
        if TOLLS:
            for i, toll in enumerate(TOLLS, 1):
                print(f"  {i}. {toll['name']} ({toll['department']}): ${toll['fare_cop']:,} - {toll['status']}")
        else:
            print("  (No hay peajes cargados)")

def save_tolls_to_json(tolls):
    """Guarda peajes en formato JSON"""
    normalized_tolls = [normalize_toll(toll, i) for i, toll in enumerate(tolls)]
    
    output_path = os.path.join('data', 'tolls_data.json')
    os.makedirs('data', exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(normalized_tolls, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Peajes guardados en {output_path}")
    print(f"  Total: {len(normalized_tolls)} peajes")

if __name__ == '__main__':
    main()

