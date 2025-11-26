"""
Glavni modul za pokretanje PDF Splitter aplikacije
"""

import sys
import argparse
from pathlib import Path

# Dodaj src folder u Python path
sys.path.insert(0, str(Path(__file__).parent))

from pdf_splitter import PDFSplitter


def main():
    """Glavna funkcija aplikacije"""
    parser = argparse.ArgumentParser(
        description="PDF Splitter - Razbijanje PDF-a sa više faktura u pojedinačne fajlove"
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Putanja do PDF fajla sa fakturima"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="output",
        help="Direktorijum za izlazne PDF fajlove (default: output)"
    )
    parser.add_argument(
        "-m", "--markers",
        nargs="+",
        help="Markeri za prepoznavanje početka fakture (npr. 'Faktura' 'Invoice')"
    )
    parser.add_argument(
        "-p", "--pattern",
        type=str,
        help="Regex pattern za prepoznavanje početka nove fakture"
    )
    
    args = parser.parse_args()
    
    print("PDF Splitter - Razbijanje faktura")
    print("=" * 50)
    print(f"Ulazni fajl: {args.input_file}")
    print(f"Izlazni folder: {args.output}")
    print()
    
    try:
        splitter = PDFSplitter(args.input_file, args.output)
        output_files = splitter.split_invoices(
            invoice_markers=args.markers,
            page_start_pattern=args.pattern
        )
        
        print()
        print("=" * 50)
        print(f"Uspešno kreirano {len(output_files)} faktura!")
        print(f"Fajlovi su sačuvani u: {args.output}")
        
    except FileNotFoundError as e:
        print(f"Greška: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Greška: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Neočekivana greška: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

