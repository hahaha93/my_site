import yt_dlp
import os
import glob
from urllib.parse import urlparse, parse_qs

def get_info(url: str):
    """
    Get information about the video.
    """
    ydl_opts = {
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

def download_video(url: str, output_path: str = "downloads"):
    """
    Download the video. Returns tuple (file_path, title).
    """
    abs_output_path = os.path.abspath(output_path)
    os.makedirs(abs_output_path, exist_ok=True)
    
    # We use id as filename to easily locate it regardless of extension
    ydl_opts = {
        'outtmpl': f'{abs_output_path}/%(id)s.%(ext)s',
        'quiet': False,
        'noplaylist': True, # Ensure no playlist
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info['id']
        video_title = info.get('title', 'video')
        
        # Find the file. It might be .mp4, .webm, or .mkv depending on merge
        # Search for file starting with video_id in the folder
        files = glob.glob(f'{abs_output_path}/{video_id}.*')
        if not files:
            raise Exception("File found not be found after download")
            
        # Return the simplified title and the actual file path
        # Prefer the one that is not a partial part if any exist (though yt-dlp cleans up)
        final_file = files[0]
        return final_file, video_title

def clean_url(url: str) -> str:
    """
    Extract the main YouTube watch URL from a potentially long YouTube URL.
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    if "v" in query_params and query_params["v"]:
        video_id = query_params["v"][0]
        return f"https://www.youtube.com/watch?v={video_id}"
    else:
        return url
