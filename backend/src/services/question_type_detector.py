"""
Question Type Detector - Auto-detects question type from structure and content
Uses heuristics to classify questions into appropriate template types
"""
import re
from typing import Tuple
from src.models.question import QuestionType, Question


class QuestionTypeDetector:
    """Auto-detect question type based on structure and content analysis"""

    @staticmethod
    def detect_type(question: Question) -> Tuple[QuestionType, dict]:
        """
        Analyze question structure and detect its type.
        Returns: (detected_type, metadata_dict)
        """
        text_lower = question.text.lower()
        answer_count = len(question.answer_options)
        
        # Check for specific patterns that indicate question type
        
        # 1. SCENARIO_SERIES: Contains "scenario", "case", "statement", "yes or no"
        if QuestionTypeDetector._is_scenario_series(text_lower, answer_count):
            return QuestionType.SCENARIO_SERIES, {"statement_count": 3}
        
        # 2. BUILD_LIST: Contains "order", "steps", "sequence", "arrange", etc.
        if QuestionTypeDetector._is_build_list(text_lower, question.answer_options):
            return QuestionType.BUILD_LIST, {"step_count": answer_count}
        
        # 3. DROP_DOWN_SELECTION: Contains blank/underscores or "fill in", "choose from dropdown"
        if QuestionTypeDetector._is_drop_down(text_lower, question.answer_options):
            return QuestionType.DROP_DOWN_SELECTION, {"blank_position": "auto-detect"}
        
        # 4. HOT_AREA: Contains "click", "image", "screenshot", "diagram", "portal"
        if QuestionTypeDetector._is_hot_area(text_lower, question.answer_options):
            return QuestionType.HOT_AREA, {"image_needed": True}
        
        # 5. DRAG_AND_DROP: Contains "match", "pair", "connect", "drag", and has even options
        if QuestionTypeDetector._is_drag_and_drop(text_lower, question.answer_options):
            return QuestionType.DRAG_AND_DROP, {"pair_count": answer_count // 2}
        
        # 6. MULTIPLE_RESPONSE: Multiple answers (marked with checkboxes/numbers in PDFs)
        if QuestionTypeDetector._is_multiple_response(text_lower, question.answer_options):
            return QuestionType.MULTIPLE_RESPONSE, {"correct_count": 2}  # Default to 2
        
        # 7. Default: MULTIPLE_CHOICE (single correct answer)
        return QuestionType.MULTIPLE_CHOICE, {}

    @staticmethod
    def _is_scenario_series(text: str, answer_count: int) -> bool:
        """Detect scenario-based questions"""
        scenario_keywords = [
            "scenario", "case study", "case", "situation", "situation:\n",
            "statement", "statements", "yes or no", "meet the goal",
            "does this solution", "does this", "requirement"
        ]
        return any(kw in text for kw in scenario_keywords) and answer_count >= 3

    @staticmethod
    def _is_build_list(text: str, options: list) -> bool:
        """Detect build/order sequence questions"""
        order_keywords = [
            "order", "sequence", "steps", "arrange", "arrange in order",
            "correct order", "which is the first", "next step", "following order",
            "1.", "2.", "3.", "-"  # Numbered/bulleted steps
        ]
        has_order_keyword = any(kw in text for kw in order_keywords)
        
        # Check if options look like steps (start with numbers or bullets)
        options_str = " ".join(options).lower()
        has_step_format = re.search(r"^\s*(1\.|2\.|3\.|step|•|-)", options_str, re.MULTILINE)
        
        return has_order_keyword or has_step_format

    @staticmethod
    def _is_drop_down(text: str, options: list) -> bool:
        """Detect fill-in-the-blank/dropdown questions"""
        dropdown_keywords = [
            "fill in", "blank", "___", "dropdown", "drop-down",
            "choose from", "select the term", "which term", "missing word",
            "sentence", "statement", "[blank]"
        ]
        has_dropdown_keyword = any(kw in text for kw in dropdown_keywords)
        
        # Check for blank indicators
        has_blank = "_" in text or "[" in text or "(" in text
        
        return has_dropdown_keyword or (has_blank and len(options) <= 5)

    @staticmethod
    def _is_hot_area(text: str, options: list) -> bool:
        """Detect click-on-image/hot-area questions"""
        hotarea_keywords = [
            "click", "image", "screenshot", "diagram", "portal",
            "where", "locate", "which area", "select the", "identify the",
            "point to", "indicates", "shown", "figure", "exhibit"
        ]
        has_hotarea_keyword = any(kw in text for kw in hotarea_keywords)
        
        # Check if options look like areas/labels
        options_str = " ".join(options).lower()
        is_location_option = any(keyword in options_str for keyword in [
            "area", "section", "box", "button", "field", "pane", "option"
        ])
        
        return has_hotarea_keyword and is_location_option

    @staticmethod
    def _is_drag_and_drop(text: str, options: list) -> bool:
        """Detect matching/pairing questions"""
        dragdrop_keywords = [
            "match", "pair", "connect", "associate", "drag",
            "link", "corresponding", "maps to", "relates to"
        ]
        has_dragdrop_keyword = any(kw in text for kw in dragdrop_keywords)
        
        # Even number of options suggests pairs
        is_even_options = len(options) % 2 == 0 and len(options) >= 4
        
        return has_dragdrop_keyword or (is_even_options and has_dragdrop_keyword)

    @staticmethod
    def _is_multiple_response(text: str, options: list) -> bool:
        """Detect multiple-response questions"""
        multiple_keywords = [
            "select all", "choose all", "multiple answers", "all that apply",
            "all of the following", "two or more", "select two", "correct answers"
        ]
        has_multiple_keyword = any(kw in text for kw in multiple_keywords)
        
        # Heuristic: if text explicitly says multiple, it's multiple response
        return has_multiple_keyword


class QuestionTypeUpdater:
    """Update existing questions with detected types"""

    @staticmethod
    async def update_question_type(question: Question) -> Question:
        """
        Update a question's type based on auto-detection.
        Preserves existing type if detection fails.
        """
        try:
            detected_type, metadata = QuestionTypeDetector.detect_type(question)
            question.question_type = detected_type
            # Merge with existing metadata if any
            if question.metadata:
                question.metadata.update(metadata)
            else:
                question.metadata = metadata
            return question
        except Exception as e:
            print(f"Error detecting type for question {question.question_id}: {e}")
            # Return question unchanged if detection fails
            return question
