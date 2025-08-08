# MiniMax TTS 到 OpenAI API 代理

这个项目提供了一个代理服务，将 MiniMax TTS API 转换为与 OpenAI 兼容的格式，使您能够将 MiniMax 的文本转语音功能与为 OpenAI API 设计的工具和库一起使用。

## 特性

- OpenAI 兼容的 TTS API 端点
- 支持多种语音和模型
- 流式和非流式音频响应
- API 密钥认证
- 从 MiniMax API 动态获取语音列表
- 可配置的默认设置

## 安装

1. 克隆仓库：
   ```bash
   git clone https://github.com/Moha-Master/MiniMax-TTS-OpenAI.git
   cd MiniMax-TTS-OpenAI
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 通过复制 `config.yaml.example` 到 `config.yaml` 并使用您的 MiniMax API 凭据和其他设置进行编辑来配置服务。

4. 运行服务：
   ```bash
   uvicorn minimax_tts_openai.app:app --host 0.0.0.0 --port 8000
   ```

## 作为 pip 包安装

您也可以将此项目作为 pip 包安装：

```bash
pip install -e .
```

安装后，您可以使用以下命令运行服务：

```bash
minimax-tts-openai --dir /path/to/config --host 0.0.0.0 --port 8000
```

参数说明：
- `--dir`: 工作目录，从中读取 config.yaml（默认：~/.config/minimax-tts-openai/）
- `--host`: 绑定的主机地址（默认：127.0.0.1）
- `--port`: 绑定的端口（默认：8000）

## 配置

在希望的工作目录中创建一个基于 `config.yaml.example` 的 `config.yaml` 文件，包含您的 MiniMax API 凭据和其他设置。服务会从 `~/.config/minimax-tts-openai/` 或设置的 `--dir` 中读取 `config.yaml`。

如果指定的目录中没有 `config.yaml` 文件，程序会提示您需要从 `config.yaml.example` 复制并编辑配置文件。

配置选项：
- `minimax.group_id`: 您的 MiniMax 组 ID
- `minimax.api_key`: 您的 MiniMax API 密钥
- `api_keys`: 用于认证的 API 密钥列表
- `defaults`: 默认参数值（语音、模型、速度等）
- `audio`: 音频设置（采样率、比特率、声道）
- `voice_fetching`: 音色获取配置（voice_type 参数）
- `supported`: 支持的格式和模型

语音列表在启动时从 MiniMax API 自动获取。

## API 端点

- `POST /v1/audio/speech`: 从文本生成语音（OpenAI 兼容）
- `GET /v1/audio/voices`: 列出可用的语音
- `GET /v1/audio/models`: 列出可用的模型
