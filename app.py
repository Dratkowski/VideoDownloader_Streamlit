import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import subprocess
import os
from urllib.parse import urlparse
import glob

def extract_video_links(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        video_extensions = r'(https?://[^\s\'"<>]+(\.mp4|\.m3u8|\.webm|\.avi|\.mov))'
        video_links = re.findall(video_extensions, soup.prettify())
        return [link[0] for link in video_links]
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch the URL: {e}")
        return []

def download_video(url):
    save_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(save_dir, exist_ok=True)

    # Use yt-dlp output template to generate unique filenames
    output_template = os.path.join(save_dir, '%(title)s-%(id)s.%(ext)s')

    try:
        # Run yt-dlp, download best mp4 video + audio
        subprocess.run([
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
            "-o", output_template,
            url
        ], check=True)

        # Find the most recent downloaded file in save_dir
        list_of_files = glob.glob(os.path.join(save_dir, '*'))
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file, f"Download finished: {os.path.basename(latest_file)}"
    except Exception as e:
        return None, f"Download error: {e}"

st.title("📹 Video Link Extractor and Downloader")

url = st.text_input("Enter Website URL to Extract Video Links:")

video_links = []
video_choice = None

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
    with st.spinner("Downloading video, please wait..."):
        file_path, result_message = download_video(video_choice)
    if file_path and os.path.exists(file_path):
        st.success(result_message)
        with open(file_path, "rb") as f:
            st.download_button(
                label="📥 Click to Download Video",
                data=f,
                file_name=os.path.basename(file_path),
                mime="video/mp4"
            )
    else:
        st.error(result_message)
else:
    st.info("Enter a URL and select a video link to begin.")
