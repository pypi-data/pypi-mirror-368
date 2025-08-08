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
    s = rutUnformat(rut)
    if len(s) < 2:
        raise ValueError("El RUT debe contener al menos el cuerpo y el dígito verificador")
    body, dv = s[:-1], s[-1]
    rev = body[::-1]
    parts = [rev[i:i+3][::-1] for i in range(0, len(rev), 3)]
    formatted_body = ".".join(parts[::-1])
    return f"{formatted_body}-{dv}"

def rutUnformat(rut: str) -> str:
    """
    Converts a formatted Chilean RUT (Rol Único Tributario) to its unformatted version.
    
    Args:
        rut (str): The formatted RUT to convert. (99.999.999-9)
        
    Returns:
        str: The unformatted RUT. (999999999)
    """
    if not isinstance(rut, str):
        raise TypeError("El RUT debe ser una cadena")
    # Keep only digits and 'k'/'K' (last char may be K)
    cleaned = "".join(ch for ch in rut if ch.isdigit() or ch.lower() == "k")
    return cleaned.upper()

def rutValidate(rut: str) -> bool:
    """
    Validates a Chilean RUT (Rol Único Tributario).
    
    Args:
        rut (str): The RUT to validate. (999999999)
        
    Returns:
        bool: True if the RUT is valid, False otherwise.
    """
    s = rutUnformat(rut)
    if len(s) < 2:
        return False
    body, dv_given = s[:-1], s[-1].upper()

    if not body.isdigit():
        return False
    
    multipliers = [2, 3, 4, 5, 6, 7]
    total = 0
    mult_idx = 0
    for ch in reversed(body):
        digit = ord(ch) - ord('0')
        multiplier = multipliers[mult_idx % len(multipliers)]
        total += digit * multiplier
        mult_idx += 1

    remainder = total % 11
    if remainder == 0:
        dv_calc = "0"
    elif remainder == 1:
        dv_calc = "K"
    else:
        dv_calc = str(11 - remainder)

    return dv_calc == dv_given