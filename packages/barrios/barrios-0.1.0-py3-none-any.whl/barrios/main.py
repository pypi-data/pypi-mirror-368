"""
General functions
"""

# Functions

# Rut Functions

def rutFormat(rut: str) -> str:
    """
    Formats a Chilean RUT (Rol Único Tributario) to the standard format.
    
    Args:
        rut (str): The RUT to format. (999999999)
        
    Returns:
        str: The formatted RUT. (99.999.999-9)
    """

def rutUnformat(rut: str) -> str:
    """
    Converts a formatted Chilean RUT (Rol Único Tributario) to its unformatted version.
    
    Args:
        rut (str): The formatted RUT to convert. (99.999.999-9)
        
    Returns:
        str: The unformatted RUT. (999999999)
    """

def rutValidate(rut: str) -> bool:
    """
    Validates a Chilean RUT (Rol Único Tributario).
    
    Args:
        rut (str): The RUT to validate. (999999999)
        
    Returns:
        bool: True if the RUT is valid, False otherwise.
    """

def rutWho(rut: str) -> str:
    """
    Give the name of the person or entity associated with a Chilean RUT.

    Args:
        rut (str): The RUT to look up. (999999999)

    Returns:
        name (str): The name associated with the RUT, or "Unknown" if not found.
        location (str): The location associated with the RUT, or "Unknown" if not found.
        sex (str): The sex of the person associated with the RUT, or "Unknown" if not found.
    """