from mcp.server.fastmcp import FastMCP
import json
import os
import requests
import tempfile
try:
    import pandas as pd
except ImportError:
    pd = None

# Create an MCP server
mcp = FastMCP("Excel Reader")


# Add Excel reading tool
@mcp.tool()
def read_excel_to_json(url: str, sheet_name: str = None) -> str:
    """Read Excel file from URL and return JSON data
    
    Args:
        url: URL of the Excel file
        sheet_name: Optional sheet name (if not provided, reads first sheet)
    
    Returns:
        JSON string containing the Excel data
    """
    if pd is None:
        return json.dumps({"error": "pandas not installed. Please install with: pip install pandas openpyxl"})
    
    try:
        # Download file from URL
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            tmp_file.write(response.content)
            temp_path = tmp_file.name
        
        try:
            # Get all sheet names first
            excel_file = pd.ExcelFile(temp_path)
            available_sheets = excel_file.sheet_names
            
            # Determine which sheet to read
            if sheet_name:
                if sheet_name not in available_sheets:
                    return json.dumps({
                        "error": f"Sheet '{sheet_name}' not found. Available sheets: {available_sheets}"
                    })
                target_sheet = sheet_name
            else:
                target_sheet = available_sheets[0]
            
            # Read Excel file
            df = pd.read_excel(temp_path, sheet_name=target_sheet)
            
            # Handle datetime columns - convert to string
            for col in df.columns:
                if df[col].dtype == 'datetime64[ns]' or pd.api.types.is_datetime64_any_dtype(df[col]):
                    df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
                elif df[col].dtype == 'object':
                    # Handle mixed types that might include datetime
                    df[col] = df[col].astype(str)
            
            # Convert to JSON
            result = {
                "success": True,
                "url": url,
                "sheet_name": target_sheet,
                "available_sheets": available_sheets,
                "rows": len(df),
                "columns": list(df.columns),
                "data": df.to_dict(orient='records')
            }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        finally:
            # Clean up temp file
            os.unlink(temp_path)
        
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Failed to download file from URL: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Failed to read Excel file: {str(e)}"})


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

def main() -> None:
    mcp.run(transport="stdio")
