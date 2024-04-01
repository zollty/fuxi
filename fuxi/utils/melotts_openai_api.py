import io
import os
from melo.api import TTS
from fastapi import FastAPI, Response
from pydantic import BaseModel
from typing import Optional

# 配置nltk 模型存储路径
import nltk

NLTK_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__)), "nltk_data"))
nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path


class SpeechRequest(BaseModel):
    input: str
    voice: str = 'ZH'
    prompt: Optional[str] = ''
    language: Optional[str] = 'ZH'
    model: Optional[str] = 'ZH'
    response_format: Optional[str] = 'wav'
    speed: Optional[float] = 1.0


app = FastAPI()
device = 'auto'

models = {
    'EN': TTS(language='EN', device=device),
    'ES': TTS(language='ES', device=device),
    'FR': TTS(language='FR', device=device),
    'ZH': TTS(language='ZH', device=device),
    'JP': TTS(language='JP', device=device),
    'KR': TTS(language='KR', device=device),
}

default_text_dict = {
    'EN': 'The field of text-to-speech has seen rapid development recently.',
    'ES': 'El campo de la conversión de texto a voz ha experimentado un rápido desarrollo recientemente.',
    'FR': 'Le domaine de la synthèse vocale a connu un développement rapide récemment',
    'ZH': 'text-to-speech 领域近年来发展迅速',
    'JP': 'テキスト読み上げの分野は最近急速な発展を遂げています',
    'KR': '최근 텍스트 음성 변환 분야가 급속도로 발전하고 있습니다.',
}


@app.post("/v1/audio/speech")
def text_to_speech(speechRequest: SpeechRequest):
    bio = io.BytesIO()
    models[speechRequest.language].tts_to_file(speechRequest.input,
                                               models[speechRequest.language].hps.data.spk2id[speechRequest.voice],
                                               bio, speed=speechRequest.speed, format=speechRequest.response_format)
    return Response(content=bio.getvalue(),
                    media_type=f"audio/{speechRequest.response_format}")


if __name__ == '__main__':
    import argparse
    from fastapi_tool import run_api

    parser = argparse.ArgumentParser(prog='Melo TTS', description='Melo TTS API')
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=6007)
    parser.add_argument(
        "-v",
        "--verbose",
        help="增加log信息",
        dest="verbose",
        type=bool,
        default=False,
    )
    # 初始化消息
    args = parser.parse_args()
    host = args.host
    port = args.port
    log_level = "info"
    if host == "localhost" or host == "127.0.0.1":
        host = "0.0.0.0"
    if args.verbose:
        log_level = "debug"
    run_api(app, host=host, port=port, log_level=log_level)
