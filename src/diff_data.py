"""Data module for the web archive diff tool."""

import re
import os
import html
import random
from typing import Union, Tuple
from datetime import datetime, timedelta

import streamlit as st
import requests
from diff_match_patch import diff_match_patch
import jsbeautifier
import cssbeautifier
from bs4 import BeautifulSoup, Comment

from loguru import logger

from constants import (
    HTML_CODE,
    CSS_CODE,
    JS_CODE,
    WBM_REGEX,
    MAX_MEMENTO_LINES,
    TOP_USERAGENTS_URL,
    DEFAULT_USER_AGENT,
    TIMEOUT,
)


def get_available_dates(url: str, history_days: int = 365) -> Union[dict, None]:
    """
    Retrieve available memento URLs and their datetimes for a URL from the TimeMap service.

    Parameters
    ----------
    url: str
      The URL to retrieve available memento URLs and their datetimes for.
    history_days: int
      The number of days of history to retrieve.

    Returns
    -------
    dict
      A dictionary of available memento URLs and their datetimes.

    Raises
    ------
    ValueError
      If the URL is not valid.
    """

    try:
        # Calculate the start date based on the specified history_days
        start_date = datetime.now() - timedelta(days=history_days)

        # TimeMap URL for the given URL
        timemap_url = f"http://web.archive.org/web/timemap/link/{url}"

        # Fetch TimeMap data
        response = requests.get(timemap_url)
        if response.status_code == 200:
            # Parse TimeMap data using regular expressions
            mementos = {}
            lines = response.text.split("\n")
            for line in lines:
                match = re.match(r'<([^>]+)>; rel="([^"]+)"; datetime="([^"]+)"', line)
                if match:
                    memento_url = match.group(1)
                    rel = match.group(2)
                    datetime_str = match.group(3)
                    datetime_obj = datetime.strptime(
                        datetime_str, "%a, %d %b %Y %H:%M:%S GMT"
                    )
                    if rel == "memento" and datetime_obj >= start_date:
                        # Format datetime_obj to nice date MM/DD/YYYY - HH:MM AM/PM
                        formatted_date = datetime_obj.strftime("%m/%d/%Y - %I:%M %p")
                        mementos[memento_url] = formatted_date
                        if len(mementos) >= MAX_MEMENTO_LINES:
                            break
            return mementos
        else:
            logger.warning(
                f"Failed to fetch TimeMap data. Status code: {response.status_code}"
            )
            return None

    except Exception as e:
        logger.error(f"Unknown Error: {e}")
        return None


def clean_wayback_html(content: str) -> str:
    """
    Cleans HTML content retrieved from the Wayback Machine by removing specific elements and comments.

    Parameters
    ----------
    content: str
        The HTML content to be cleaned.

    Returns
    -------
    str
        The cleaned HTML content.
    """
    soup = BeautifulSoup(content, "html.parser")

    # Remove elements with src or href containing "archive.org"
    for script_tag in soup.head.find_all(
        "script", src=re.compile("web-static\.archive\.org")
    ):
        script_tag.decompose()

    for link_tag in soup.head.find_all(
        "link", href=re.compile("web-static\.archive\.org")
    ):
        link_tag.decompose()

    # Remove comments that include "Wayback"
    comments = soup.head.find_all(
        string=lambda text: isinstance(text, Comment) and "Wayback" in text
    )
    for comment in comments:
        comment.extract()

    # Remove specific <script> tags based on their content
    script_content_patterns = [r"window\.RufflePlayer", r"__wm\.wombat"]
    for pattern in script_content_patterns:
        for script_tag in soup.find_all("script", string=re.compile(pattern)):
            script_tag.decompose()

    return soup.prettify()


def beautify_file(content: str, file_type: str) -> str:
    """
    Beautify the content of a file based on the file type.

    Paramaters
    ----------
    content: str
      The content of the file to be beautified.
    file_type: str
      The type of file to be beautified. Can be one of the following:
      - 'html': Beautify the content as HTML.
      - 'css': Beautify the content as CSS.
      - 'js': Beautify the content as JavaScript.

    Returns
    -------
    str
      The beautified content.

    Raises
    -------
    ValueError
      If the file type is not supported.
    """

    if file_type == "html":
        beautified_content = clean_wayback_html(content)
    elif file_type == "css":
        beautified_content = cssbeautifier.beautify(content)
    elif file_type == "js":
        beautified_content = jsbeautifier.beautify(content)
    else:
        raise ValueError("Unsupported file type. Please use 'html', 'css', or 'js'.")

    return beautified_content


def get_random_user_agent() -> str:
    """Grabs a random user agent from the top user agents list.

    Returns
    -------
    str
      A random user agent or the default user agent if the top user agents list cannot be fetched.
    """

    response = requests.get(TOP_USERAGENTS_URL)
    if response.status_code == 200:
        user_agents = response.json()
        # Randomly select a user agent
        loc = random.randint(0, len(user_agents) - 1)
        return user_agents[loc]
    else:
        logger.warning(
            f"Failed to fetch top user agents. Status code: {response.status_code}"
        )
        return DEFAULT_USER_AGENT


def fetch_and_beautify_content(url: str) -> Union[str, None]:
    """Fetch and beautify content from web archive.

    Parameters
    ----------
    url: str
      The URL of the content to be fetched and beautified.

    Returns
    -------
    Union[str, None]
      The beautified content or None if the content could not be fetched.

    """

    # Fetch content
    headers = {
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "identity",
        "Cache-Control": "no-cache",
        "User-Agent": get_random_user_agent(),
        "Dnt": "1",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1",
    }  # Set the user agent to avoid 403 errors

    response = requests.get(url, headers=headers, timeout=TIMEOUT)

    if response.status_code == 200:

        content_type = response.headers["Content-Type"]
        content = response.text

        # Removes the Wayback Machine footer
        content = re.split(r"(?:/\*|<!--)\s+FILE ARCHIVED ON", content, maxsplit=1)[
            0
        ].strip()

        # Remove Wayback Machine URLs
        wbm_url_pattern = re.compile(WBM_REGEX)
        content = re.sub(
            wbm_url_pattern,
            "",
            content,
        )

        # Arbitrary length check to ensure content is not empty or too short
        if not content or len(content) < 50:
            st.warning(f"No content returned for {url}.")
            logger.warning(f"No content returned for {url}.")
            return None

        if "text/html" in content_type:
            beautified_content = html.escape(beautify_file(content, "html"))

        elif "text/css" in content_type:
            beautified_content = beautify_file(content, "css")

        elif "application/javascript" in content_type:
            beautified_content = beautify_file(content, "js")

        else:
            st.warning(
                f"Unsupported content type: {content_type}. Please use 'text/html', 'text/css', or 'application/javascript'."
            )
            logger.error(
                f"Unsupported content type: {content_type}. Please use 'text/html', 'text/css', or 'application/javascript'."
            )

            return None

        return beautified_content

    elif response.status_code in [404, 403]:
        st.warning(f"{url} does not exist or we have been blocked.")
        logger.warning(f"{url} does not exist or we have been blocked.")

    else:
        st.warning(
            f"Failed to fetch content from {url}. Status code: {response.status_code}"
        )
        logger.warning(
            f"Failed to fetch content from {url}. Status code: {response.status_code}"
        )

    return None


def process_op(op: str) -> Union[str, None]:
    """Process a diff operation.

    Parameters
    ----------
    op: str
      The diff operation to be processed.

    Returns
    -------
    Union[str, None]
      The processed diff operation or None if the operation is no diff.
    """
    if op == diff_match_patch.DIFF_INSERT:
        return "added"
    elif op == diff_match_patch.DIFF_DELETE:
        return "deleted"
    else:
        return None


def process_temp(
    op: str, line: str, temp: list, clear_temp: bool = False
) -> Tuple[str, list]:
    """Process a temporary diff

    Parameters
    ----------
    op: str
      The diff operation to be processed.
    line: str
      The line to be processed.
    temp: list
      A list of tuples containing the diff operations and lines.
    clear_temp: bool
      Whether this is the last line to be processed and the temp list should be cleared.


    Returns
    -------
    Tuple[str, list]
      A tuple containing the processed diff operation and temp list.
    """

    temp.append((op, line))

    line_html = ""

    for temp_op, temp_line in temp:
        span_class = process_op(temp_op)
        data_html = temp_line.replace(" ", "&nbsp;").replace("\t", "&nbsp;" * 4)
        line_html += (
            f'<span class="{span_class}">{data_html}</span>'
            if span_class
            else data_html
        )

    if clear_temp:
        temp = []

    return line_html, temp


def process_line(
    text: str,
) -> Tuple[Union[str, None], Union[str, None], Union[str, None]]:
    """Process a line of text and categorize into partial, whole, and remaining lines.

    Parameters
    ----------
    text: str
      The text to be processed.

    Returns
    -------
    Tuple[Union[str, None], Union[str, None], Union[str, None]]
      A tuple containing the partial, whole, and remaining lines.
    """

    partial, whole_lines, remaining = None, None, None

    if "\n" in text:
        split_data = text.split("\n")
        whole_lines = split_data[:-1]
        remaining = split_data[-1] if split_data[-1] else None
    else:
        partial = text

    return partial, whole_lines, remaining


def process_diff(url1: str, url2: str) -> Union[str, None]:
    """Processes urls to generate a diff between the two.

    Parameters
    ----------
    url1 : str
      The first url to be processed.
    url2 : str
      The second url to be processed.

    Returns
    ------
    Union[str, None]
      The HTML diff.
    """

    content1 = fetch_and_beautify_content(url1)
    content2 = fetch_and_beautify_content(url2)

    if content1 and content2:

        if content1 == content2:
            logger.info("The content from both URLs is the same.")
            return "SAME CONTENT"

        # Perform the diffs
        dmp = diff_match_patch()
        diffs = dmp.diff_main(content1, content2)
        dmp.diff_cleanupSemantic(diffs)

        # Initial diff-container
        diff_content = []

        # Initial Line
        line_number = 1

        # Temp storage for incomplete lines
        temp = []

        for op, data in diffs:

            partial, whole_lines, remaining = process_line(data)

            # Process partial lines
            if partial:
                temp.append((op, partial))

            # Process whole lines
            elif whole_lines:
                for line in whole_lines:
                    # Clearing temp here because it will append the current line
                    # to previous buffered temp items and will process to a line.
                    # Temp should be empty for consecutive lines.
                    line_html, temp = process_temp(op, line, temp, clear_temp=True)
                    diff_content.append(
                        f'\t\t\t<div class="line"><span class="line-num">{line_number}</span>{line_html}</div>'
                    )
                    line_number += 1

            if remaining:
                temp.append((op, remaining))

        # Clean up any remaining
        if len(temp) > 0:
            line_html, temp = process_temp(op, line, temp, clear_temp=True)
            diff_content.append(
                f'\t\t\t<div class="line"><span class="line-num">{line_number}</span>{line_html}</div>'
            )

        # Generate the HTML
        diff_content = "\n".join(diff_content)

        html = HTML_CODE.format(
            css_code=CSS_CODE, js_code=JS_CODE, diff_content=diff_content
        )

        logger.info(
            "Successfully fetched JavaScript content from both URLs and generated html diff."
        )

        return html

    else:
        logger.error("Failed to fetch content from one or both URLs.")
        st.error("Failed to fetch content from one or both URLs.")
        return None


def save_file(html: str, filename: str = "diff.html") -> str:
    """Saves the HTML to a file.

    Parameters
    ----------
    html : str
      The HTML to be saved.
    filename : str
      The name of the file to be saved.

    Returns
    -------
    str
      The file location.
    """

    with open(filename, "w") as f:
        f.write(html)

    # Get file location
    file_location = os.path.abspath(filename)

    logger.info(f"Successfully saved HTML to {file_location}")

    return file_location
