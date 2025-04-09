#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""유튜브 동영상 다운로드 모듈."""

import os
import re
from typing import Tuple

import yt_dlp


def clean_filename(filename: str) -> str:
    """파일 이름에서 유효하지 않은 문자 제거."""
    return re.sub(r'[\\/*?:"<>|]', "", filename)


def get_video_id(url: str) -> str:
    """YouTube URL에서 비디오 ID 추출."""
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    elif "youtube.com" in url:
        if "v=" in url:
            return url.split("v=")[1].split("&")[0]
    return url  # 이미 ID인 경우


def download_video(url: str, output_dir: str) -> Tuple[str, str, str]:
    """유튜브 동영상 다운로드."""
    video_id = get_video_id(url)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'ignoreerrors': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        title = info.get('title', video_id)
        
    # 확장자가 변경될 수 있으므로 실제 파일 확인
    base_filename = os.path.join(output_dir, video_id)
    for file in os.listdir(output_dir):
        if file.startswith(video_id + '.'):
            filename = os.path.join(output_dir, file)
            break
    
    return filename, title, video_id