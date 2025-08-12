from .functions import get_list_of_all_project_infos, get_recent_project
from ._backend_calls import _backend_GET
import streamlit as st
import warnings
from deprecated import deprecated

@deprecated(reason="This function is deprecated. Please use st_project_selector() instead.", category=DeprecationWarning)   
def load_project():
    warnings.warn("This function is deprecated. Please use st_project_selector() instead.", DeprecationWarning, stacklevel=2)
    return st_project_selector()

def st_project_selector(columns_sizes: [int, int, int, int] = [5, 1, 2, 2]):

    projects_simple_list = get_list_of_all_project_infos()

    col01, col02, col03, col04 = st.columns(columns_sizes)
    # with col01:
    #     st.title("Load or Create a new CubeSat project")
        # st.title(
        #     f"Summary of the System Generation for {st.session_state['project_name']}")

    with col02:
        if st.button("Get recent project"):
            (st.session_state["project_id"],
             st.session_state["project_name"],
             st.session_state["modified"]) = get_recent_project()
    with col03:
        # Let the user select a project from the list of projects in the project DB
        selected_project = st.selectbox("Project",
                                        projects_simple_list,
                                        index=None,
                                        placeholder="Select a project",
                                        format_func=lambda x: f"{x[1]}")
        if selected_project is not None:
            st.session_state["project_id"] = selected_project[0]
            st.session_state["project_name"] = selected_project[1]
    with col04:
        if 'project_id' not in st.session_state or st.session_state['project_id'] is None:
            st.metric(label="   ",
                  value="<-- Please select")
        else:
            st.metric(label=f"Active project ID: {st.session_state['project_id']}",
                      value=f"{st.session_state['project_name']}")

def st_generated_design_selector(columns_sizes: [int, int, int, int] = [5, 1, 2, 2]):
    """A function which adds a generated design selector to the top of the page.
    A generated design is the stored as part of the project in the backend.

    Suitable to be used in conjunction with st_project_selector().
    """
    # check if the project is set and exit without doing anything if not
    if 'project_id' not in st.session_state or st.session_state['project_id'] is None:
        return

    col01, col02, col03, col04 = st.columns(columns_sizes)

    # get the list of system generators for the current project
    status_code, system_generators = _backend_GET(f"/projects/{st.session_state['project_id']}/sysgen")

    # if successful display a selector for the system generators based on their IDs and names
    with col03:
        if status_code == 200:
            selected_sysgen = st.selectbox("System Generator",
                                                [(sysgen["id"], sysgen["description"])
                                                 for sysgen in system_generators],
                                                index=None,
                                                placeholder="Select a system generator",
                                                format_func=lambda x: f"{x[1]}")

            if selected_sysgen is not None:
                st.session_state["sysgen_id"] = int(selected_sysgen[0])
                st.session_state["sysgen_description"] = selected_sysgen[1]
        else:
            st.error(f"Error while loading system generators: {system_generators}")

    # After selecting a system generator, extract and present the generated designs from system_generators with the ID system_generators_id
    if 'sysgen_id' in st.session_state:
        status_code, system_generator = _backend_GET(f"/projects/{st.session_state['project_id']}/sysgen/{st.session_state['sysgen_id']}/")
        if status_code == 200:
            st.session_state["system_generator"] = system_generator
            st.session_state["generated_designs"] = system_generator.get("generated_designs")
        else:
            st.error(f"Error while loading generated designs: {system_generator}")

    # display the generated designs (comp_list_uids) in a selectbox
    with col04:
        # Only show design selector and warnings if a system generator has been selected
        if 'sysgen_id' in st.session_state:
            if 'generated_designs' in st.session_state and st.session_state["generated_designs"]:
                generated_designs = st.selectbox("Generated Design",
                                                 [(design["id"], design["comp_list_uids"])
                                                  for design in st.session_state["generated_designs"]],
                                                 index=None,
                                                 placeholder="Select a generated design",
                                                 format_func=lambda x: f"Design #{x[0]}, Components: {x[1]}")

                if generated_designs is not None:
                    st.session_state["generated_design_id"] = generated_designs[0]
                    st.session_state["generated_design_comp_list_uids"] = generated_designs[1]
            else:
                st.warning("No generated designs available for the selected system generator.")
    
    # display the selected system generator and generated design
    if 'sysgen_description' in st.session_state and 'generated_design_comp_list_uids' in st.session_state:
        st.metric(label=f"Selected System Generator (ID: {st.session_state['sysgen_id']})",
                  value=st.session_state["sysgen_description"])
        st.metric(label=f"Selected Generated Design (ID: {st.session_state['generated_design_id']})",
                  value=str(st.session_state["generated_design_comp_list_uids"]))
    elif 'sysgen_description' in st.session_state:
        st.metric(label="Selected System Generator",
                  value=st.session_state["sysgen_description"])