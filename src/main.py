import streamlit as st
import streamlit.components.v1 as components
from data import get_available_dates, process_diff, save_file
import webbrowser


def list_available_dates(url, history_days):
    try:
        available_dates = get_available_dates(url, history_days)
        if available_dates:
            return available_dates
        else:
            st.write("Failed to retrieve available dates.")
            return None
    except Exception as e:
        st.error(f"Error retrieving dates: {e}")
        return None


def main():

    st.set_page_config(layout="wide")

    st.title("🤖 💾 Wayback Machine URL Comparison Tool")

    st.write(
        """This tool allows you to compare two versions of a URL using the Wayback Machine.
        It uses [diff_match_patch](https://github.com/google/diff-match-patch) for the diffing.
        It should handle HTML, CSS, and JavaScript file diffs."""
    )

    st.write(
        "You can grab the source code for this app [here](https://github.com/jroakes/WayDiffer)."
    )

    st.divider()

    if "historical_url_input" not in st.session_state:
        st.session_state["historical_url_input"] = ""

    if "current_url_input" not in st.session_state:
        st.session_state["current_url_input"] = ""

    st.header("Step 1: List Available Dates")

    with st.form("url_input_form"):
        url = st.text_input(
            "Enter URL", key="url_input", help="Enter the URL to compare"
        )
        history_days = st.number_input(
            "Enter number of historical days",
            min_value=1,
            value=30,
            step=1,
            key="history_days_input",
            help="Enter the number of historical days to check for available dates",
        )
        submitted = st.form_submit_button("List Available Dates")

    if submitted and url:
        available_dates = list_available_dates(url, history_days)
        if available_dates:
            st.write("Available dates:")
            for memento_url, datetime_obj in available_dates.items():
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    st.write(f"{memento_url} - {datetime_obj}")
                with col2:
                    btn_key = f"btn_{memento_url}"
                    if st.button(
                        "Use This Date",
                        key=btn_key,
                        on_click=lambda memento_url=memento_url: st.session_state.update(
                            {
                                "historical_url_input": memento_url,
                                "current_url_input": url,
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
        diff_submitted = st.form_submit_button("Run Comparison")

    if diff_submitted and current_url and historical_url:
        display_option = "inline" if view_option == "View inline" else "new window"
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
