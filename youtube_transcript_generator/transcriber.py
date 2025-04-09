#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""자막 추출 및 생성 모듈."""

from typing import Tuple, List, Dict, Any, Optional

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled, 
    NoTranscriptFound, 
    NoTranscriptAvailable
)


def get_youtube_captions(video_id: str) -> Tuple[bool, Optional[List[Dict[str, Any]]]]:
    """유튜브 자동 자막 가져오기."""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # 언어 우선순위 확장 (한국어, 영어, 일본어, 중국어, 자동 생성 등)
        language_priority = ['ko', 'en', 'ja', 'auto']
        
        # 자동 생성된 자막 우선, 없으면 일반 자막 사용
        try:
            transcript = transcript_list.find_generated_transcript(language_priority)
        except (NoTranscriptFound, NoTranscriptAvailable):
            # 자동 생성 자막이 없는 경우 수동 자막 시도
            try:
                transcript = transcript_list.find_manually_created_transcript(language_priority)
            except (NoTranscriptFound, NoTranscriptAvailable):
                # 어떤 자막도 없으면 첫 번째 사용 가능한 자막 사용
                try:
                    transcript = next(iter(transcript_list))
                except StopIteration:
                    # 사용 가능한 자막이 없음
                    return False, None
        
        captions = transcript.fetch()
        
        # 자막에 실질적인 내용이 있는지 확인
        if check_meaningful_captions(captions):
            return True, captions
        else:
            print("자막이 있지만 의미 있는 내용이 충분하지 않습니다.")
            return True, captions  # 자막은 반환하되, 의미 있는 내용이 적다는 정보를 로그로 출력
        
    except (TranscriptsDisabled, NoTranscriptFound, NoTranscriptAvailable) as e:
        print(f"유튜브 자막 추출 실패: {str(e)}")
        return False, None
    except Exception as e:
        print(f"자막 추출 중 오류 발생: {str(e)}")
        return False, None


def check_meaningful_captions(captions: List[Dict[str, Any]]) -> bool:
    """자막에 실질적인 내용이 있는지 확인."""
    if not captions:
        return False
    
    # 자막 텍스트의 총 길이 확인
    total_text = " ".join(caption["text"] for caption in captions)
    
    # 특수문자, 공백 등을 제외한 실질적인 텍스트 길이
    meaningful_length = len("".join(c for c in total_text if c.isalnum()))
    
    # 의미 있는 텍스트가 최소 20자 이상인지 확인
    return meaningful_length >= 20


def format_time(seconds: float) -> str:
    """초를 00:00:00 형식으로 변환."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"