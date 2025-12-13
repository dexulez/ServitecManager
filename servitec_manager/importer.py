import os
import pandas as pd
import pdfplumber
import re
from typing import List, Dict

class SmartImporter:
    """SmartImporter parses Excel or PDF files to extract product information.
    It returns a list of dictionaries with keys: 'name' and 'cost'.
    """

    def load_file(self, path: str) -> List[Dict[str, float]]:
        """Dispatch to the appropriate parser based on file extension."""
        ext = os.path.splitext(path)[1].lower()
        if ext in ['.xlsx', '.xls']:
            return self._parse_excel(path)
        if ext == '.pdf':
            return self._parse_pdf(path)
        raise ValueError(f"Unsupported file type: {ext}")

    def _parse_excel(self, path: str) -> List[Dict[str, float]]:
        """Read an Excel file with pandas and attempt to locate name and cost columns.
        Heuristic: look for column headers containing keywords.
        """
        df = pd.read_excel(path, dtype=str)
        # Normalise column names
        cols = {c.lower(): c for c in df.columns}
        # Find name column
        name_candidates = [c for k, c in cols.items() if any(kw in k for kw in ['desc', 'product', 'name', 'item'])]
        cost_candidates = [c for k, c in cols.items() if any(kw in k for kw in ['cost', 'price', 'precio', 'costo', 'net'])]
        if not name_candidates or not cost_candidates:
            raise ValueError('Could not detect required columns in Excel file')
        name_col = name_candidates[0]
        cost_col = cost_candidates[0]
        results = []
        for _, row in df.iterrows():
            name = str(row[name_col]).strip()
            try:
                cost = float(str(row[cost_col]).replace('$', '').replace(',', '').strip())
            except Exception:
                continue
            if name:
                results.append({'name': name.upper(), 'cost': cost})
        return results

    def _parse_pdf(self, path: str) -> List[Dict[str, float]]:
        """Extract tables from a PDF using pdfplumber. If no tables are found, fall back to regex.
        """
        results = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                # Try to extract tables first
                tables = page.extract_tables()
                for table in tables:
                    # Convert to DataFrame for easier handling
                    df = pd.DataFrame(table)
                    # Assume first row is header
                    df.columns = df.iloc[0]
                    df = df[1:]
                    # Normalise column names
                    cols = {str(c).lower(): c for c in df.columns if c is not None}
                    name_candidates = [c for k, c in cols.items() if any(kw in k for kw in ['desc', 'product', 'name', 'item'])]
                    cost_candidates = [c for k, c in cols.items() if any(kw in k for kw in ['cost', 'price', 'precio', 'costo', 'net'])]
                    if not name_candidates or not cost_candidates:
                        continue
                    name_col = name_candidates[0]
                    cost_col = cost_candidates[0]
                    for _, row in df.iterrows():
                        name = str(row[name_col]).strip()
                        try:
                            cost = float(str(row[cost_col]).replace('$', '').replace(',', '').strip())
                        except Exception:
                            continue
                        if name:
                            results.append({'name': name.upper(), 'cost': cost})
                # Fallback regex if no tables produced any result
                if not results:
                    text = page.extract_text()
                    # Simple pattern: "Some product description ... $1234"
                    pattern = r"([A-Za-z0-9\s\-]+)\s+\$?([0-9]+(?:[.,][0-9]{2})?)"
                    for match in re.finditer(pattern, text):
                        name = match.group(1).strip()
                        cost = float(match.group(2).replace(',', '.'))
                        results.append({'name': name.upper(), 'cost': cost})
        return results
