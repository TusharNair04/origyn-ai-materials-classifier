"""Translation agent for the Origyn application."""

import logging
from google.cloud import translate_v2 as translate
from ..models import PartInfoState
from ..config import get_service_account_path

logger = logging.getLogger(__name__)

def translating_agent_node(state: PartInfoState) -> PartInfoState:
    """
    Translate the query to English if it's in another language.
    
    Args:
        state: The current workflow state.
        
    Returns:
        Updated workflow state with translated query.
    """
    text = state["original_query"]
    logger.info(f"Translating query: {text}")
    
    try:
        service_account_path = get_service_account_path()
        translate_client = translate.Client.from_service_account_json(service_account_path)
        
        detection = translate_client.detect_language(text)
        text_language = detection["language"]
        
        logger.info(f"Detected language: {text_language}")
        
        translated_text = text
        
        if text_language != "en":
            translation_result = translate_client.translate(text, target_language="en")
            translated_text = translation_result["translatedText"]
            logger.info(f"Translated to: {translated_text}")
        else:
            logger.info("Query is already in English, no translation needed.")
        
        return {**state, "translated_query": translated_text, "error": None}
    except Exception as e:
        error_msg = f"Translation error: {str(e)}"
        logger.error(error_msg)
        return {**state, "error": error_msg}