import os
import yaml
import requests
import logging
from typing import Set, Dict, Any
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        # 从YAML文件加载配置
        self._load_config()
    
    def _load_config(self):
        # 读取YAML配置文件（始终从当前工作目录读取）
        config_path = "config.yaml"
        
        logger.info(f"Loading configuration from {config_path}")
        
        if not os.path.exists(config_path):
            # 如果没有config.yaml文件，直接抛出异常
            error_msg = f"Configuration file {config_path} not found. Please create it from config.yaml.example"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        # Minimax API 配置
        self.MINIMAX_GROUP_ID = config_data["minimax"]["group_id"]
        self.MINIMAX_API_KEY = config_data["minimax"]["api_key"]
        logger.info("Minimax API configuration loaded")
        
        # API 密钥认证
        self.API_KEYS: Set[str] = set(config_data["api_keys"])
        logger.info(f"Loaded {len(self.API_KEYS)} API keys for authentication")
        
        # 默认参数配置
        defaults = config_data["defaults"]
        self.DEFAULT_VOICE = defaults["voice"]
        self.DEFAULT_MODEL = defaults["model"]
        self.DEFAULT_SPEED = float(defaults["speed"])
        self.DEFAULT_VOLUME = int(defaults["volume"])
        self.DEFAULT_PITCH = int(defaults["pitch"])
        self.DEFAULT_EMOTION = defaults["emotion"]
        logger.info("Default parameters loaded")
        
        # 音频设置默认值
        audio = config_data["audio"]
        self.DEFAULT_SAMPLE_RATE = int(audio["sample_rate"])
        self.DEFAULT_BITRATE = int(audio["bitrate"])
        self.DEFAULT_CHANNEL = int(audio["channel"])
        logger.info("Audio settings loaded")
        
        # 音色获取配置
        voice_fetching = config_data.get("voice_fetching", {})
        self.VOICE_TYPE = voice_fetching.get("voice_type", "all")
        logger.info(f"Voice fetching configuration: {self.VOICE_TYPE}")
        
        # 支持的格式和模型
        supported = config_data["supported"]
        self.SUPPORTED_FORMATS = supported["formats"]
        self.SUPPORTED_MODELS = supported["models"]
        logger.info(f"Supported formats: {self.SUPPORTED_FORMATS}")
        logger.info("Supported models loaded")
        
        # 动态获取音色列表
        logger.info("Fetching supported voices from Minimax API")
        self.SUPPORTED_VOICES = self._fetch_voices()
        logger.info(f"Fetched {len(self.SUPPORTED_VOICES)} voices")
    
    def _fetch_voices(self) -> Dict[str, Any]:
        """从MiniMax API动态获取音色列表"""
        if not self.MINIMAX_API_KEY:
            logger.warning("MINIMAX_API_KEY not set, using empty voices list")
            return {}
            
        try:
            # 使用新的API端点获取音色列表
            url = "https://api.minimaxi.com/v1/get_voice"
            headers = {
                "Authorization": f"Bearer {self.MINIMAX_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "voice_type": self.VOICE_TYPE
            }
            
            logger.info("Fetching voices from Minimax API")
            response = requests.post(url, headers=headers, json=data)
            logger.info(f"Voice fetching response status: {response.status_code}")
            
            if response.status_code == 200:
                voices_data = response.json()
                voices = {}
                
                # 处理系统预定义音色
                for voice in voices_data.get("system_voice", []):
                    voice_id = voice.get("voice_id")
                    if voice_id:
                        voices[voice_id] = {
                            "name": voice.get("voice_name", ""),
                            "category": "system",
                            "description": voice.get("description", [])
                        }
                
                # 处理音色快速复刻
                for voice in voices_data.get("voice_cloning", []):
                    voice_id = voice.get("voice_id")
                    if voice_id:
                        voices[voice_id] = {
                            "name": voice_id,
                            "category": "cloning",
                            "description": voice.get("description", []),
                            "created_time": voice.get("created_time", "")
                        }
                
                # 处理音色生成
                for voice in voices_data.get("voice_generation", []):
                    voice_id = voice.get("voice_id")
                    if voice_id:
                        voices[voice_id] = {
                            "name": voice_id,
                            "category": "generation",
                            "description": voice.get("description", []),
                            "created_time": voice.get("created_time", "")
                        }
                
                # 处理音乐生成音色
                for voice in voices_data.get("music_generation", []):
                    voice_id = voice.get("voice_id")
                    instrumental_id = voice.get("instrumental_id")
                    if voice_id and instrumental_id:
                        full_voice_id = f"{voice_id}_{instrumental_id}"
                        voices[full_voice_id] = {
                            "name": full_voice_id,
                            "category": "music",
                            "description": voice.get("description", []),
                            "created_time": voice.get("created_time", "")
                        }
                
                logger.info(f"Successfully fetched {len(voices)} voices")
                return voices
            else:
                logger.warning(f"Failed to fetch voices, status code: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"Error fetching voices: {e}")
            return {}
