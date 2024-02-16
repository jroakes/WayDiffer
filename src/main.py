"""Main application file for the Wayback Machine URL Comparison Tool."""

from typing import Union, Dict
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

try:
    from diff_data import get_available_dates, process_diff, save_file
except:
    from src.diff_data import get_available_dates, process_diff, save_file

import webbrowser


def list_available_dates(
    url: str, history_days: int
) -> Union[Dict[str, datetime], None]:
    """List available dates for a URL in the Wayback Machine.

    Parameters
    ----------
    url : str
        The URL to check for available dates.
    history_days : int
        The number of historical days to check for available dates.

    Returns
    -------
    Union[Dict[str, datetime], None]
        A dictionary of available dates and their corresponding datetime objects, or None if no dates are found.

    Raises
    ------
    Exception
        If an error occurs while retrieving the available dates.
    """

    try:
        available_dates = get_available_dates(url, history_days)
        if available_dates:
            return available_dates
        else:
            st.warning(
                "Failed to find available dates. Please check the URL and try again or try a longer date range."
            )
            return None
    except Exception as e:
        st.error(f"Error retrieving dates: {e}")
        return None


def main():
    """Main application function."""

    st.set_page_config(
        page_title="Waydiffer: Wayback Machine URL Comparison Tool",
        page_icon="🤖 💾",
        layout="wide",
    )

    st.title("🤖 💾 Waydiffer: Wayback Machine URL Comparison Tool")

    st.write(
        "**Waydiffer** allows you to compare the content of a URL from the Wayback Machine with its current version. You can also view the differences between two selected Wayback Machine snapshots."
    )

    expander = st.expander("More Info")

    waydiffer_description = """
    It utilizes the [diff_match_patch](https://github.com/google/diff-match-patch) library from Google for tracking differences in HTML, CSS, and JavaScript files between two selected snapshots.

    Features include:
    - Finding available dates for a URL in the Wayback Machine.
    - Diffing support for HTML, CSS, and JavaScript.
    - Auto-beautification of HTML, CSS, and JavaScript files.
    - Custom diff interface with line numbers for easy comparison.
    - Two viewing options: inline or in a new window.

    Note: ⚠️ Open in a new window does not work in Streamlit Hosted Apps.

    Access the source code [here](https://github.com/jroakes/WayDiffer).
    """

    expander.write(waydiffer_description)

    st.divider()

    if "historical_url_input" not in st.session_state:
        st.session_state["historical_url_input"] = ""

    if "current_url_input" not in st.session_state:
        st.session_state["current_url_input"] = ""

    if "url_input" not in st.session_state:
        st.session_state["url_input"] = ""

    st.header("Step 1: List Available Dates")

    with st.form("url_input_form"):
        url_input = st.text_input(
            "Enter URL", key="url_input", help="Enter the URL to compare"
        )
        history_days = st.number_input(
            "Enter number of historical days",
            min_value=10,
            value=30,
            step=10,
            key="history_days_input",
            help="Enter the number of historical days to check for available dates",
        )

        submitted = st.form_submit_button(
            "List Available Dates",
            type="primary",
        )

    if submitted and url_input:
        available_dates = list_available_dates(url_input, history_days)
        if available_dates:
            st.write("### Available dates:")
            for memento_url, datetime_obj in available_dates.items():

                col1, col2 = st.columns([2, 1])
                with col1:
                    # st.write(f"{memento_url} - {datetime_obj}")
                    st.link_button(
                        f"{memento_url} - {datetime_obj} ↗",
                        memento_url,
                        use_container_width=True,
                    )
                with col2:
                    btn_key = f"btn_{memento_url}"
                    if st.button(
                        "Use This Date",
                        key=btn_key,
                        type="primary",
                        on_click=lambda memento_url=memento_url: st.session_state.update(
                            {
                                "historical_url_input": memento_url,
                                "current_url_input": url_input,
                            }
                        ),
                    ):
                        pass

    st.write("")

    st.header("Step 2: Compare URLs")

    with st.form("diff_input_form"):
        current_url = st.text_input(
            "Enter current URL", key="current_url_input", help="Enter the current URL"
        )
        historical_url = st.text_input(
            "Enter historical URL",
            key="historical_url_input",
            help="Enter the historical URL",
        )
        view_option = st.radio(
            "Choose how to view the diff:",
            ("View inline", "Open in new window"),
            key="view_option_input",
            help="Choose how to view the diff.  Open in a new window does not work in Streamlit Hosted Apps.",
        )
        st.write("")

        diff_submitted = st.form_submit_button(
            "Run Comparison",
            type="primary",
        )

    if diff_submitted and current_url and historical_url:

        display_option = "inline" if view_option == "View inline" else "new window"

        with st.spinner("Processing diff..."):

            html = process_diff(historical_url, current_url)

            if html:

                if html == "SAME CONTENT":
                    st.success("The content is the same.  No diff to display.")
                elif display_option == "new window":
                    file_location = save_file(html)
                    webbrowser.open_new_tab(file_location)
                else:
                    st.write("")
                    st.header("Step 3: Enjoy the Diff!")
                    components.html(html, height=1000, scrolling=True)
            else:
                st.error("Failed to process diff. Please ensure the URLs are correct.")


if __name__ == "__main__":
    main()
