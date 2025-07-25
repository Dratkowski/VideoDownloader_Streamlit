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
    save_path = os.getcwd()  # Use current directory instead of Desktop
    if not custom_filename:
        parsed_url = urlparse(url)
        custom_filename = parsed_url.netloc
    custom_filename = os.path.join(save_path, custom_filename)

    if not custom_filename.endswith(".mp4"):
        custom_filename += ".mp4"

    try:
        subprocess.run([
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
            "-o", custom_filename,
            url
        ], check=True)

        result_text = f"Download finished: {custom_filename}"
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

custom_filename = st.text_input("Enter custom file name:", "default_filename")

video_choice = url
video_links = []

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

if st.button("Download") and video_choice:
    file_path, result = download_video(video_choice, custom_filename, download_option)
    if file_path:
        st.success(result)
        with open(file_path, "rb") as f:
            st.download_button(
                label="📥 Click to Download Video",
                data=f,
                file_name=os.path.basename(file_path),
                mime="video/mp4"
            )
    else:
        st.error(result)
else:
    st.info("Enter a URL to begin.")
