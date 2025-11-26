"""
Modul za razbijanje PDF fajlova
"""

from pathlib import Path
from typing import List, Optional
import re

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    raise ImportError("Potrebno je instalirati pypdf: pip install pypdf")


class PDFSplitter:
    """Klasa za razbijanje PDF fajlova"""
    
    def __init__(self, input_path: str, output_dir: str = "output"):
        """
        Inicijalizuje PDFSplitter
        
        Args:
            input_path: Putanja do ulaznog PDF fajla
            output_dir: Direktorijum za izlazne PDF fajlove
        """
        self.input_path = Path(input_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.input_path.exists():
            raise FileNotFoundError(f"PDF fajl nije pronađen: {input_path}")
        
        if not self.input_path.suffix.lower() == '.pdf':
            raise ValueError(f"Fajl mora biti PDF: {input_path}")
    
    def split_by_pages(self, pages_per_file: int) -> List[str]:
        """
        Razbija PDF po broju stranica
        
        Args:
            pages_per_file: Broj stranica po izlaznom fajlu
            
        Returns:
            Lista putanja do kreiranih PDF fajlova
        """
        # TODO: Implementirati logiku za razbijanje po stranicama
        pass
    
    def split_by_size(self, max_size_mb: float) -> List[str]:
        """
        Razbija PDF po maksimalnoj veličini
        
        Args:
            max_size_mb: Maksimalna veličina fajla u MB
            
        Returns:
            Lista putanja do kreiranih PDF fajlova
        """
        # TODO: Implementirati logiku za razbijanje po veličini
        pass
    
    def split_by_markers(self, markers: List[str]) -> List[str]:
        """
        Razbija PDF na osnovu markera (npr. naslova, ključnih reči)
        
        Args:
            markers: Lista markera za podele
            
        Returns:
            Lista putanja do kreiranih PDF fajlova
        """
        # TODO: Implementirati logiku za razbijanje po markerima
        pass
    
    def split_invoices(self, 
                      invoice_markers: Optional[List[str]] = None,
                      page_start_pattern: Optional[str] = None) -> List[str]:
        """
        Razbija PDF sa više faktura u pojedinačne PDF fajlove (jedan po fakturi)
        
        Args:
            invoice_markers: Lista markera za prepoznavanje početka fakture 
                           (npr. ["Faktura", "Invoice", "Faktura br."])
                           Ako nije navedeno, koristi se default lista
            page_start_pattern: Regex pattern za prepoznavanje početka nove fakture
                              Ako nije navedeno, traži se po markerima
                              
        Returns:
            Lista putanja do kreiranih PDF fajlova (jedan po fakturi)
        """
        if invoice_markers is None:
            invoice_markers = [
                "Faktura",
                "Invoice", 
                "Faktura br.",
                "Invoice No.",
                "Račun",
                "Bill"
            ]
        
        reader = PdfReader(str(self.input_path))
        total_pages = len(reader.pages)
        
        # Pronađi stranice gde počinju nove fakture
        invoice_starts = self._find_invoice_starts(reader, invoice_markers, page_start_pattern)
        
        if not invoice_starts:
            raise ValueError("Nisu pronađene fakture u PDF-u. Proverite markere ili strukturu fajla.")
        
        # Dodaj poslednju stranicu kao kraj poslednje fakture
        invoice_starts.append(total_pages)
        
        # Kreiraj pojedinačne PDF fajlove
        output_files = []
        base_name = self.input_path.stem
        
        for i in range(len(invoice_starts) - 1):
            start_page = invoice_starts[i]
            end_page = invoice_starts[i + 1]
            
            writer = PdfWriter()
            
            # Dodaj stranice za ovu fakturu
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])
            
            # Sačuvaj fajl
            output_filename = f"{base_name}_faktura_{i+1:03d}.pdf"
            output_path = self.output_dir / output_filename
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            output_files.append(str(output_path))
            print(f"Kreirana faktura {i+1}: {output_filename} (stranice {start_page+1}-{end_page})")
        
        return output_files
    
    def _find_invoice_starts(self, 
                            reader: PdfReader, 
                            markers: List[str],
                            pattern: Optional[str] = None) -> List[int]:
        """
        Pronalazi stranice gde počinju nove fakture
        
        Args:
            reader: PdfReader objekat
            markers: Lista markera za prepoznavanje faktura
            pattern: Regex pattern (ako je naveden, koristi se umesto markera)
            
        Returns:
            Lista brojeva stranica gde počinju fakture (0-indexed)
        """
        invoice_starts = [0]  # Prva stranica uvek počinje prvu fakturu
        
        for page_num in range(1, len(reader.pages)):  # Počni od druge stranice
            page = reader.pages[page_num]
            text = page.extract_text()
            
            if not text:
                continue
            
            # Proveri da li stranica sadrži marker za početak nove fakture
            is_new_invoice = False
            
            if pattern:
                # Koristi regex pattern
                if re.search(pattern, text, re.IGNORECASE):
                    is_new_invoice = True
            else:
                # Koristi markere
                for marker in markers:
                    # Traži marker na početku stranice ili u gornjem delu
                    # (prvih 500 karaktera za brže pretraživanje)
                    if marker.lower() in text[:500].lower():
                        # Proveri da li je marker dovoljno blizu početka stranice
                        # da bi bio početak nove fakture, a ne samo spomen u tekstu
                        marker_pos = text.lower().find(marker.lower())
                        if marker_pos < 500:  # Marker je u gornjem delu stranice
                            is_new_invoice = True
                            break
            
            if is_new_invoice:
                invoice_starts.append(page_num)
        
        return invoice_starts

