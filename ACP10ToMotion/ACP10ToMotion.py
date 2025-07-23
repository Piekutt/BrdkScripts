import os
import re
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom

# --- Adjust these paths based on your project ---
# PROJECT_ROOT = os.path.dirname(__file__)
project_root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
HW_DIR = os.path.join(project_root, "Physical", "1CP")
PLC_DIR = os.path.join(HW_DIR, "PLC")
AXFILE_DIR = os.path.join(project_root, "Logical", "Motion", "objects")
NCM_FILE = os.path.join(PLC_DIR, "Motion", "Acp10map.ncm")
AXIS_FILE = os.path.join(PLC_DIR, "mappMotion", "Axis.axis")
HW_FILE = os.path.join(HW_DIR, "Hardware.hw")
OUTPUT_AXIS_FILE = os.path.join(PLC_DIR, "mappMotion", "Axis_updated.axis")
OUTPUT_HW_FILE = os.path.join(HW_DIR, "Hardware_updated.hw")
# ------------------------------------------------

ET.register_namespace('', "http://br-automation.co.at/AS/Hardware")

def clean_name(name):
    return re.sub(r"[\[\]]", "", name)

def pretty_xml(elem, preamble=None):
    rough = ET.tostring(elem, 'utf-8')
    parsed = minidom.parseString(rough)
    pretty = parsed.toprettyxml(indent="  ")

    clean_lines = [line for line in pretty.splitlines() if line.strip()]
    if preamble:
        return f"{preamble}\n" + "\n".join(clean_lines[1:])
    return "\n".join(clean_lines)

def extract_relevant_ax_parameters(ax_path):
    tree = ET.parse(ax_path)
    root = tree.getroot()
    params = []
    rename_map = {
        "t_jolt": "JerkTime",
        "kv": "ProportionalGain",
        "t_total": "TotalDelayTime",
        "t_predict": "PredictionTime",
        "a": "Acceleration",
        "v_switch": "StartVelocity",
        "v_trigger": "HomingVelocity",
        "mode": "Mode",
        "type": "LoopFilter1",
        "a0": "CenterFrequency",
        "a1": "Bandwidth",
        "units": "ReferenceDistance",
        "rev_motor": "Input",
        "edge_sw": "SwitchEdge",
        "start_dir": "StartDirection",
        "trigg_dir": "HomingDirection",
        "fix_dir": "KeepDirection",
    }
    rename_val_map={
        "ncABS_SWITCH": "AbsoluteSwitch",
        "ncSWITCH_GATE": "SwitchGate",
        "ncNOTCH": "Notch",
        "ncNEGATIVE": "Negative"
    }
    skip_values = {"0.0", "0", "ncOFF", "ncSTANDARD", "ncLINEAR + ncCORRECTION", "ncMOTOR_PAR", "ncPOSITIVE", "ncPOSITION", "ncDIRECT"}
    skip_params = {"p_max", "fn", "speed_kv", "t_filt", "a_max", "encoder_res", "encoder_type", "i_max", "n_max", "count_dir"}

    for group in root.findall(".//Group"):
        group_name = group.attrib.get("ID", "").lower()
        if group_name in ["position", "speed", "homing", "limit", "encoder_if"]:
            for param in group.findall(".//Parameter"):
                pid = param.attrib.get("ID")
                val = param.attrib.get("Value")
                if val in rename_val_map:
                    val = rename_val_map[val]
                if pid in skip_params or val in skip_values:
                    continue
                if group_name == "limit" and pid != "t_jolt":
                    continue
                pid = rename_map.get(pid, pid)
                params.append((pid, val, group_name))
    return params

def extract_axis_parameters(ax_path):
    tree = ET.parse(ax_path)
    root = tree.getroot()
    result = {}

    cd = root.find(".//Parameter[@ID='count_dir']")
    result["CountDirection"] = "Inverse" if cd is not None and "INV" in cd.attrib["Value"].upper() else "Standard"

    for pid, key in [("v_pos", "Velocity"), ("a_pos", "Acceleration"), ("d_pos", "Deceleration")]:
        p = root.find(f".//Parameter[@ID='{pid}']")
        result[key] = p.attrib["Value"] if p is not None else "1.0E+07"

    return result

def index_ax_files(root_path):
    ax_files = {}
    for dirpath, _, filenames in os.walk(root_path):
        for fname in filenames:
            if fname.lower().endswith(".ax"):
                base = os.path.splitext(fname)[0].lower()
                ax_files[base] = os.path.join(dirpath, fname)
    return ax_files

def get_namespace(element):
    m = re.match(r'\{.*\}', element.tag)
    return m.group(0) if m else ''

def main():
    # Check if valid project path
    if not os.path.exists(project_root):
        print(f"Error: The provided project path does not exist: {project_root}")
        print("\nEnsure the path is correct and the project folder exists.")
        print("\nIf the path contains spaces, make sure to wrap it in quotes, like this:")
        print('   python ACP10ToMotion.py "C:\\path\\to\\your\\project"')
        sys.exit(1)


    ax_files = index_ax_files(AXFILE_DIR)

    axis_tree = ET.parse(AXIS_FILE)
    axis_root = axis_tree.getroot()
    hw_tree = ET.parse(HW_FILE)
    hw_root = hw_tree.getroot()
    ncm_root = ET.parse(NCM_FILE).getroot()

    namespace = get_namespace(hw_root)
    ax_count = 0

    for nc in ncm_root.findall(".//NcObject"):
        if nc.attrib.get("Disabled", "FALSE").upper() == "TRUE":
            continue

        name = nc.attrib.get("Name")
        axis_id = clean_name(name)
        init_param = nc.attrib.get("InitParameter")
        module_id = nc.attrib.get("ModuleId")
        channel = nc.attrib.get("Channel", "1")

        elem = ET.Element("Element", ID=axis_id, Type="axis")

        if not init_param:
            print(f"ℹ️  Adding axis '{axis_id}' without InitParameter")
            axis_root.append(elem)
            ax_count += 1
            continue

        ax_path = None
        for ax_name, path in ax_files.items():
            if ax_name.startswith(init_param.lower()):
                ax_path = path
                break

        if not ax_path:
            print(f"⚠️  No .ax file found for InitParameter='{init_param}' (needed for '{name}')")
            continue

        axis_params = extract_axis_parameters(ax_path)
        base = ET.SubElement(elem, "Selector", ID="BaseType")
        ET.SubElement(base, "Property", ID="CountDirection", Value=axis_params["CountDirection"])

        limits = ET.SubElement(elem, "Selector", ID="MovementLimits")
        for key in ("Velocity", "Acceleration", "Deceleration"):
            sel = ET.SubElement(limits, "Selector", ID=key)
            ET.SubElement(sel, "Property", ID=key, Value=axis_params[key])

        axis_root.append(elem)
        print(f"✅ Added axis '{axis_id}' using {os.path.basename(ax_path)}")
        ax_count += 1

        module = hw_root.find(f".//{namespace}Module[@Name='{module_id}']")
        if module is None:
            print(f"⚠️  Module '{module_id}' not found in Hardware.hw")
            continue

        # Prefix path if module type matches
        module_type = module.attrib.get("Type", "")
        chan_path = f"DriveConfiguration/Channel[{channel}]/RealAxis"
        if module_type in ["80SD100XS.C04X-01", "80SD100XD.C044-01"]:
            chan_path = f"FunctionModel/DriveConfiguration/Channel[{channel}]/RealAxis"

        hw_params = extract_relevant_ax_parameters(ax_path)

        # Add AxisReference line
        axis_ref = ET.Element("Parameter", ID="AxisReference", Location=chan_path, Value=axis_id)
        module.append(axis_ref)
        # adding the encoder
        if module_type == "8EIxxxHxS1x.xxxx-1": # 1 axis servo
            module.append(ET.Element("Parameter", ID="InterfaceType", Location="DriveConfiguration/Encoder/EncoderX41", Value="EnDat" )) 
        elif module_type == "80SD100XS.C04X-01": # 1 axis stepper
            module.append(ET.Element("Parameter", ID="InterfaceType", Location="FunctionModel/DriveConfiguration/Encoder/EncoderX6", Value="Incremental" ))
        elif module_type == "80SD100XD.C044-01": # 2 axis stepper
            module.append(ET.Element("Parameter", ID="InterfaceType", Location="FunctionModel/DriveConfiguration/Encoder/EncoderX6A", Value="Incremental" ))
            module.append(ET.Element("Parameter", ID="InterfaceType", Location="FunctionModel/DriveConfiguration/Encoder/EncoderX6B", Value="Incremental" ))
        elif module_type == "8EI8X8HWT10.xxxx-1": # 3 axis servo
            module.append(ET.Element("Parameter", ID="InterfaceType", Location="DriveConfiguration/Encoder/EncoderX41", Value="EnDat" ))
            module.append(ET.Element("Parameter", ID="InterfaceType", Location="DriveConfiguration/Encoder/EncoderX42", Value="EnDat" ))
            module.append(ET.Element("Parameter", ID="InterfaceType", Location="DriveConfiguration/Encoder/EncoderX43", Value="EnDat" ))

        sorted_hw_params = sorted(hw_params, key=lambda p: (p[2] != "homing" or p[0] != "Mode",))

        for pid, val, group in sorted_hw_params:
            for ex in list(module.findall(f".//{namespace}Parameter")):
                if ex.attrib.get("ID") == pid:
                    loc = ex.attrib.get("Location", "")
                    if loc == chan_path or loc.startswith(f"{chan_path}/"):
                        module.remove(ex)

            if group == "position" and pid in ("ProportionalGain", "PredictionTime", "TotalDelayTime"):
                location = chan_path + "/Controller/Mode/Position"
            elif group == "speed" and pid in ("ProportionalGain", "PredictionTime", "TotalDelayTime"):
                location = chan_path + "/Controller/Mode/Speed"
            elif group == "speed" and pid in ("CenterFrequency", "Bandwidth"):
                location = chan_path + "/Controller/Mode/LoopFilters/LoopFilter1"
            elif pid == "LoopFilter1":
                location = chan_path + "/Controller/Mode/LoopFilters"
            elif pid == "Mode":
                location = chan_path + "/Homing"
            elif group == "homing":
                location = chan_path + "/Homing/Mode"
            elif pid == "JerkTime":
                location = chan_path + "/JerkFilter"
            elif pid == "ReferenceDistance":
                location = chan_path + "/MechanicalElements/RotaryToLinearTransformation"
            elif group == "encoder_if":
                location = chan_path + "/MechanicalElements/Gearbox"
            else:
                location = chan_path

            if pid == "JerkTime":
                module.append(ET.Element("Parameter", ID="JerkFilter", Location=chan_path, Value="Used"))

            param_elem = ET.Element("Parameter", ID=pid, Location=location, Value=val)
            module.append(param_elem)

    with open(OUTPUT_AXIS_FILE, "w", encoding="utf-8") as f:
        f.write(pretty_xml(axis_root))

    print(f"\n🎉 Axis output saved to {OUTPUT_AXIS_FILE}")
    print(f"Added {ax_count} number of axes")

    hw_preamble = '<?xml version="1.0" encoding="utf-8"?>\n<?AutomationStudio WorkingVersion="6.1" FileVersion="4.9"?>'
    with open(OUTPUT_HW_FILE, "w", encoding="utf-8") as f:
        f.write(pretty_xml(hw_root, preamble=hw_preamble))

    print(f"🎉 Hardware output saved to {OUTPUT_HW_FILE}")

if __name__ == "__main__":
    main()
