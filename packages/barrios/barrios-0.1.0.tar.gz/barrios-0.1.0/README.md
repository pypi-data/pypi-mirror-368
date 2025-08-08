# BarriosLib

BarriosLib is a personal Python library where I add functions to make my work easier.  
Anyone can use it, but it’s mainly for my own convenience.  
More functions will be added over time.

## Current Functions

### RUT Functions
- **rutFormat(rut: str) -> str**  
  Formats a Chilean RUT to the standard format (e.g., `99.999.999-9`).

- **rutUnformat(rut: str) -> str**  
  Removes formatting from a Chilean RUT (e.g., `999999999`).

- **rutValidate(rut: str) -> bool**  
  Checks if a Chilean RUT is valid.

- **rutWho(rut: str) -> str**  
  Returns the name, location, and sex associated with a Chilean RUT (if available).
