"""
Multi-Tier Layout-Robust OCR & Document Extraction Engine for Grid Interconnection Files.
Processes E.8 (Plant Datasheet), E.9 (DSO Requirements), and SLD (Single Line Diagram) PDFs.
Handles varied European / German grid operator layouts (Bayernwerk, Netze BW, E.ON, Westnetz, etc.).
"""

import io
import re
import logging
from typing import Dict, Any, List, Optional
from pypdf import PdfReader
from PIL import Image

logger = logging.getLogger("coneza_ocr")

class GridDocumentOCREngine:
    """
    Extracts text, tabular structures, and electrical parameters from E8, E9, and SLD documents.
    Operates on digital and scanned PDFs, normalizing key-value parameters.
    """

    def __init__(self):
        # Check if pytesseract is optionally available on the host
        self.tesseract_available = False
        try:
            import pytesseract
            self.tesseract_available = True
        except ImportError:
            pass

    def extract_document(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """Extracts text, analyzes layout, identifies document type, and extracts key electrical fields."""
        extracted_pages: List[Dict[str, Any]] = []
        full_text_parts: List[str] = []

        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            total_pages = len(reader.pages)

            for page_idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                image_count = len(page.images)
                
                # If page text is very sparse and images exist, attempt OCR if tesseract is installed
                if len(page_text.strip()) < 40 and image_count > 0 and self.tesseract_available:
                    ocr_text_parts = []
                    try:
                        import pytesseract
                        for img_obj in page.images:
                            pil_img = Image.open(io.BytesIO(img_obj.data))
                            ocr_part = pytesseract.image_to_string(pil_img)
                            if ocr_part:
                                ocr_text_parts.append(ocr_part)
                        if ocr_text_parts:
                            page_text += "\n[OCR Extracted Text]\n" + "\n".join(ocr_text_parts)
                    except Exception as ocr_err:
                        logger.warning(f"Tesseract OCR attempt failed on page {page_idx + 1}: {ocr_err}")

                extracted_pages.append({
                    "page_number": page_idx + 1,
                    "character_count": len(page_text),
                    "image_count": image_count,
                    "text": page_text
                })
                full_text_parts.append(page_text)

        except Exception as e:
            logger.error(f"PDF extraction error for {filename}: {e}")
            return {
                "filename": filename,
                "success": False,
                "error": str(e),
                "detected_type": "UNKNOWN",
                "full_text": "",
                "pages": []
            }

        combined_text = "\n--- PAGE BREAK ---\n".join(full_text_parts)
        detected_type = self._classify_document(filename, combined_text)
        extracted_entities = self._extract_grid_entities(combined_text, detected_type)

        return {
            "filename": filename,
            "success": True,
            "detected_type": detected_type,
            "total_pages": len(extracted_pages),
            "pages": extracted_pages,
            "full_text": combined_text,
            "extracted_entities": extracted_entities
        }

    def _classify_document(self, filename: str, text: str) -> str:
        """Classifies whether the document is E.8, E.9, or SLD based on name and text markers."""
        upper_name = filename.upper()
        upper_text = text.upper()

        if "E8" in upper_name or "E.8" in upper_name or "DATENBLATT EINER ERZEUGUNGSANLAGE" in upper_text or "DATENBLATT SPEICHER" in upper_text:
            return "E8"
        elif "E9" in upper_name or "E.9" in upper_name or "INBETRIEBSETZUNGSPROTOKOLL" in upper_text or "ABFRAGEBOGEN" in upper_text or "NETZBETREIBER" in upper_text and "VDE-AR-N 4110" in upper_text:
            return "E9"
        elif "SLD" in upper_name or "SCHALTPLAN" in upper_name or "SINGLE LINE" in upper_name or "EINPOLIG" in upper_text or "ÜBERSICHTSSCHALTPLAN" in upper_text:
            return "SLD"
        
        # Fallback heuristic based on keyword density
        if "WECHSELRICHTER" in upper_text and ("PMAX" in upper_text or "KW" in upper_text or "KVA" in upper_text):
            return "E8"
        if "Q(U)" in upper_text or "COS PHI" in upper_text or "EINSCHALTUNG" in upper_text or "FERNWIRK" in upper_text:
            return "E9"
        if "TRAFO" in upper_text or "SCHALTER" in upper_text or "KABEL" in upper_text or "SAMMELSCHIENE" in upper_text:
            return "SLD"

        return "E8"

    def _extract_grid_entities(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Parses common German / European grid application parameters via regex & layout heuristics."""
        entities: Dict[str, Any] = {}

        # 1. Rated / Active Power (kW / MW)
        p_matches = re.findall(r'(?:P(?:inst|max|n|av|r)?|Wirkleistung|Einspeiseleistung)[^\n0-9]{0,40}[\s:=]*\n?\s*([0-9]+[.,]?[0-9]*)\s*\n?\s*\b(k?W|MW)\b', text, re.IGNORECASE)
        if p_matches:
            val, unit = p_matches[0]
            val_f = float(val.replace(',', '.'))
            if unit.upper() == 'MW':
                val_f *= 1000.0
            entities["active_power_kw"] = val_f

        # 2. Grid Voltage (kV or V)
        u_matches = re.findall(r'(?:Netzspannung|Nennspannung|Netznennspannung|Un|U_n|Spannungsebene)[^\n0-9]{0,40}[\s:=]*\n?\s*([0-9]+[.,]?[0-9]*)\s*\n?\s*\b(k?V)\b', text, re.IGNORECASE)
        if u_matches:
            val, unit = u_matches[0]
            val_f = float(val.replace(',', '.'))
            if unit.upper() == 'KV':
                val_f *= 1000.0
            entities["grid_voltage_v"] = val_f

        # 3. Apparent Power (kVA / MVA)
        s_matches = re.findall(r'(?:Scheinleistung|Bemessungsscheinleistung|Sr|Sn|S_max)[^\n0-9]{0,40}[\s:=]*\n?\s*([0-9]+[.,]?[0-9]*)\s*\n?\s*\b(kVA|MVA)\b', text, re.IGNORECASE)
        if s_matches:
            val, unit = s_matches[0]
            val_f = float(val.replace(',', '.'))
            if unit.upper() == 'MVA':
                val_f *= 1000.0
            entities["apparent_power_kva"] = val_f

        # 4. Reactive power mode
        if "Q(U)" in text:
            entities["reactive_mode"] = "Q(U)"
        elif "cos" in text.lower() and "phi" in text.lower():
            entities["reactive_mode"] = "cos(phi)"
        elif "Q-fest" in text or "Blindleistungsvorgabe" in text:
            entities["reactive_mode"] = "Q_fixed"

        # 5. cos(phi) setpoint value
        cos_matches = re.findall(r'(?:cos\s*[\(]?\s*phi|Leistungsfaktor)[\s:=]*\n?\s*([0-9]+[.,]?[0-9]+)', text, re.IGNORECASE)
        if cos_matches:
            entities["cos_phi"] = float(cos_matches[0].replace(',', '.'))

        # 6. Transformer data
        trafo_match = re.findall(r'(?:Transformator|Trafo|Kurzschlussspannung|u_k)[^\n0-9]{0,40}[\s:=]*\n?\s*([0-9]+[.,]?[0-9]*)\s*\n?\s*%', text, re.IGNORECASE)
        if trafo_match:
            entities["transformer_uk_percent"] = float(trafo_match[0].replace(',', '.'))

        # 7. Breakers / Switching elements (SLD)
        breaker_matches = re.findall(r'\b(Q0|Q1|Q2|Q3|Q4|Q9|F1|F2|T1|T2)\b', text)
        if breaker_matches:
            entities["detected_equipment_tags"] = list(set(breaker_matches))

        return entities

ocr_engine = GridDocumentOCREngine()
