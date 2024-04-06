import io, os, sys

# 获取当前脚本的绝对路径
__current_script_path = os.path.abspath(__file__)
# 将项目根目录添加到sys.path
runtime_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__current_script_path)))
sys.path.append(runtime_root_dir)

from melo.api import TTS
from fastapi import FastAPI, Response
from pydantic import BaseModel
from typing import Optional
from fuxi.utils.runtime_conf import init_nltk

init_nltk()


class SpeechRequest(BaseModel):
    input: str
    voice: str = 'ZH'
    prompt: Optional[str] = ''
    language: Optional[str] = 'ZH'
    model: Optional[str] = 'ZH'
    response_format: Optional[str] = 'wav'
    speed: Optional[float] = 1.0


default_text_dict = {
    'EN': 'The field of text-to-speech has seen rapid development recently.',
    'ES': 'El campo de la conversión de texto a voz ha experimentado un rápido desarrollo recientemente.',
    'FR': 'Le domaine de la synthèse vocale a connu un développement rapide récemment',
    'ZH': 'text-to-speech 领域近年来发展迅速',
    'JP': 'テキスト読み上げの分野は最近急速な発展を遂げています',
    'KR': '최근 텍스트 음성 변환 분야가 급속도로 발전하고 있습니다.',
}


def base_init_0(device):
    app = FastAPI(title="伏羲AI TTS Server (melo)")

    models = {
        'EN': TTS(language='EN', device=device),
        'ES': TTS(language='ES', device=device),
        'FR': TTS(language='FR', device=device),
        'ZH': TTS(language='ZH', device=device),
        'JP': TTS(language='JP', device=device),
        'KR': TTS(language='KR', device=device),
    }

    @app.post("/v1/audio/speech")
    def text_to_speech(speechRequest: SpeechRequest):
        bio = io.BytesIO()
        # format = None if speechRequest.response_format == 'wav' else speechRequest.response_format
        models[speechRequest.language].tts_to_file(speechRequest.input,
                                                   models[speechRequest.language].hps.data.spk2id[speechRequest.voice],
                                                   bio, speed=speechRequest.speed, format=speechRequest.response_format)
        return Response(content=bio.getvalue(),
                        media_type=f"audio/{speechRequest.response_format}")

    return app


if __name__ == '__main__':
    import argparse
    from fuxi.utils.fastapi_tool import run_api

    parser = argparse.ArgumentParser(prog='Melo TTS', description='Melo TTS API')
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=6007)
    parser.add_argument("--device", type=str, default="auto")
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

    app = base_init_0(args.device)

    from fuxi.utils.fastapi_tool import MakeFastAPIOffline

    MakeFastAPIOffline(app)
    run_api(app, host=host, port=port, log_level=log_level)
