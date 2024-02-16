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

    st.title("🚂 Wayback Machine URL Comparison Tool")

    if "historical_url_input" not in st.session_state:
        st.session_state["historical_url_input"] = ""

    if "current_url_input" not in st.session_state:
        st.session_state["current_url_input"] = ""

    with st.form("url_input_form"):
        url = st.text_input("Enter URL", key="url_input")
        history_days = st.number_input(
            "Enter number of historical days",
            min_value=1,
            value=30,
            step=1,
            key="history_days_input",
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
    st.write("")
    with st.form("diff_input_form"):
        current_url = st.text_input("Enter current URL", key="current_url_input")
        historical_url = st.text_input(
            "Enter historical URL", key="historical_url_input"
        )
        view_option = st.radio(
            "Choose how to view the diff:",
            ("Open in new window", "View inline"),
            key="view_option_input",
        )
        diff_submitted = st.form_submit_button("Run Comparison")

    if diff_submitted and current_url and historical_url:
        display_option = "inline" if view_option == "View inline" else "new window"
        html = process_diff(current_url, historical_url)
        if html:
            if display_option == "new window":
                file_location = save_file(html)
                webbrowser.open_new_tab(file_location)
            else:
                st.write("")
                st.write("")
                components.html(html, height=1000, scrolling=True)
        else:
            st.error("Failed to process diff. Please ensure the URLs are correct.")


if __name__ == "__main__":
    main()
