import io, os, sys

# 获取当前脚本的绝对路径
__current_script_path = os.path.abspath(__file__)
# 将项目根目录添加到sys.path
runtime_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__current_script_path)))
sys.path.append(runtime_root_dir)

import edge_tts
from fastapi import FastAPI, Response
from pydantic import BaseModel
from typing import Optional


class SpeechRequest(BaseModel):
    input: str
    voice: str = 'zh-CN-YunxiNeural'
    # zh-TW-HsiaoYuNeural
    # zh-CN-YunyangNeural
    # zh-CN-shaanxi-XiaoniNeural
    prompt: Optional[str] = ''
    language: Optional[str] = 'ZH'
    model: Optional[str] = 'ZH'
    response_format: Optional[str] = 'mp3'
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
    app = FastAPI(title="伏羲AI TTS Server (edge)")

    @app.post("/v1/audio/speech")
    async def text_to_speech(speechRequest: SpeechRequest):
        bio = io.BytesIO()
        # format = None if speechRequest.response_format == 'wav' else speechRequest.response_format
        rt = (speechRequest.speed - 1.0) * 100
        rate = "+0%"
        if rt > 1:
            rate = "+" + rt + "%"
        elif rt < -1:
            rate = "-" + (0 - rt) + "%"
        communicate = edge_tts.Communicate(speechRequest.input, speechRequest.voice, rate)
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                bio.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                print(f"WordBoundary: {chunk}")

        return Response(content=bio.getvalue(),
                        media_type=f"audio/{speechRequest.response_format}")

    return app


if __name__ == '__main__':
    import argparse
    from fuxi.utils.fastapi_tool import run_api

    parser = argparse.ArgumentParser(prog='Melo TTS', description='Melo TTS API')
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=6008)
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
