"""
Table handling module for docx-json-replacer.
Provides functionality to create and style tables from JSON data.
"""
from typing import Dict, Any, List, Union, Optional
from docxtpl import DocxTemplate, RichText
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


class TableHandler:
    """Handles table creation and styling from JSON data"""
    
    @staticmethod
    def is_table_data(value: Any) -> bool:
        """Check if the value represents table data"""
        if not isinstance(value, list):
            return False
        
        if len(value) == 0:
            return False
            
        # Check if it's a list of dictionaries with 'cells' key
        first_item = value[0]
        if isinstance(first_item, dict) and 'cells' in first_item:
            return True
            
        # Check if it's a list of lists (simple table)
        if isinstance(first_item, list):
            return True
            
        # Check if it's a list of dictionaries (data table)
        if isinstance(first_item, dict):
            return True
            
        return False
    
    @staticmethod
    def parse_html_table(html_content: str) -> List[Dict[str, Any]]:
        """Parse HTML table string into table data structure"""
        import re
        
        # Basic HTML table parsing
        rows = []
        
        # Find all <tr> tags
        tr_pattern = r'<tr[^>]*>(.*?)</tr>'
        tr_matches = re.findall(tr_pattern, html_content, re.IGNORECASE | re.DOTALL)
        
        for tr_content in tr_matches:
            # Find all <td> or <th> tags
            cell_pattern = r'<(?:td|th)[^>]*>(.*?)</(?:td|th)>'
            cells = re.findall(cell_pattern, tr_content, re.IGNORECASE | re.DOTALL)
            
            # Clean HTML from cell content
            cleaned_cells = []
            for cell in cells:
                # Remove HTML tags
                clean_cell = re.sub(r'<[^>]+>', '', cell).strip()
                cleaned_cells.append(clean_cell)
            
            if cleaned_cells:
                rows.append({'cells': cleaned_cells})
        
        return rows
    
    @staticmethod
    def process_table_data(data: Union[List[Dict], List[List], str]) -> Dict[str, Any]:
        """
        Process various table data formats into a standardized structure
        
        Args:
            data: Table data in various formats:
                - List of dicts with 'cells' and optional 'style'
                - List of lists (simple rows)
                - List of dicts (data rows)
                - HTML table string
        
        Returns:
            Standardized table context for docxtpl
        """
        # Handle HTML table strings
        if isinstance(data, str) and '<table' in data.lower():
            data = TableHandler.parse_html_table(data)
        
        if not isinstance(data, list) or len(data) == 0:
            return {'rows': []}
        
        first_item = data[0]
        
        # Format 1: List of dicts with 'cells' key (styled table)
        if isinstance(first_item, dict) and 'cells' in first_item:
            return TableHandler._process_styled_table(data)
        
        # Format 2: List of lists (simple table)
        elif isinstance(first_item, list):
            return TableHandler._process_simple_table(data)
        
        # Format 3: List of dicts (data table)
        elif isinstance(first_item, dict):
            return TableHandler._process_data_table(data)
        
        return {'rows': []}
    
    @staticmethod
    def _process_styled_table(data: List[Dict]) -> Dict[str, Any]:
        """Process table with styling information"""
        rows = []
        for row_data in data:
            row = {
                'cells': row_data.get('cells', []),
                'style': row_data.get('style', {})
            }
            
            # Process style information
            if 'style' in row_data and isinstance(row_data['style'], dict):
                style = row_data['style']
                row['bg'] = style.get('bg', '')
                row['color'] = style.get('color', '')
                row['bold'] = style.get('bold', False)
                row['italic'] = style.get('italic', False)
            
            rows.append(row)
        
        return {'rows': rows, 'has_style': True}
    
    @staticmethod
    def _process_simple_table(data: List[List]) -> Dict[str, Any]:
        """Process simple list of lists table"""
        rows = []
        for row_data in data:
            rows.append({
                'cells': row_data,
                'style': {}
            })
        
        return {'rows': rows, 'has_style': False}
    
    @staticmethod
    def _process_data_table(data: List[Dict]) -> Dict[str, Any]:
        """Process list of dictionaries as table with headers"""
        if not data:
            return {'rows': []}
        
        # Extract headers from first item keys
        headers = list(data[0].keys())
        
        rows = []
        
        # Add header row with default styling
        rows.append({
            'cells': headers,
            'style': {'bg': '4472C4', 'color': 'FFFFFF', 'bold': True}
        })
        
        # Add data rows
        for item in data:
            cells = [str(item.get(key, '')) for key in headers]
            rows.append({
                'cells': cells,
                'style': {}
            })
        
        return {'rows': rows, 'has_style': True, 'has_headers': True}
    
    @staticmethod
    def create_table_context(key: str, value: Any) -> Dict[str, Any]:
        """
        Create table context for template rendering
        
        Args:
            key: The JSON key (e.g., 'input.otrosdocs')
            value: The table data
        
        Returns:
            Context dict with table data for docxtpl
        """
        if not TableHandler.is_table_data(value) and not (isinstance(value, str) and '<table' in value.lower()):
            return {key: value}
        
        table_data = TableHandler.process_table_data(value)
        
        # Create context with table data
        context = {
            f"{key}_table": table_data['rows'],
            f"{key}_has_style": table_data.get('has_style', False),
            f"{key}_has_headers": table_data.get('has_headers', False)
        }
        
        return context
    
    @staticmethod
    def apply_cell_style(cell, style: Dict[str, Any]) -> None:
        """
        Apply styling to a table cell
        
        Args:
            cell: docx table cell object
            style: Style dictionary with bg, color, bold, italic
        """
        if not style:
            return
        
        # Apply background color
        if 'bg' in style and style['bg']:
            TableHandler._set_cell_background(cell, style['bg'])
        
        # Apply text formatting
        if cell.paragraphs:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    if 'bold' in style:
                        run.bold = style['bold']
                    if 'italic' in style:
                        run.italic = style['italic']
                    # Note: Text color requires more complex handling
    
    @staticmethod
    def _set_cell_background(cell, color: str) -> None:
        """
        Set background color for a table cell
        
        Args:
            cell: docx table cell
            color: Hex color code (without #)
        """
        # Remove # if present
        color = color.replace('#', '')
        
        # Get or create cell properties
        tc_pr = cell._tc.get_or_add_tcPr()
        
        # Create shading element
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), color)
        
        # Remove existing shading if present
        existing_shd = tc_pr.find(qn('w:shd'))
        if existing_shd is not None:
            tc_pr.remove(existing_shd)
        
        # Add new shading
        tc_pr.append(shd)