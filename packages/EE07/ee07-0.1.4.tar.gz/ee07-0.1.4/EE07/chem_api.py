import requests

PUBCHEM_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

def handle_chemical_function(func_str):
    try:
        if func_str.startswith("structure("):
            compound = _extract_param(func_str)
            return get_structure_info(compound)
        elif func_str.startswith("geometry("):
            compound = _extract_param(func_str)
            return f"📐 Geometry lookup for {compound} (3D conformer request pending implementation)"
        elif func_str.startswith("orbital("):
            compound = _extract_param(func_str)
            return f"🌀 Orbital query for {compound} (s, p, d, f assignment)"
        elif func_str.startswith("hybrid("):
            compound = _extract_param(func_str)
            return f"🔗 Hybridization check for {compound}"
        elif func_str.startswith("isomer("):
            compound = _extract_param(func_str)
            return f"🧬 Isomer types for {compound}: structural/stereo info TBD"
        elif func_str.startswith("react("):
            reagents = _extract_list(func_str)
            return simulate_reaction(reagents)
        elif func_str.startswith("oxidize("):
            compound = _extract_param(func_str)
            return f"🧪 Oxidizing {compound} — Redox pair search"
        elif func_str.startswith("reduce("):
            compound = _extract_param(func_str)
            return f"🧪 Reducing {compound} — Electron gain simulated"
        elif func_str.startswith("redox("):
            pair = _extract_list(func_str)
            return f"🔁 Redox system: {' <-> '.join(pair)}"
        elif func_str.startswith("half_rxn("):
            compound = _extract_param(func_str)
            return f"⚗️ Half-reaction breakdown for {compound}"
        elif func_str.startswith("mass("):
            compound = _extract_param(func_str)
            return get_mass(compound)
        elif func_str.startswith("moles("):
            args = _extract_list(func_str)
            return calculate_moles(*args)
        elif func_str.startswith("limiting("):
            reactants = _extract_list(func_str)
            return f"🧮 Limiting reagent analysis: {', '.join(reactants)}"
        elif func_str.startswith("excess("):
            reactants = _extract_list(func_str)
            return f"📊 Excess reagent among: {', '.join(reactants)}"
        elif func_str.startswith("balance("):
            reaction = _extract_param(func_str)
            return f"⚖️ Balancing reaction: {reaction}"
        elif func_str.startswith("bind("):
            target = _extract_param(func_str)
            return f"🔗 Binding process initiated for: {target}"
        elif func_str.startswith("trig("):
            val = _extract_param(func_str)
            return f"⚙️ Trigger applied with: {val}"
        elif func_str.startswith("release("):
            compound = _extract_param(func_str)
            return f"💊 Releasing compound: {compound}"
        elif func_str.startswith("delay("):
            seconds = _extract_param(func_str)
            return f"⏳ Delay applied: {seconds} sec"
        elif func_str.startswith("save("):
            item = _extract_param(func_str)
            return f"💾 Saved log for: {item}"
        elif func_str.startswith("adsorb("):
            target = _extract_param(func_str)
            return f"🌐 Adsorption event at surface for: {target}"
        elif func_str.startswith("absorb("):
            compound = _extract_param(func_str)
            return f"🌊 Absorbed compound: {compound}"
        elif func_str.startswith("gel("):
            mat = _extract_param(func_str)
            return f"🧫 Gel matrix activated using: {mat}"
        elif func_str.startswith("interface("):
            comp = _extract_param(func_str)
            return f"🌉 Interface initiated at: {comp}"
        elif func_str.startswith("l1(") or func_str.startswith("l2(") or func_str.startswith("l3("):
            level = func_str.split("(")[0]
            return f"📂 Layer defined: {level}"
        elif func_str.startswith("h1(") or func_str.startswith("h2(") or func_str.startswith("h3("):
            hierarchy = func_str.split("(")[0]
            return f"🏗️ Hierarchy initiated: {hierarchy}"
        elif func_str.startswith("toxicity("):
            compound = _extract_param(func_str)
            return f"☣️ Checking toxicity for: {compound}"
        elif func_str.startswith("hazard("):
            compound = _extract_param(func_str)
            return f"⚠️ Hazard details for: {compound}"
        else:
            return f"⚠️ Unknown EEL chemical function: {func_str}"
    except Exception as e:
        return f"❌ Error: {func_str} — {e}"

def _extract_param(code):
    return code.split("(", 1)[1].split(")", 1)[0].strip('"\' ')

def _extract_list(code):
    return [x.strip('"\' ') for x in code.split("(", 1)[1].split(")", 1)[0].split(",")]

def get_structure_info(compound):
    url = f"{PUBCHEM_BASE}/compound/name/{compound}/property/MolecularFormula,MolecularWeight,IUPACName/JSON"
    res = requests.get(url)
    if res.status_code != 200:
        return f"🔍 No data found for '{compound}'"
    data = res.json()["PropertyTable"]["Properties"][0]
    return f"""
🧬 Compound: {compound}
- Formula: {data['MolecularFormula']}
- Weight: {data['MolecularWeight']}
- IUPAC: {data['IUPACName']}
"""

def simulate_reaction(reagents):
    if len(reagents) < 2:
        return "⚠️ react() requires at least two reagents"
    return f"🔬 Simulating: {' + '.join(reagents)} → Products (PubChem-based)"

def get_mass(compound):
    url = f"{PUBCHEM_BASE}/compound/name/{compound}/property/MolecularWeight/JSON"
    res = requests.get(url)
    if res.status_code != 200:
        return f"⚖️ Mass not found for '{compound}'"
    weight = res.json()["PropertyTable"]["Properties"][0]["MolecularWeight"]
    return f"⚖️ Molecular mass of {compound}: {weight} g/mol"

def calculate_moles(mass_str, compound):
    try:
        mass = float(mass_str)
        url = f"{PUBCHEM_BASE}/compound/name/{compound}/property/MolecularWeight/JSON"
        res = requests.get(url)
        if res.status_code != 200:
            return f"⚖️ Molar mass not found for '{compound}'"
        molar_mass = res.json()["PropertyTable"]["Properties"][0]["MolecularWeight"]
        moles = mass / molar_mass
        return f"🔢 Moles of {compound} in {mass} g: {moles:.4f} mol"
    except Exception as e:
        return f"❌ Moles calculation error: {e}"
