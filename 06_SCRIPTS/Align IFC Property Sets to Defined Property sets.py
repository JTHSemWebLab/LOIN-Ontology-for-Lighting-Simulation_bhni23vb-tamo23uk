import sys
from typing import Dict, Tuple, Optional

try:
    import ifcopenshell
except ImportError as e:
    raise SystemExit(
        "IfcOpenShell is required.\n"
        "Install with: pip install ifcopenshell\n"
        f"Import error: {e}"
    )

# (PsetName, PropertyName) -> Target IFC simple type
TARGET_TYPES: Dict[Tuple[str, str], str] = {
    ("Pset_Electrical", "PowerFactor"): "IFCNORMALISEDRATIOMEASURE",
    ("Pset_Electrical", "RatedVoltage"): "IFCELECTRICVOLTAGEMEASURE",
    ("Pset_Electrical", "StandByPower"): "IFCPOWERMEASURE",

    ("Pset_MechanicalAndInstallation", "MountingType"): "IFCLABEL",
    ("Pset_MechanicalAndInstallation", "Length"): "IFCLENGTHMEASURE",
    ("Pset_MechanicalAndInstallation", "IPRating"): "IFCLABEL",
    ("Pset_MechanicalAndInstallation", "Height"): "IFCLENGTHMEASURE",
    ("Pset_MechanicalAndInstallation", "Width"): "IFCLENGTHMEASURE",

    ("Pset_Photometric", "RatedLuminousFlux"): "IFCLUMINOUSFLUXMEASURE",
    ("Pset_Photometric", "LuminousEfficacy"): "IFCRATIOMEASURE",
    ("Pset_Photometric", "CorrelatedColorTemperature"): "IFCTHERMODYNAMICTEMPERATUREMEASURE",
}

# Optional value normalization rules (only if you want them)
def normalize_value(pset: str, prop: str, raw):
    """
    Return possibly-normalized value (Python primitive: float/int/str) or raw.
    """
    if raw is None:
        return None

    # IP rating: many exports store "20" instead of "IP20"
    if pset == "Pset_MechanicalAndInstallation" and prop == "IPRating":
        s = str(raw).strip()
        if s.isdigit():
            return f"IP{s}"
        # handle already like "IP20"
        return s.upper().replace(" ", "")

    # MountingType: normalize to your controlled vocab if needed
    if pset == "Pset_MechanicalAndInstallation" and prop == "MountingType":
        return str(raw).strip().lower()

    return raw


def unwrap_nominal_value(nv) -> Optional[object]:
    """
    Convert IFC nominal value to a Python primitive.
    nv is an IfcOpenShell entity_instance for simple types (e.g., IfcReal, IfcLabel).
    """
    if nv is None:
        return None
    try:
        # In IfcOpenShell, simple types often behave like nv.wrappedValue
        if hasattr(nv, "wrappedValue"):
            return nv.wrappedValue
    except Exception:
        pass

    # Fallback: string representation
    return str(nv)


def make_simple_value(ifc, ifc_type: str, py_value):
    """
    Create a new IFC simple-typed value (e.g. IfcLengthMeasure(123.0)).
    """
    t = ifc_type.upper()

    # Labels/text types need strings
    if t in ("IFCLABEL", "IFCTEXT", "IFCIDENTIFIER"):
        return ifc.create_entity(t, str(py_value))

    # Numbers: try float (covers measures, ratio, etc.)
    try:
        num = float(py_value)
    except Exception:
        # If it cannot be numeric but target is numeric, keep original as string to avoid crash
        num = None

    if num is None:
        # last resort: store as label
        return ifc.create_entity("IFCLABEL", str(py_value))

    return ifc.create_entity(t, num)


def patch_psets(ifc):
    """
    Patch IfcPropertySet.HasProperties values according to TARGET_TYPES.
    Returns a list of (pset, prop, beforeType, afterType, beforeValue, afterValue).
    """
    changes = []

    # Iterate property sets
    for pset in ifc.by_type("IfcPropertySet"):
        pset_name = (pset.Name or "").strip()
        if not pset_name:
            continue

        # skip if pset not in  mapping
        relevant = [k for k in TARGET_TYPES.keys() if k[0] == pset_name]
        if not relevant:
            continue

        for prop in getattr(pset, "HasProperties", []) or []:
            prop_name = (prop.Name or "").strip()
            key = (pset_name, prop_name)
            if key not in TARGET_TYPES:
                continue

            target_type = TARGET_TYPES[key].upper()

            #  handle only IfcPropertySingleValue here 

            if prop.is_a("IfcPropertySingleValue"):
                before_nv = prop.NominalValue
                before_type = before_nv.is_a() if before_nv else None
                before_val = unwrap_nominal_value(before_nv)

                # normalize (optional)
                after_val = normalize_value(pset_name, prop_name, before_val)

                # create new typed nominal value
                new_nv = make_simple_value(ifc, target_type, after_val)

                # apply
                prop.NominalValue = new_nv

                changes.append(
                    (pset_name, prop_name, before_type, target_type, before_val, after_val)
                )
            else:
                # If it is not SingleValue, skip it safely.
                changes.append((pset_name, prop_name, prop.is_a(), "SKIPPED", None, None))

    return changes


def main():
    if len(sys.argv) < 3:
        raise SystemExit(
            "Usage:\n"
            "  python patch_ifc_psets.py input.ifc output.ifc\n"
        )

    in_path = sys.argv[1]
    out_path = sys.argv[2]

    ifc = ifcopenshell.open(in_path)
    changes = patch_psets(ifc)
    ifc.write(out_path)

    # Print summary
    print(f"Patched IFC written to: {out_path}")
    print("Changes:")
    for c in changes:
        pset, prop, bt, at, bv, av = c
        if at == "SKIPPED":
            print(f"  - {pset}.{prop}: skipped (property type {bt})")
        else:
            print(f"  - {pset}.{prop}: {bt}({bv}) -> {at}({av})")


if __name__ == "__main__":
    main()
