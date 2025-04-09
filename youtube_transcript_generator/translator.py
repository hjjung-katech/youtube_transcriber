#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""스크립트 번역 모듈."""

import os
import time
from typing import Optional, Dict, Any
import json
from pathlib import Path

try:
    import dotenv
    dotenv_loaded = True
except ImportError:
    dotenv_loaded = False

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
except ImportError:
    genai = None


class TranslationError(Exception):
    """번역 중 발생하는 오류를 처리하기 위한 예외 클래스."""
    pass


def load_env_file(env_path: Optional[str] = None) -> bool:
    """환경 변수 설정 파일(.env) 로드."""
    if not dotenv_loaded:
        print("dotenv 패키지가 설치되지 않았습니다. pip install python-dotenv 명령으로 설치하세요.")
        return False
    
    # 기본 .env 파일 경로
    if not env_path:
        # 프로젝트 루트 디렉토리 찾기
        current_dir = Path(__file__).resolve().parent
        root_dir = current_dir.parent
        env_path = root_dir / '.env'
    
    # .env 파일 로드
    if os.path.exists(env_path):
        dotenv.load_dotenv(env_path)
        return True
    else:
        print(f".env 파일을 찾을 수 없습니다: {env_path}")
        return False


def configure_genai(api_key: Optional[str] = None) -> bool:
    """Gemini API 설정."""
    if genai is None:
        print("Gemini API를 사용하려면 google-generativeai 패키지를 설치하세요: pip install google-generativeai")
        return False
    
    # .env 파일 로드 시도
    if dotenv_loaded:
        load_env_file()
    
    # API 키 설정 (우선순위: 인자 > 환경변수)
    if api_key is None:
        api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("Gemini API 키가 설정되지 않았습니다. .env 파일 또는 환경변수 GEMINI_API_KEY를 설정하거나 매개변수로 전달하세요.")
        return False
    
    # Gemini API 설정
    genai.configure(api_key=api_key)
    return True


def translate_text(text: str, source_lang: str = "en", target_lang: str = "ko", api_key: Optional[str] = None) -> str:
    """Gemini API를 사용하여 텍스트 번역."""
    if not configure_genai(api_key):
        raise TranslationError("Gemini API 설정에 실패했습니다.")
    
    # 텍스트가 너무 짧으면 번역하지 않음
    if len(text.strip()) < 5:
        return text
    
    # 번역 프롬프트 작성
    prompt = f"""
Please translate the following text from {source_lang} to {target_lang}.
Maintain the original meaning, tone, and context as closely as possible.
Ensure the translation is natural and fluent in {target_lang}.

Text to translate:
{text}

Translation:
"""
    
    # Gemini 모델 설정
    try:
        generation_config = {
            "temperature": 0.2,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # 응답 생성
        response = model.generate_content(prompt)
        translated_text = response.text
        
        # 결과 반환
        return translated_text.strip()
        
    except Exception as e:
        # 오류 발생 시 재시도
        try:
            print(f"번역 중 오류 발생: {str(e)}. 5초 후 재시도합니다...")
            time.sleep(5)
            model = genai.GenerativeModel(model_name="gemini-1.5-pro")
            response = model.generate_content(prompt)
            translated_text = response.text
            return translated_text.strip()
        except Exception as e:
            raise TranslationError(f"번역 중 오류 발생: {str(e)}")


def translate_paragraphs(paragraphs: list, source_lang: str = "en", target_lang: str = "ko", api_key: Optional[str] = None) -> list:
    """단락 목록을 번역."""
    if not configure_genai(api_key):
        raise TranslationError("Gemini API 설정에 실패했습니다.")
    
    translated_paragraphs = []
    
    for i, paragraph in enumerate(paragraphs):
        if paragraph.strip():
            try:
                print(f"단락 {i+1}/{len(paragraphs)} 번역 중...")
                translated = translate_text(paragraph, source_lang, target_lang, api_key)
                translated_paragraphs.append(translated)
                # API 요청 간 간격 두기
                time.sleep(1)
            except Exception as e:
                print(f"단락 번역 실패: {str(e)}")
                translated_paragraphs.append(paragraph)  # 실패 시 원본 텍스트 사용
        else:
            translated_paragraphs.append("")
    
    return translated_paragraphs


def detect_language(text: str) -> str:
    """텍스트의 언어 감지 (간단한 휴리스틱 사용).
    
    참고: 더 정확한 언어 감지가 필요하면 langdetect 또는 fasttext 등의 전용 라이브러리를 사용하는 것이 좋습니다.
    """
    # 한국어 문자 범위
    korean_chars = set([chr(c) for c in range(0xAC00, 0xD7A4)])
    
    # 일본어 히라가나, 가타카나 범위
    japanese_chars = set([chr(c) for c in range(0x3040, 0x30FF)])
    
    # 중국어 간체, 번체 범위 (일부)
    chinese_chars = set([chr(c) for c in range(0x4E00, 0x9FFF)])
    
    # 영어 문자
    english_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    
    # 문자별 카운트
    korean_count = sum(1 for c in text if c in korean_chars)
    japanese_count = sum(1 for c in text if c in japanese_chars)
    chinese_count = sum(1 for c in text if c in chinese_chars)
    english_count = sum(1 for c in text if c in english_chars)
    
    # 가장 많은 문자 타입의 언어 반환
    counts = {
        'ko': korean_count,
        'ja': japanese_count,
        'zh': chinese_count,
        'en': english_count
    }
    
    # 언어 코드 반환 (기본값은 영어)
    max_lang = max(counts, key=counts.get)
    
    # 대부분의 문자가 ASCII인 경우 영어로 가정
    if counts[max_lang] < len(text) * 0.05:
        return 'en'
    
    return max_lang