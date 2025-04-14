import unittest
from unittest.mock import patch, MagicMock, mock_open
from youtube_transcript_generator.document_generator import (
    create_script_document,
    create_timestamp_document,
    refine_script
)
import os
import shutil
from datetime import datetime

class TestDocumentGenerator(unittest.TestCase):
    def setUp(self):
        """테스트 설정."""
        self.test_captions = [
            {"start": 0, "text": "Hello world."},
            {"start": 5, "text": "This is a test."}
        ]
        self.title = "Test Title"
        # 테스트 디렉토리를 프로젝트 루트 아래에 생성하도록 경로 수정
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_output")

        # 테스트 출력 디렉토리 생성 (기존 디렉토리 삭제 후 생성)
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def tearDown(self):
        """테스트 정리."""
        # 테스트 디렉토리가 존재하면 완전히 제거
        if os.path.exists(self.output_dir):
            try:
                shutil.rmtree(self.output_dir)
            except Exception as e:
                print(f"Warning: Failed to clean up test directory: {e}")

    # verify_document_files 함수는 실제 파일 생성 시 유용하므로 유지

    @patch('youtube_transcript_generator.document_generator.clean_filename')
    @patch('youtube_transcript_generator.document_generator.Document')
    @patch('builtins.open', new_callable=mock_open) # TXT 파일 쓰기를 위한 mock 추가
    def test_create_script_document(self, mock_file_open, mock_document, mock_clean_filename):
        """create_script_document 함수 테스트 (TXT 파일 생성 포함)."""
        # Mock 설정
        mock_clean_filename.return_value = "Test_Title"
        mock_doc_instance = MagicMock()
        mock_document.return_value = mock_doc_instance

        # 기본 케이스 테스트
        result_docx = create_script_document(self.test_captions, self.title, self.output_dir)

        # DOCX 검증
        mock_clean_filename.assert_called_with(self.title)
        mock_document.assert_called_once()
        expected_docx_path = os.path.join(self.output_dir, "Test_Title_전체스크립트.docx")
        mock_doc_instance.save.assert_called_once_with(expected_docx_path)
        self.assertEqual(result_docx, expected_docx_path)

        # TXT 검증
        expected_txt_path = os.path.join(self.output_dir, "Test_Title_전체스크립트.txt")
        mock_file_open.assert_called_once_with(expected_txt_path, 'w', encoding='utf-8')

        # 빈 자막 케이스 테스트 (mock 재설정 필요)
        mock_clean_filename.reset_mock()
        mock_document.reset_mock()
        mock_doc_instance.reset_mock()
        mock_file_open.reset_mock()
        mock_clean_filename.return_value = "Test_Title_Empty" # 다른 파일 이름 사용

        result_empty = create_script_document([], "Empty Title", self.output_dir) # 제목도 변경
        self.assertTrue(os.path.basename(result_empty).startswith("Test_Title_Empty"))
        self.assertTrue(result_empty.endswith("_전체스크립트.docx"))
        mock_doc_instance.save.assert_called_once()
        mock_file_open.assert_called_once() # TXT 파일도 생성되는지 확인

    @patch('youtube_transcript_generator.document_generator.clean_filename')
    @patch('youtube_transcript_generator.document_generator.Document')
    @patch('builtins.open', new_callable=mock_open) # TXT 파일 쓰기를 위한 mock 추가
    def test_create_timestamp_document(self, mock_file_open, mock_document, mock_clean_filename):
        """create_timestamp_document 함수 테스트 (TXT 파일 생성 포함)."""
        # Mock 설정
        mock_clean_filename.return_value = "Test_Title"
        mock_doc_instance = MagicMock()
        mock_document.return_value = mock_doc_instance

        # 기본 케이스 테스트
        result_docx = create_timestamp_document(self.test_captions, self.title, self.output_dir)

        # DOCX 검증
        mock_clean_filename.assert_called_with(self.title)
        mock_document.assert_called_once()
        expected_docx_path = os.path.join(self.output_dir, "Test_Title_타임스탬프.docx")
        mock_doc_instance.save.assert_called_once_with(expected_docx_path)
        self.assertEqual(result_docx, expected_docx_path)

        # TXT 검증
        expected_txt_path = os.path.join(self.output_dir, "Test_Title_타임스탬프.txt")
        mock_file_open.assert_called_once_with(expected_txt_path, 'w', encoding='utf-8')

    def test_refine_script(self):
        """refine_script 함수 테스트 (최신 로직 기준)."""
        test_cases = [
            # 기본 정제 및 중복 제거
            (
                "[음악] Hello world. Hello world. This is a test. [음악] This is a test.",
                "Hello world. This is a test." # 원본 구두점 유지
            ),
            # 빈 텍스트
            ("", ""),
            # 연속된 마침표 및 문장 부호 처리
            ("Hello... World..?! Test.", "Hello. World?! Test."), # 연속 마침표는 하나로, 다른 부호는 유지
            # 공백 처리
            ("  Hello  .  World  .  ", "Hello. World."),
            # 중복 문장 제거 (구두점 포함)
            (
                "First sentence. Second sentence. First sentence. Third sentence.",
                "First sentence. Second sentence. Third sentence."
            ),
            # 특수 문자 및 태그 처리
            (
                "[음악] Test! [박수] Test? [웃음] Test.",
                "Test! Test? Test." # 원본 구두점 유지
            ),
            # 한글 텍스트 및 중복
            (
                "[음악] 안녕하세요. 안녕하세요. 테스트입니다. [박수] 테스트입니다.",
                "안녕하세요. 테스트입니다." # 원본 구두점 유지
            ),
            # 문장 부호 없는 경우 (현재 로직은 부호 추가 안 함)
            ("Sentence one Sentence two Sentence one", "Sentence one Sentence two"),
            # 다양한 문장 부호
            ("Question? Answer. Exclamation!", "Question? Answer. Exclamation!"),
        ]

        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                actual = refine_script(input_text)
                self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()