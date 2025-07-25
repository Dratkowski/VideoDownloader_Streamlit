import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import subprocess
import os
from urllib.parse import urlparse

def extract_video_links(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        video_extensions = r'(https?://[^\s]+(\.mp4|\.m3u8|\.webm|\.avi|\.mov))'
        video_links = re.findall(video_extensions, soup.prettify())
        return [link[0] for link in video_links]
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch the URL: {e}")
        return []

def download_video(url, custom_filename, download_option):
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    if not custom_filename:
        parsed_url = urlparse(url)
        custom_filename = parsed_url.netloc
    custom_filename = os.path.join(desktop_path, custom_filename)

    if url.lower().endswith(".mp4"):
        if not custom_filename.endswith(".mp4"):
            custom_filename += ".mp4"
        download_option = "MP4"
    elif download_option == ".m3u8" and not custom_filename.endswith(".mp4"):
        custom_filename += ".mp4"
    elif download_option == "MP4/Social Media Videos" and not custom_filename.endswith(".mp4"):
        custom_filename += ".mp4"

    try:
        subprocess.run(["yt-dlp", "-o", custom_filename, url], check=True)
        result_text = f"Download finished: {custom_filename}"

        if download_option == "Youtube":
            webm_file = f"{custom_filename}.webm"
            mp4_file = f"{custom_filename}.mp4"
            subprocess.run(["ffmpeg", "-i", webm_file, mp4_file], check=True)
            os.remove(webm_file)
            result_text = f"Download and conversion finished: {mp4_file}"
            return mp4_file, result_text
        return custom_filename, result_text

    except Exception as e:
        return None, f"Error: {e}"

st.title("📹 Video Link Extractor and Downloader")

url = st.text_input("Enter Website URL to Extract Video Links:")

download_option = st.selectbox(
    "Select video option",
    ["Youtube", ".m3u8", "MP4/Social Media Videos"],
    index=2
)

custom_filename = st.text_input("Enter custom file name (video will save to Desktop):", "default_filename")

if url:
    if 'facebook.com' in url:
        video_links = [url]
    else:
        video_links = extract_video_links(url)

    if video_links:
        video_choice = st.selectbox("Select a video link to download:", video_links)
    else:
        st.warning("No video links found. Defaulting to entered URL.")
        video_choice = url

    if st.button("Download"):
        file_path, result = download_video(video_choice, custom_filename, download_option)
        if file_path:
            st.success(result)
            st.markdown(f"[📁 Open File]({file_path})")
        else:
            st.error(result)
else:
    st.info("Enter a URL to begin.")
