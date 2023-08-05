import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import json
import os
import io

st.set_option('deprecation.showPyplotGlobalUse', False)

st.set_page_config(
    page_title="EspressoIn Tools",
    page_icon="assets/icon/logo.ico",
    # layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.maulanaibrohim.github.io/espressoin',
        'Report a bug': "https://github.com/maulanaibrohim/espressoin-tools/issues/new/choose",
        # 'About': "# This is a header. This is an *extremely* cool app!"
    }
)


def calculate_band_gap(energy_values):
    lowest_positive_point = None
    highest_negative_point = None
    for energy in energy_values:
        if energy > 0:
            if lowest_positive_point is None or energy < lowest_positive_point:
                lowest_positive_point = energy
        elif energy < 0:
            if highest_negative_point is None or energy > highest_negative_point:
                highest_negative_point = energy
    band_gap = abs(highest_negative_point - lowest_positive_point)

    return band_gap, highest_negative_point, lowest_positive_point

def plot_band_structure(data, fermi_energy, color, high_symmetry_points=None, dpi=300, y_axis_increment=2, title="Band Structure", x_label="k-points", y_label="Energy (eV)", show_band_gap=True, grid_on=True, line_thickness=1.0, marker_color="#FF0003", marker_size=50, dash_line_color="#000000", dash_line_thickness=1.0):
    k_points = data[:, 0]
    energy_values = data[:, 1] - fermi_energy
    band_gap, highest_negative_point, lowest_positive_point = calculate_band_gap(energy_values)

    k_indices = np.where(k_points == 0)[0]
    k_labels = list(high_symmetry_points.values()) if high_symmetry_points else None

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axhline(0, color=dash_line_color, linestyle='dashed', linewidth=dash_line_thickness)
    ax.set_xticks(list(high_symmetry_points.keys())) if k_labels else None
    ax.set_xticklabels(k_labels) if k_labels else None
    for idx in range(len(k_indices) - 1):
        start, end = k_indices[idx], k_indices[idx + 1]
        ax.plot(k_points[start:end], energy_values[start:end], color=color, linewidth=line_thickness)

    mark_points = [highest_negative_point, lowest_positive_point]
    indices = [i for i, y in enumerate(energy_values) if y in mark_points]
    ax.scatter([k_points[i] for i in indices], [energy_values[i] for i in indices], marker='o', s=marker_size, color=marker_color)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    if show_band_gap:
        title_text = ax.set_title(title + f"\nBand Gap = {band_gap:.2f} eV")
    else:
        title_text = ax.set_title(title)

    ax.grid(grid_on)

    interval = y_axis_increment
    y_min, y_max = plt.ylim()
    min_y = interval * (y_min // interval)
    max_y = interval * (y_max // interval) + interval
    ticks = [i for i in range(int(min_y), int(max_y + interval), interval)]

    plt.yticks(ticks)
    plt.xlim(0, max(k_points)) 

    plt.tight_layout()

    return plt

def max_min_energy(data):
    energy_values = data[:, 1] 
    return np.min(energy_values), np.max(energy_values)

def main():
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("assets/logo.png", width=90)

    with col2:
        web_name_url = "https://www.maulanaibrohim.github.io/espressoin" 
        web_name = "EspressoIn - Tools"  
        web_name_html = f'<div style="display: flex; align-items: center;"><a href="{web_name_url}" target="_blank" style="text-decoration: none; color: #0078FF;"><h1>{web_name}</h1></a></div>'
        st.markdown(web_name_html, unsafe_allow_html=True)
    
    st.write("---")

    assets_folder = os.path.join(os.path.dirname(__file__), "assets/lang")

    with col1:
        st.sidebar.image("assets/logo.png", width=60)

    with col2:
        web_name_url = "https://www.maulanaibrohim.github.io/espressoin" 
        web_name = "EspressoIn - Tools" 
        web_name_html = f'<div style="display: flex; align-items: center;"><a href="{web_name_url}" target="_blank" style="text-decoration: none; color: #0078FF;"><h1>{web_name}</h1></a></div>'
        st.sidebar.markdown(web_name_html, unsafe_allow_html=True)
    
    st.sidebar.write("---")

    language = st.sidebar.selectbox("Select Language", ["English", "German", "Bahasa Indonesia"])
    if language == "English":
        json_file_path = os.path.join(assets_folder, "text_en.json")
    elif language == "German":
        json_file_path = os.path.join(assets_folder, "text_de.json")
    else:
        json_file_path = os.path.join(assets_folder, "text_id.json")

    with open(json_file_path, "r", encoding='utf-8') as file:
        texts = json.load(file)

    st.sidebar.write("---")

    st.sidebar.header(texts["settings_header"])
    st.sidebar.caption(texts["upload_data_label"])

    with st.expander(texts["how_to_label"]):
        st.markdown(texts["how_to_instructions"])

        if st.button(texts["download_sample_file_button"]):
            file_path = "assets/sample/sample.dat" 
            if os.path.exists(file_path):
                with open(file_path, "rb") as file:
                    file_content = file.read()
                st.download_button(label=texts["download_button_click"], data=file_content, file_name="sample.dat", mime="application/octet-stream")
            else:
                st.warning(texts["downlaod_error_message"])

    
    st.write("---")
    
    file = st.file_uploader(texts["upload_data_label"], type=["dat", "gnu"])


    if file is not None:
        data = np.loadtxt(file)
        min_energy, max_energy = max_min_energy(data)

        with st.sidebar.expander(texts["data_setting_label"]):
            fermi_energy = st.number_input((texts["fermi_energy_label"]), value=0.0, step=0.5,help=(texts["fermi_energy_help"]), max_value=max_energy, min_value=min_energy)
            high_symmetry_points = {}
            num_points = st.number_input((texts["num_points_label"]), value=0, step=1,help=(texts["num_points_help"]))
            predefined_labels = [(texts["custom_label"]), "Γ", "M", "R", "X", "K", "L", "U", "W", "H", "N", "P", "A"]
            for i in range(num_points):
                selected_label = st.selectbox(f"{(texts['selected_label_label'])} {i+1}", predefined_labels)
                custom_label = st.text_input(f"{(texts)['custom_label_label']} {i+1} :red[{(texts['custom_label_info'])}]", "")
                k_value = st.number_input(f"{(texts['k_value_label'])} {i+1}", min_value=0.0, value=0.00001, step=0.01, help=(texts["k_value_help"]))
                label = custom_label if custom_label else selected_label
                if label and k_value:
                    high_symmetry_points[k_value] = label

        with st.sidebar.expander(texts["plot_customization_label"]):
            show_band_gap = st.checkbox((texts["show_band_gap_label"]), value=False, help=(texts["show_band_gap_help"]))
            grid_on = st.checkbox(texts["plot_grid_label"], value=True, help=texts["plot_grid_help"])
            color = st.color_picker((texts["color_label"]), "#FF0003", help=(texts["color_help"]))
            line_thickness = st.slider(texts["plot_line_thickness_label"], min_value=0.25, max_value=5.0, value=1.0, step=0.25, help=texts["plot_line_thickness_help"])
            marker_color = st.color_picker(texts["dot_marker_color_label"], "#FF0003", help=texts["dot_marker_color_help"])
            marker_size = st.slider(texts["dot_marker_size_label"], min_value=0, max_value=150, value=50, step=1, help=texts["dot_marker_size_help"])
            dash_line_color = st.color_picker(texts["dash_line_color_label"], "#000000", help=texts["dash_line_color_help"])
            dash_line_thickness = st.slider(texts["dash_line_thickness_label"], min_value=0.25, max_value=5.0, value=1.0, step=0.25, help=texts["dash_line_thickness_help"])
            y_axis_increment = st.number_input((texts["y_axis_increment_label"]), value=2, help=(texts["y_axis_increment_help"]))

            title = st.text_input((texts["title_label"]), (texts["title_sample"]), help=(texts["title_help"]))
            x_label = st.text_input((texts["x_label_label"]), (texts["x_label_sample"]), help=(texts["x_label_help"]))
            y_label = st.text_input((texts["y_label_label"]), (texts["y_label_sample"]), help=(texts["y_label_help"]))
            
        with st.sidebar.expander(texts["download_settings_label"]):
            dpi = st.number_input((texts["dpi_label"]), value=300, min_value=150, max_value=1200, step=10, help=(texts["dpi_help"]))
            # st.write((texts["choose_format_label"]))
            download_format = st.selectbox((texts["choose_format_label"]), ["jpg", "png", "tiff", "svg"])
            custom_file_name = st.text_input((texts['custom_file_name_label']), "")

        st.write(f"\n**{(texts['preview_label'])}**")
        plot = plot_band_structure(data, fermi_energy, color, high_symmetry_points, dpi, y_axis_increment, title, x_label, y_label, show_band_gap, grid_on, line_thickness, marker_color, marker_size, dash_line_color, dash_line_thickness)
        st.pyplot(plot, dpi=dpi)


        if st.button((texts["download_plot_label"])):
            buffer = io.BytesIO()

            if custom_file_name.strip():
                file_name = f"{custom_file_name.strip()}.{download_format}"
            else:
                file_name = f"{title}.{download_format}"

            plot.savefig(buffer, format=download_format, dpi=dpi)
            plot.close()
            st.download_button(label=f"{(texts['download_as'])} {download_format.upper()}", data=buffer.getvalue(), file_name=file_name)

if __name__ == "__main__":
    main()