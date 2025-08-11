import plotly.io as pio
import streamlit as st


def download_plot(fig, label="", filename="image"):
    st.download_button(
        label=f"Download {label} plot",
        data=pio.to_image(fig, format="svg"),
        file_name=f"{filename}.svg",
        mime="/image/svg"
    )


def download_longitudinal_plot(fig, label="", filename="image"):
    st.download_button(
        label=f"Download {label} plot",
        data=pio.to_image(fig, format="svg", width=1600, height=600),
        file_name=f"{filename}.svg",
        mime="/image/svg"
    )
