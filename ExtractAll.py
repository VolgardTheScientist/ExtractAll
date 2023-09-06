import streamlit as st
import ifcopenshell
import ifcopenshell.util
from ifcopenshell.util.selector import Selector
import ifcopenshell.util.placement 
import ifcopenshell.api
import numpy as np
import tempfile
from vendor import ifcpatch
import os
import time
import sys
sys.path.append('./vendor')

def move_to_origin(ifc_file, guid):
    part = ifc_file.by_guid(guid)
    old_matrix = ifcopenshell.util.placement.get_local_placement(part.ObjectPlacement)
    # st.write(old_matrix)
    new_matrix = np.eye(4)
    # st.write(new_matrix)
    ifcopenshell.api.run("geometry.edit_object_placement", ifc_file, product=part, matrix=new_matrix)

    # Save the modified IFC file to a temporary location and return the path
    # output_path = tempfile.mktemp(suffix=".ifc")
    # ifc_file.write(output_path)
    return ifc_file

def extract_and_save_element(ifc_file, guid, save_dir):
    extracted_ifc = ifcpatch.execute({"input": ifc_file, "file": ifc_file, "recipe": "ExtractElements", "arguments": [f"{guid}"]})
    extracted_ifc = move_to_origin(extracted_ifc, guid)
    temp_file_path = os.path.join(save_dir, f"{guid}.ifc")
    extracted_ifc.write(temp_file_path)

save_dir = "C:\\Users\\pp\\Downloads\\Extracted"

st.title('BIMease: extract all products')

st.markdown("""
This app will extract all products from your IFC file and save these as independent IFC files
""")

uploaded_file = st.file_uploader("Choose an IFC file", type=['ifc'])


if uploaded_file:
    with st.spinner("Your products are being extracted..."):
        time.sleep(2)
        tfile = tempfile.NamedTemporaryFile(delete=False) 
        tfile.write(uploaded_file.read())
        temp_path = tfile.name
        ifc = ifcopenshell.open(tfile.name)
        # selector = Selector()

        # Create a set to store unique IfcElement types in the file
        unique_element_types = set()

        # Get all IfcElement instances and populate the set with their types
        all_elements = ifc.by_type("IfcElement")
        for elem in all_elements:
            unique_element_types.add(elem.is_a())

        # Loop through each unique IfcElement type to extract and save elements
        for element_type in unique_element_types:
            elements = ifc.by_type(element_type)
            for element in elements:
                guid = element.GlobalId
                extract_and_save_element(ifc, guid, save_dir)

        st.write(f"All elements have been extracted and saved.")