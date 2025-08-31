# app.py
import streamlit as st
from final_teams_title import run_scraping
import os
import time

st.set_page_config(page_title="UF Job Scraper", page_icon="🧑‍💼", layout="wide")

st.title("UF Job Scraper")
st.write("Paste a UF sitemap URL or a single job URL. If you paste the root `https://teams-titles.hr.ufl.edu/`, the app will scrape ALL jobs from the default UF sitemap.")

default = "https://teams-titles.hr.ufl.edu/"
url_input = st.text_input("URL (sitemap or single job)", value=default)

start = st.button("Start scraping")

progress_bar = st.progress(0)
status_text = st.empty()
log_box = st.empty()

_logs = []

def progress_cb(curr, total, msg):
    """Callback passed to run_scraping to update UI"""
    try:
        pct = int((curr / max(total, 1)) * 100)
    except Exception:
        pct = 0
    # progress_bar accepts 0-100
    progress_bar.progress(min(max(pct, 0), 100))
    status_text.text(f"{msg} — {curr} of {total}")
    _logs.append(f"{time.strftime('%H:%M:%S')} - {msg}")
    # keep only last 12 messages
    log_box.text("\n".join(_logs[-12:]))

if start:
    if not url_input.strip():
        st.error("Please enter a URL or leave empty to use the default sitemap.")
    else:
        status_text.info("Starting scraping. This can take a while if you scrape all jobs...")
        with st.spinner("Scraping in progress..."):
            try:
                output_file = run_scraping(url_input.strip(), progress_cb=progress_cb)
                # Ensure progress reaches 100%
                progress_bar.progress(100)
                if output_file and os.path.exists(output_file):
                    st.success("Done! Your formatted Excel is ready.")
                    with open(output_file, "rb") as fh:
                        st.download_button(
                            label="Download formatted Excel",
                            data=fh,
                            file_name=output_file,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        )
                else:
                    st.error("No jobs found or an error occurred. Check the logs below.")
            except Exception as e:
                st.error(f"Unexpected error: {e}")
                _logs.append(f"ERROR: {e}")
                log_box.text("\n".join(_logs[-12:]))
