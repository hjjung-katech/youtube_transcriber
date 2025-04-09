#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""유튜브 동영상 다운로드 및 자막 추출 메인 모듈."""

import os
import sys
import argparse
from typing import List, Optional
from pathlib import Path

from youtube_transcript_generator.downloader import download_video, get_video_id
from youtube_transcript_generator.transcriber import get_youtube_captions
from youtube_transcript_generator.document_generator import create_transcript_document
from youtube_transcript_generator.translator import load_env_file


def process_video(
    url: str, 
    output_dir: str, 
    translate: bool = False, 
    api_key: Optional[str] = None,
    env_file: Optional[str] = None
) -> int:
    """비디오 처리 프로세스."""
    try:
        # .env 파일 로드 (있는 경우)
        if env_file:
            load_env_file(env_file)
        else:
            # 프로젝트 루트 디렉토리의 .env 파일 자동 로드
            load_env_file()
            
        # 비디오 ID 추출
        video_id = get_video_id(url)
        print(f"비디오 ID: {video_id}")
        
        # 유튜브 자막 가져오기 시도
        success, captions = get_youtube_captions(video_id)
        
        # 다운로드 시도 여부 확인 (선택 사항)
        try_download = False  # 동영상 다운로드를 건너뛰려면 False로 설정
        
        # 기본 제목 설정
        title = f"YouTube Video {video_id}"
        
        # 동영상 정보 가져오기 (다운로드 없이)
        if try_download:
            try:
                print(f"동영상 다운로드 중: {url}")
                audio_file, video_title, _ = download_video(url, output_dir)
                title = video_title  # 다운로드 성공 시 실제 영상 제목으로 변경
                print(f"다운로드 완료: {title}")
            except Exception as e:
                print(f"동영상 다운로드 실패 (자막만 처리합니다): {str(e)}")
        else:
            # 동영상 다운로드 없이 제목만 가져오기 (YouTube API 사용)
            try:
                import yt_dlp
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'skip_download': True,
                    'ignoreerrors': True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info:
                        title = info.get('title', title)
                print(f"동영상 제목 추출 완료: {title}")
            except Exception as e:
                print(f"동영상 제목 추출 실패 (기본 ID를 사용합니다): {str(e)}")
        
        # 유튜브 자막이 없는 경우 메시지 표시
        if not success or not captions:
            print("유튜브 자막을 찾을 수 없습니다.")
            captions = []  # 빈 자막 리스트 사용
        else:
            print(f"유튜브 자막을 성공적으로 가져왔습니다. (총 {len(captions)}개 항목)")
        
        # 번역 기능 사용 여부 확인
        if translate:
            # Gemini API 키 확인
            if not api_key:
                api_key = os.environ.get("GEMINI_API_KEY")
                if not api_key:
                    print("Gemini API 키가 설정되지 않았습니다. 번역 기능을 사용하지 않습니다.")
                    print("API 키를 설정하려면 .env 파일에 GEMINI_API_KEY를 설정하거나 --api-key 옵션을 사용하세요.")
                    translate = False
                else:
                    print(".env 파일 또는 환경 변수에서 Gemini API 키를 가져왔습니다.")
            else:
                print("명령줄 옵션으로 제공된 Gemini API 키를 사용합니다.")
        
        # 문서 생성 (자막이 없어도 문서는 생성)
        output_file = create_transcript_document(captions, title, output_dir, translate, api_key)
        print(f"스크립트 문서 생성 완료: {output_file}")
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """명령줄 인수 파싱."""
    parser = argparse.ArgumentParser(description='유튜브 동영상 다운로드 및 자막 추출')
    parser.add_argument('url', help='유튜브 동영상 URL 또는 ID')
    parser.add_argument(
        '--output-dir', 
        '-o', 
        default='./downloads', 
        help='출력 디렉토리 (기본값: ./downloads)'
    )
    parser.add_argument(
        '--download',
        '-d',
        action='store_true',
        help='동영상 다운로드 시도 (기본값: 다운로드 안 함)'
    )
    parser.add_argument(
        '--translate',
        '-t',
        action='store_true',
        help='Gemini API를 사용하여 자막을 한국어로 번역 (기본값: 번역 안 함)'
    )
    parser.add_argument(
        '--api-key',
        help='Gemini API 키 (환경 변수 GEMINI_API_KEY로도 설정 가능)'
    )
    parser.add_argument(
        '--env-file',
        help='.env 파일 경로 지정 (기본값: 프로젝트 루트 디렉토리의 .env 파일)'
    )
    
    return parser.parse_args(args)


def run_cli(args: Optional[List[str]] = None) -> int:
    """CLI 실행 함수."""
    parsed_args = parse_args(args)
    
    # 출력 디렉토리 생성
    os.makedirs(parsed_args.output_dir, exist_ok=True)
    
    return process_video(
        parsed_args.url, 
        parsed_args.output_dir, 
        parsed_args.translate, 
        parsed_args.api_key,
        parsed_args.env_file
    )


def main() -> int:
    """메인 함수."""
    return run_cli()


if __name__ == "__main__":
    sys.exit(main())