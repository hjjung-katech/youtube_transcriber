#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""자막 문서 생성 모듈."""

import os
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

from youtube_transcript_generator.downloader import clean_filename
from youtube_transcript_generator.transcriber import format_time


def create_transcript_document(
    captions: List[Dict[str, Any]], 
    title: str, 
    output_dir: str,
    translate: bool = False,
    api_key: Optional[str] = None
) -> str:
    """자막을 문서 파일로 만들기."""
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # 타임스탬프 포함 자막과 전체 스크립트 문서를 각각 생성
    timestamp_file = create_timestamp_document(captions, title, output_dir)
    script_file = create_script_document(captions, title, output_dir)
    
    # 타임스탬프 파일 경로 반환
    return timestamp_file


def create_timestamp_document(
    captions: List[Dict[str, Any]], 
    title: str, 
    output_dir: str
) -> str:
    """타임스탬프가 포함된 자막 문서 생성."""
    # 출력 디렉토리 생성 (상위 디렉토리 포함)
    os.makedirs(output_dir, exist_ok=True)
    
    doc = Document()
    
    # 제목 추가
    title_para = doc.add_heading(title, level=1)
    title_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    
    # 생성 시간 추가
    time_para = doc.add_paragraph(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    time_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    doc.add_paragraph()
    
    # 타임스탬프 포함 자막 섹션 추가
    doc.add_heading("타임스탬프 포함 자막", level=2)
    
    # 자막 내용 추가
    full_text = ""
    if captions:
        for caption in captions:
            time_str = format_time(caption['start'])
            text = caption['text']
            doc.add_paragraph(f"[{time_str}] {text}")
            full_text += text + " "
    else:
        doc.add_paragraph("자막이 없습니다.")
    
    # 자막이 거의 없는 경우 처리
    if not captions or len(full_text.strip()) < 30:
        warning_para = doc.add_paragraph("※ 이 동영상에는 충분한 자막이 없습니다.")
        warning_para.runs[0].bold = True
    
    # 파일 저장 전 디렉토리 재확인
    safe_title = clean_filename(title)
    output_file = os.path.join(output_dir, f"{safe_title}_타임스탬프.docx")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    doc.save(output_file)
    
    # 텍스트 파일로도 저장
    txt_output_file = os.path.join(output_dir, f"{safe_title}_타임스탬프.txt")
    with open(txt_output_file, 'w', encoding='utf-8') as f:
        f.write(f"{title}\n\n")
        f.write(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if not captions or len(full_text.strip()) < 30:
            f.write("※ 이 동영상에는 충분한 자막이 없습니다.\n\n")
        
        f.write("==== 타임스탬프 포함 자막 ====\n\n")
        if captions:
            for caption in captions:
                time_str = format_time(caption['start'])
                f.write(f"[{time_str}] {caption['text']}\n")
        else:
            f.write("자막이 없습니다.\n")
    
    return output_file


def create_script_document(
    captions: List[Dict[str, Any]], 
    title: str, 
    output_dir: str,
    translate: bool = False,
    api_key: Optional[str] = None
) -> str:
    """전체 스크립트 문서 생성."""
    # 출력 디렉토리 생성 (상위 디렉토리 포함)
    os.makedirs(output_dir, exist_ok=True)
    
    doc = Document()
    
    # 제목 추가
    title_para = doc.add_heading(title, level=1)
    title_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    
    # 생성 시간 추가
    time_para = doc.add_paragraph(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    time_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    doc.add_paragraph()
    
    # 자막 텍스트 추출
    full_text = ""
    if captions:
        for caption in captions:
            full_text += caption['text'] + " "
    
    # 자막이 거의 없는 경우 처리
    if not captions or len(full_text.strip()) < 30:
        warning_para = doc.add_paragraph("※ 이 동영상에는 충분한 자막이 없습니다.")
        warning_para.runs[0].bold = True
        full_text = "※ 이 동영상에는 충분한 자막이 없습니다. 자동 생성된 자막이 제한적이거나 없는 경우입니다."
    
    # 전체 스크립트 정제
    refined_script = refine_script(full_text) if full_text.strip() else "자막이 없습니다."
    
    # 전체 스크립트 추가 (정제된 버전)
    doc.add_heading("전체 스크립트", level=2)
    full_script_para = doc.add_paragraph(refined_script)
    full_script_para.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
    
    # 파일 저장 전 디렉토리 재확인
    safe_title = clean_filename(title)
    output_file = os.path.join(output_dir, f"{safe_title}_전체스크립트.docx")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    doc.save(output_file)
    
    # 텍스트 파일로도 저장
    txt_output_file = os.path.join(output_dir, f"{safe_title}_전체스크립트.txt")
    with open(txt_output_file, 'w', encoding='utf-8') as f:
        f.write(f"{title}\n\n")
        f.write(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if not captions or len(full_text.strip()) < 30:
            f.write("※ 이 동영상에는 충분한 자막이 없습니다.\n\n")
        
        f.write("==== 전체 스크립트 ====\n\n")
        f.write(refined_script)
    
    return output_file


def refine_script(text: str) -> str:
    """전체 스크립트에서 중복되는 단어나 불필요한 표현을 정리하고 원본 구두점을 유지."""
    if not text.strip():
        return ""

    # '[음악]', '[박수]', '[웃음]' 같은 불필요한 표현 제거
    text = re.sub(r'\[[^\]]*\]', '', text)

    # 문장 단위로 분리하되, 구분자(하나 이상의 .!?)도 보존
    parts = re.split(r'([.!?]+)', text) # 구분자를 그룹으로 묶어 보존

    sentences = []
    # parts 리스트는 [텍스트1, 구두점1, 텍스트2, 구두점2, ..., 텍스트N, (선택적)구두점N, (선택적)마지막텍스트] 형태
    for i in range(0, len(parts) - 1, 2): # 텍스트와 바로 뒤 구두점을 짝으로 처리
        text_part = parts[i].strip()
        punctuation_part = parts[i+1].strip() if (i + 1) < len(parts) else ""

        if text_part: # 텍스트 내용이 있는 경우에만 처리
            # === 구두점 처리 로직 수정 시작 ===
            processed_punc = punctuation_part
            if not processed_punc: # 구두점이 없는 경우 (거의 발생 안 함)
                processed_punc = "." # 기본값으로 마침표 추가? 또는 빈 문자열 유지? 여기서는 빈 문자열 유지

            elif all(c == '.' for c in processed_punc):
                processed_punc = '.'
            elif all(c == '?' for c in processed_punc):
                processed_punc = '?'
            elif all(c == '!' for c in processed_punc):
                processed_punc = '!'
            else: # 혼합 구두점 또는 단일 구두점
                # 규칙: ? 또는 !가 포함된 경우, 앞뒤의 . 제거
                if '?' in processed_punc or '!' in processed_punc:
                    processed_punc = processed_punc.strip('.')
                    # . 제거 후 비어있으면 ?나 ! 중 하나로 복원 (혹은 기본값 .)
                    if not processed_punc:
                         # 원래 ?나 !가 있었으므로 . 보다는 ?나 !가 더 적절할 수 있음
                         # 여기서는 원래 문자열에서 마지막 문자를 사용하거나, 기본값 . 사용
                         # 테스트 케이스에 맞춰 ?! 유지하도록 했으므로, 비는 경우는 거의 없음
                         # 만약 ".?." 같은 입력 -> "?" 가 됨.
                         # 만약 "." 만 있었다면 위에서 처리됨.
                         # 만약 ".!" 만 있었다면 "!" 가 됨.
                         # 만약 "..!" 였다면 "!" 가 됨.
                         # 만약 "!." 였다면 "!" 가 됨.
                         # 만약 ".?!" 였다면 "?!" 가 됨.
                         # 만약 "?!." 였다면 "?!" 가 됨.
                         # 만약 "..." 였다면 위에서 처리됨.
                         # 만약 "???" 였다면 위에서 처리됨.
                         # 만약 "!!!" 였다면 위에서 처리됨.
                         pass # .strip('.') 후 비지 않는다고 가정

                # 남은 문자열 내에서 동일 문자 반복 축약 (예: ??.! -> ?!)
                processed_punc = re.sub(r'(\?)\1+', r'\1', processed_punc)
                processed_punc = re.sub(r'(!)\1+', r'\1', processed_punc)
                # .은 이미 처리되었거나 제거됨

                # 최종적으로 비어있다면 기본값 . 추가 (예: " ." 같은 입력 처리)
                if not processed_punc:
                    processed_punc = "."

            # === 구두점 처리 로직 수정 끝 ===

            sentences.append(text_part + processed_punc) # 텍스트와 처리된 구두점 결합

    # 리스트 끝에 텍스트 부분만 남는 경우 처리 (구두점 없이 끝나는 경우)
    if len(parts) % 2 == 1 and parts[-1] and parts[-1].strip():
        trailing_text = parts[-1].strip()
        # 마지막 문장에 구두점이 없으면 기본값으로 마침표 추가
        if not re.search(r'[.!?]$', trailing_text):
             sentences.append(trailing_text + '.')
        else:
             sentences.append(trailing_text) # 이미 구두점 있으면 그대로 사용

    # 중복 문장 제거 (구두점 제외하고 내용으로 비교)
    unique_sentences = []
    seen_sentences_content = set()
    for sentence in sentences:
        # 비교를 위해 문장 끝의 구두점(하나 이상)을 제거
        content = re.sub(r'[.!?]+$', '', sentence).strip()
        if content and content not in seen_sentences_content:
            seen_sentences_content.add(content)
            unique_sentences.append(sentence) # 원본 문장(구두점 포함) 추가

    # 문장들을 공백으로 구분하여 결합
    refined_text = ' '.join(unique_sentences)

    # 불필요한 공백 정리 (최종)
    refined_text = ' '.join(refined_text.split())

    return refined_text.strip()