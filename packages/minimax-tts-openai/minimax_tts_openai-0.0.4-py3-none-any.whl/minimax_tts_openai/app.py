import os
import time
import json
import subprocess
import logging
from typing import Optional, Dict, Any, Iterator

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import StreamingResponse
import requests
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# We'll initialize the config when the app starts
config = None

def initialize_config():
    """Initialize the configuration when the app starts"""
    global config
    from .config import Config
    try:
        config = Config()
        logger.info("Configuration initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize configuration: {e}")
        raise

app = FastAPI(
    title="Minimax TTS Proxy",
    description="A proxy service that converts Minimax TTS API to OpenAI-compatible format",
    version="1.0"
)

# Initialize config when the app starts
@app.on_event("startup")
async def startup_event():
    initialize_config()

class TTSRequest(BaseModel):
    model: Optional[str] = None
    input: str
    voice: Optional[str] = None
    response_format: Optional[str] = "mp3"
    speed: Optional[float] = None
    stream: Optional[bool] = False

@app.post("/v1/audio/speech")
async def create_speech(
    request: TTSRequest,
    authorization: Optional[str] = Header(None)
):
    """OpenAI兼容的TTS端点"""
    logger.info(f"Received TTS request for model: {request.model}, voice: {request.voice}")
    
    # Ensure config is initialized
    if config is None:
        logger.error("Configuration not initialized")
        raise HTTPException(status_code=500, detail="Configuration not initialized")
    
    # API密钥验证
    if config.API_KEYS:
        if not authorization or not authorization.startswith("Bearer "):
            logger.warning("Unauthorized access attempt - missing or invalid Authorization header")
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        api_key = authorization.split(" ")[1]
        if api_key not in config.API_KEYS:
            logger.warning("Access forbidden for API key")
            raise HTTPException(status_code=403, detail="Forbidden")
    
    # 验证请求参数
    if request.response_format not in config.SUPPORTED_FORMATS:
        logger.warning(f"Unsupported format requested: {request.response_format}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Supported: {config.SUPPORTED_FORMATS}"
        )
    
    # 构建Minimax请求
    minimax_url = f"https://api.minimax.chat/v1/t2a_v2?GroupId={config.MINIMAX_GROUP_ID}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.MINIMAX_API_KEY}"
    }
    
    body = {
        "model": request.model or config.DEFAULT_MODEL,
        "text": request.input,
        "stream": request.stream,
        "voice_setting": {
            "voice_id": request.voice or config.DEFAULT_VOICE,
            "speed": request.speed if request.speed is not None else config.DEFAULT_SPEED,
            "vol": config.DEFAULT_VOLUME,
            "pitch": config.DEFAULT_PITCH,
            "emotion": config.DEFAULT_EMOTION
        },
        "audio_setting": {
            "sample_rate": config.DEFAULT_SAMPLE_RATE,
            "bitrate": config.DEFAULT_BITRATE,
            "format": request.response_format,
            "channel": config.DEFAULT_CHANNEL
        }
    }
    
    logger.info(f"Sending request to Minimax API for model: {body['model']}, voice: {body['voice_setting']['voice_id']}")
    
    # 流式响应
    if request.stream:
        logger.info("Processing streaming response")
        def generate():
            try:
                response = requests.post(
                    minimax_url,
                    headers=headers,
                    json=body,
                    stream=True
                )
                logger.info(f"Minimax API response status: {response.status_code}")
                
                if response.status_code != 200:
                    logger.error(f"Minimax API error: {response.status_code}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Minimax API error: {response.status_code}"
                    )
                
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        yield chunk
            except Exception as e:
                logger.error(f"Error during streaming: {e}")
                raise
        
        return StreamingResponse(
            generate(),
            media_type=f"audio/{request.response_format}"
        )
    
    # 非流式响应
    else:
        logger.info("Processing non-streaming response")
        try:
            response = requests.post(minimax_url, headers=headers, json=body)
            logger.info(f"Minimax API response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Minimax API error: {response.status_code}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Minimax API error: {response.status_code}"
                )
            
            response_json = response.json()
            
            audio_data = response_json.get("data", {}).get("audio", "")
            if not audio_data:
                logger.error("No audio data received from Minimax API")
                raise HTTPException(
                    status_code=500,
                    detail="No audio data received from Minimax API"
                )
            
            decoded_audio = bytes.fromhex(audio_data)
            logger.info("Successfully processed audio data")
            return StreamingResponse(
                iter([decoded_audio]),
                media_type=f"audio/{request.response_format}"
            )
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error during TTS processing: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )

@app.get("/v1/audio/voices")
async def list_voices():
    """获取可用的音色列表"""
    # Ensure config is initialized
    if config is None:
        raise HTTPException(status_code=500, detail="Configuration not initialized")
        
    voices = []
    for voice_id, voice_info in config.SUPPORTED_VOICES.items():
        voices.append({
            "voice_id": voice_id,
            **voice_info
        })
    return {"voices": voices}

@app.get("/v1/audio/models")
async def list_models():
    """获取可用的模型列表"""
    # Ensure config is initialized
    if config is None:
        raise HTTPException(status_code=500, detail="Configuration not initialized")
        
    models = []
    for model_id, model_name in config.SUPPORTED_MODELS.items():
        models.append({
            "model_id": model_id,
            "name": model_name
        })
    return {"models": models}