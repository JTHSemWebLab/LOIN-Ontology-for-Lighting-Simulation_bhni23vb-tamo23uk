#!/usr/bin/env python3
# ──────────────────────
# USER SETTINGS
# ──────────────────────
INPUT_XLSX = ""                 # leave empty to auto-pick first .xlsx next to script
SHEET_NAME = "IDS_FOR_LOIN"     # exact Excel sheet name
OUTPUT_XML = ""                # leave empty for auto-name

# ──────────────────────
# IMPORTS
# ──────────────────────
import re
import os, glob, argparse, pandas as pd
from xml.etree.ElementTree import Element, SubElement, tostring, register_namespace
from xml.dom import minidom

NS_IDS = "http://standards.buildingsmart.org/IDS"
NS_XS  = "http://www.w3.org/2001/XMLSchema"
register_namespace("", NS_IDS)
register_namespace("xs", NS_XS)

INFO_KEYS = {
    "Title":"title", "Copyright":"copyright", "Version":"version",
    "Description":"description", "Author":"author", "Date":"date",
    "Purpose":"purpose", "Milestone":"milestone",
}
SPEC_KEYS = {
    "Name":"name", "IfcVersion":"ifcVersion", "Identifier":"identifier",
    "Description":"description", "Instruction":"instructions"
}

# ──────────────────────
# HELPERS
# ──────────────────────
def _canon(s):
    return str(s).strip().lower().replace(" ", "") if s is not None else ""

def _find_pair(df, start_col, left, right):
    cols = list(df.columns)
    for i in range(start_col, len(cols)-1):
        if _canon(cols[i]) == left and _canon(cols[i+1]) == right:
            return i, i+1
    return None, None

def _kv(df, k_idx, v_idx):
    d = {}
    for _, r in df.iterrows():
        k = r.iloc[k_idx]
        v = r.iloc[v_idx]
        k = str(k).strip() if pd.notna(k) else ""
        v = str(v).strip() if pd.notna(v) else ""
        if k and v and k not in d:
            d[k] = v
    return d

def _pick_idx(columns, name):
    t = name.replace(" ", "").lower()
    for i, c in enumerate(columns):
        c_norm = str(c).replace(" ", "").lower()
        if c_norm == t or t in c_norm:
            return i
    return None

def _cell(r, base, idx):
    if idx is None:
        return ""
    try:
        v = r.iloc[base + idx]
    except IndexError:
        return ""
    return str(v).strip() if pd.notna(v) else ""

def _first_xlsx(folder):
    files = [f for f in glob.glob(os.path.join(folder, "*.xlsx"))
             if not os.path.basename(f).startswith("~$")]
    return files[0] if files else ""

# ──────────────────────
# LOAD EXCEL
# ──────────────────────
def load_df(xlsx_path, sheet_name):
    raw = pd.read_excel(xlsx_path, sheet_name=sheet_name,
                        engine="openpyxl", header=None)
    df = raw[list(raw.keys())[0]] if isinstance(raw, dict) else raw

    def canon(v):
        return str(v).strip().lower().replace("\n", " ") if pd.notna(v) else ""

    header_row = None
    for r in range(min(50, len(df))):
        for c in range(min(30, df.shape[1]) - 1):
            if canon(df.iat[r, c]) == "elements" and canon(df.iat[r, c+1]) == "values":
                header_row = r
                break
        if header_row is not None:
            break

    if header_row is None:
        raise SystemExit("❌ Could not find 'Elements | Values' header row")

    headers = [str(v).strip() if pd.notna(v) else "" for v in df.iloc[header_row]]
    df = df.iloc[header_row + 1:].reset_index(drop=True)
    df.columns = headers
    return df

# ──────────────────────
# BUILD IDS
# ──────────────────────
def build_ids(df):
    df.columns = [str(c).strip() for c in df.columns]

    iL, iR = _find_pair(df, 0, "elements", "values")
    sL, sR = _find_pair(df, iR+1, "element", "values")
    aL, aR = _find_pair(df, sR+1, "element", "values")

    if None in (iL, sL, aL):
        raise SystemExit("❌ Failed to detect INFO / SPEC / APPL blocks")

    req_cols = list(df.columns[aR+1:])
    base = aR + 1

    info = _kv(df, iL, iR)
    spec = _kv(df, sL, sR)
    appl = _kv(df, aL, aR)

    ids = Element("ids", {"version": "1.0.0"})

    # INFO
    info_el = SubElement(ids, "info")
    title = info.get("Title") or spec.get("Name") or "Specification"
    SubElement(info_el, "title").text = title
    for k, tag in INFO_KEYS.items():
        if k != "Title" and info.get(k):
            SubElement(info_el, tag).text = info[k]

    # SPECIFICATION
    specs_el = SubElement(ids, "specifications")
    sattrs = {}
    for k, attr in SPEC_KEYS.items():
        if spec.get(k):
            sattrs[attr] = spec[k]
    sattrs.setdefault("name", title)
    spec_el = SubElement(specs_el, "specification", sattrs)

    # APPLICABILITY
    appl_el = SubElement(spec_el, "applicability")
    ent_el = SubElement(appl_el, "entity")
    SubElement(SubElement(ent_el, "name"), "simpleValue").text = appl.get("Name", "IfcLightFixtureType")
    if appl.get("Predefined Type"):
        SubElement(SubElement(ent_el, "predefinedType"), "simpleValue").text = appl["Predefined Type"]

    # REQUIREMENTS
    req_el = SubElement(spec_el, "requirements")

    c_reqtype = _pick_idx(req_cols, "Requirement Type")
    c_uri     = _pick_idx(req_cols, "URI")
    c_card    = _pick_idx(req_cols, "Cardinality")
    c_instr   = _pick_idx(req_cols, "Instructions")
    c_pset    = _pick_idx(req_cols, "PropertySet")
    c_bname   = _pick_idx(req_cols, "BaseName")
    c_value   = _pick_idx(req_cols, "Value")
    c_dtype   = _pick_idx(req_cols, "dataType")
    c_enum    = _pick_idx(req_cols, "Enumeration Value")

    for _, r in df.iterrows():
        if _cell(r, base, c_reqtype).lower() != "property":
            continue

        attrs = {}
        for k, idx in [("cardinality", c_card), ("dataType", c_dtype),
                       ("uri", c_uri), ("instructions", c_instr)]:
            v = _cell(r, base, idx)
            if v:
                attrs[k] = v

        prop = SubElement(req_el, "property", attrs)

        SubElement(SubElement(prop, "propertySet"), "simpleValue").text = \
            _cell(r, base, c_pset) or "Pset_LightFixtureTypeCommon"
        SubElement(SubElement(prop, "baseName"), "simpleValue").text = \
            _cell(r, base, c_bname) or "Undefined"

        enum_raw = _cell(r, base, c_enum)
        lit_val  = _cell(r, base, c_value)

        if enum_raw:
            # Normalize any escaped newlines that may already exist
            enum_raw = enum_raw.replace("&#10;", "\n").replace("\\n", "\n")

            # Split on newline / semicolon / comma (covers most Excel patterns)
            items = [s.strip() for s in re.split(r"[;\n\r,]+", enum_raw) if s and s.strip()]

            v_el = SubElement(prop, "value")
            restr = SubElement(v_el, f"{{{NS_XS}}}restriction",
                            {"base": "xs:string"})


            for it in items:
                # Important: ensure NO newline remains in attribute value
                it = it.replace("\n", "").replace("\r", "").strip()
                if it:
                    SubElement(restr, f"{{{NS_XS}}}enumeration", {"value": it})


    return ids

# ──────────────────────
# MAIN
# ──────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx")
    ap.add_argument("--sheet")
    ap.add_argument("--out")
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    xlsx = args.xlsx or (os.path.join(here, INPUT_XLSX) if INPUT_XLSX else _first_xlsx(here))
    if not xlsx or not os.path.isfile(xlsx):
        raise SystemExit("❌ Excel file not found")

    sheet = args.sheet or SHEET_NAME
    df = load_df(xlsx, sheet)
    ids = build_ids(df)

    xml = minidom.parseString(tostring(ids, encoding="utf-8")) \
                  .toprettyxml(indent="  ", encoding="utf-8")

    out = args.out or (os.path.splitext(xlsx)[0] + "_IDS.xml")
    with open(out, "wb") as f:
        f.write(xml)

    print(f"✅ IDS written:\n{out}")

if __name__ == "__main__":
    main()
