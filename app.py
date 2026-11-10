import streamlit as st

from kbyg.ui import require_password


st.set_page_config(page_title="Know Before You Go SG", page_icon="🌺", layout="wide")
require_password()

navigation = st.navigation(
    [
        st.Page("pages/0_Start_Here.py", title="Start Here", icon="🏠", default=True),
        st.Page("pages/1_Plan_My_Outing.py", title="Plan My Outing", icon="🗺️", url_path="plan-my-outing"),
        st.Page(
            "pages/2_Explore_Heritage_Places.py",
            title="Explore Heritage Places",
            icon="🔎",
            url_path="explore-heritage-places",
        ),
        st.Page("pages/4_About_Us.py", title="About Us", icon="🌺", url_path="about-us"),
        st.Page("pages/5_Methodology.py", title="Methodology", icon="📚", url_path="methodology"),
    ]
)
navigation.run()

