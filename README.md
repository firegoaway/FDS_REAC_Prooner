# FDS REAC Parameter Calculator

A Python application with a PyQt6 GUI for calculating Fire Dynamics Simulator (FDS) REAC parameters from fuel properties.

## Features

- User-friendly interface with light blue color theme
- Calculates FDS REAC parameters based on fuel inputs
- Generates ready-to-use FDS input lines
- Copy results directly to clipboard
- Input validation with helpful error messages

## Requirements

- Python 3.6 or higher
- PyQt6

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install PyQt6
```

3. Run the application:

```bash
python FDS_REAC_Prooner.py
```

## How to Use

1. Enter the following fuel parameters:
   - Heat Release Rate (kJ/kg)
   - Soot Yield (m²/kg)
   - O₂ Consumption (kg/kg)
   - CO₂ Yield (kg/kg)
   - CO Yield (kg/kg)
   - HCl Yield (kg/kg) - optional, can be left blank
   - Molar Mass (g/mol)

2. Click "Calculate" to generate the FDS REAC lines
3. Use "Copy to Clipboard" to copy the results
4. "Clear" button resets all inputs and results

## Calculation Method

The application calculates the following parameters:

1. Air = O₂ + 3.7619N₂
2. Fuel + ϑ_{O₂}Air → Products
3. ϑ_{O₂} = (W_{Fuel}/W_{O₂})*Y_{O₂}
4. ϑ_{CO₂} = (W_{Fuel}/W_{CO₂})*Y_{CO₂}
5. ϑ_{CO} = (W_{Fuel}/W_{CO})*Y_{CO}
6. ϑ_{Soot} = (W_{Fuel}/W_{Soot})*Y_{Soot}/8700
7. ϑ_{HCl} = (W_{Fuel}/W_{HCl})*Y_{HCl}
8. Y_{H₂O} = 1 + Y_{O₂} - Y_{CO₂} - Y_{CO} - Y_{Soot} - Y_{HCl}
9. ϑ_{H₂O} = (W_{Fuel}/W_{H₂O})*Y_{H₂O}
10. ϑ_{N₂} = 3.7619*ϑ_{O₂}

## Example Output

```
&SPEC ID='OXYGEN' LUMPED_COMPONENT_ONLY=.True./
&SPEC ID='NITROGEN' LUMPED_COMPONENT_ONLY=.True./
&SPEC ID='CARBON DIOXIDE' LUMPED_COMPONENT_ONLY=.True./
&SPEC ID='CARBON MONOXIDE' LUMPED_COMPONENT_ONLY=.True./
&SPEC ID='HYDROGEN CHLORIDE' LUMPED_COMPONENT_ONLY=.True./
&SPEC ID='WATER VAPOR' LUMPED_COMPONENT_ONLY=.True./
&SPEC ID='SOOT' LUMPED_COMPONENT_ONLY=.True./
&SPEC ID='Fuel' MW=104.3233/
&SPEC ID='AIR' BACKGROUND=.True. SPEC_ID(1:2)='OXYGEN','NITROGEN' VOLUME_FRACTION(1:2)=1,3.7619/
&SPEC ID='PRODUCTS' SPEC_ID(1:6)='SOOT','CARBON DIOXIDE','CARBON MONOXIDE','HYDROGEN CHLORIDE','WATER VAPOR','NITROGEN' VOLUME_FRACTION(1:6)=0.000100000000000,5.924161818181818,0.186547500000000,0.028582849315068,0.871428832502849,19.394223750000002/
&REAC FUEL='Fuel' HEAT_OF_COMBUSTION=31700 SPEC_ID_NU(1:3)='Fuel','AIR','PRODUCTS' NU(1:3)=-1,-8.6115,1 REAC_ATOM_ERROR=1E5 REAC_MASS_ERROR=1E4 CHECK_ATOM_BALANCE=.False./
```

## License

This project is open-source software and available under the MIT License. 