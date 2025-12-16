"""
Modul za editovanje PDF fajlova - zamena teksta
"""

from pathlib import Path
from typing import Optional
import io

try:
    from pypdf import PdfReader, PdfWriter
    import pypdf
except ImportError:
    raise ImportError("Potrebno je instalirati pypdf: pip install pypdf")

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class PDFEditor:
    """Klasa za editovanje PDF fajlova - zamena teksta"""
    
    def __init__(self, input_path: str):
        """
        Inicijalizuje PDFEditor
        
        Args:
            input_path: Putanja do ulaznog PDF fajla
        """
        self.input_path = Path(input_path)
        
        if not self.input_path.exists():
            raise FileNotFoundError(f"PDF fajl nije pronađen: {input_path}")
        
        if not self.input_path.suffix.lower() == '.pdf':
            raise ValueError(f"Fajl mora biti PDF: {input_path}")
    
    def replace_text(self, old_text: str, new_text: str, output_path: Optional[str] = None) -> str:
        """
        Zamenjuje tekst u PDF fajlu
        
        Args:
            old_text: Tekst koji treba zameniti
            new_text: Novi tekst
            output_path: Putanja za izlazni PDF (ako nije navedeno, kreira se automatski)
            
        Returns:
            Putanja do izmenjenog PDF fajla
        """
        if PYMUPDF_AVAILABLE:
            return self._replace_text_pymupdf(old_text, new_text, output_path)
        else:
            return self._replace_text_pypdf(old_text, new_text, output_path)
    
    def _replace_text_pymupdf(self, old_text: str, new_text: str, output_path: Optional[str] = None) -> str:
        """
        Zamenjuje tekst koristeći PyMuPDF (fitz) - bolja metoda
        """
        if output_path is None:
            output_path = str(self.input_path.parent / f"{self.input_path.stem}_edited.pdf")
        
        # Otvori PDF
        doc = fitz.open(str(self.input_path))
        try:
            # Prođi kroz sve stranice
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Pronađi sve instance starog teksta
                text_instances = page.search_for(old_text)
            
                # Prvo prikupi sve redakcije i podatke za umetanje teksta
                text_insertions = []
                for inst in text_instances:
                    # Dodaj redakciju (ne primenjuj još)
                    page.add_redact_annot(inst)
                    
                    # Sačuvaj podatke za umetanje teksta pre primene redakcija
                    rect_height = inst.height
                    font_size = rect_height * 0.8  # Približno 80% visine
                    point = fitz.Point(inst.x0, inst.y1 - (rect_height - font_size) / 2)
                    text_insertions.append((point, font_size, new_text))
            
                # Primeni sve redakcije odjednom
                if text_instances:
                    page.apply_redactions()
            
                # Zatim umetni sve nove tekstove
                for point, font_size, text in text_insertions:
                    page.insert_text(
                        point,
                            text,
                        fontsize=font_size,
                    color=(0, 0, 0)  # Crna boja
                )
            
                # Sačuvaj izmenjeni PDF
                doc.save(output_path)
            doc.save(output_path)
        finally:
            # Uvek zatvori dokument, čak i ako se desi izuzetak
            doc.close()
        
        return output_path
    
    def _replace_text_pypdf(self, old_text: str, new_text: str, output_path: Optional[str] = None) -> str:
        """
        Zamenjuje tekst koristeći pypdf - osnovna metoda
        Napomena: pypdf ima ograničene mogućnosti za direktnu zamenu teksta,
        pa ova metoda koristi PyMuPDF ako je dostupan, inače vraća grešku
        """
        if not PYMUPDF_AVAILABLE:
            raise ImportError(
                "Za zamenu teksta u PDF-u potrebno je instalirati PyMuPDF: pip install PyMuPDF\n"
                "pypdf ne podržava direktnu zamenu teksta u postojećim PDF fajlovima."
            )
        
        # Ako je PyMuPDF dostupan, koristi ga
        return self._replace_text_pymupdf(old_text, new_text, output_path)
    
    def replace_text_multiple(self, replacements: dict, output_path: Optional[str] = None) -> str:
        """
        Zamenjuje više tekstova odjednom
        
        Args:
            replacements: Dictionary sa parovima {old_text: new_text}
            output_path: Putanja za izlazni PDF
            
        Returns:
            Putanja do izmenjenog PDF fajla
        """
        if output_path is None:
            output_path = str(self.input_path.parent / f"{self.input_path.stem}_edited.pdf")
        
        if PYMUPDF_AVAILABLE:
            # Otvori PDF
            doc = fitz.open(str(self.input_path))
            try:
                # Prođi kroz sve stranice
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    
                    # Prvo prikupi sve redakcije i podatke za umetanje teksta
                    text_insertions = []
                    for old_text, new_text in replacements.items():
                        # Pronađi sve instance starog teksta
                        text_instances = page.search_for(old_text)
                        
                        # Prikupi sve redakcije i podatke za umetanje
                        for inst in text_instances:
                            # Dodaj redakciju (ne primenjuj još)
                            page.add_redact_annot(inst)
                            
                            # Sačuvaj podatke za umetanje teksta pre primene redakcija
                            rect_height = inst.height
                            font_size = rect_height * 0.8
                            point = fitz.Point(inst.x0, inst.y1 - (rect_height - font_size) / 2)
                            text_insertions.append((point, font_size, new_text))
                
                    # Primeni sve redakcije odjednom
                    if text_insertions:
                        page.apply_redactions()
                    
                    # Zatim umetni sve nove tekstove
                    for point, font_size, text in text_insertions:
                        page.insert_text(
                            point,
                        text,
                        fontsize=font_size,
                        color=(0, 0, 0)
                    )
            
                # Sačuvaj izmenjeni PDF
                doc.save(output_path)
                doc.save(output_path)
            finally:
                # Uvek zatvori dokument, čak i ako se desi izuzetak
                doc.close()
            
            return output_path
        else:
            raise ImportError(
                "Za zamenu teksta u PDF-u potrebno je instalirati PyMuPDF: pip install PyMuPDF"
            )

