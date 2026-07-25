"""
MidiaSaver — backend de extração de mídia.

Suporta: Instagram, TikTok, Twitter/X, YouTube, Facebook, Pinterest
(qualquer site suportado pelo yt-dlp, na prática).

Rodar localmente:
    pip install -r requirements.txt
    uvicorn main:app --reload

Deploy: veja README.md (Render.com, free tier).
"""

import re
import logging
from typing import Optional

import yt_dlp
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MidiaSaver API")

# Em produção, troque "*" pela URL exata do seu GitHub Pages
# (ex: "https://seu-usuario.github.io") por segurança.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

HEADERS_NAVEGADOR = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

PLATAFORMAS = {
    "instagram.com": "instagram",
    "tiktok.com": "tiktok",
    "twitter.com": "twitter",
    "x.com": "twitter",
    "youtube.com": "youtube",
    "youtu.be": "youtube",
    "facebook.com": "facebook",
    "fb.watch": "facebook",
    "pinterest.com": "pinterest",
    "pin.it": "pinterest",
}


class RespostaMidia(BaseModel):
    plataforma: str
    tipo: str  # "video" ou "imagem"
    titulo: Optional[str] = None
    url_midia: str
    thumbnail: Optional[str] = None
    aviso: Optional[str] = None


def detectar_plataforma(url: str) -> str:
    for dominio, nome in PLATAFORMAS.items():
        if dominio in url:
            return nome
    return "desconhecida"


def extrair_com_ytdlp(url: str) -> Optional[RespostaMidia]:
    """Tenta extrair via yt-dlp (cobre vídeo em todas as plataformas suportadas)."""
    opcoes = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "format": "best[ext=mp4]/best",
        "http_headers": HEADERS_NAVEGADOR,
    }
    try:
        with yt_dlp.YoutubeDL(opcoes) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        logger.warning("yt-dlp falhou para %s: %s", url, e)
        return None

    if not info:
        return None

    url_midia = info.get("url")
    if not url_midia:
        return None

    aviso = None
    if info.get("ext") in ("mp4",) and info.get("vcodec") != "none" and info.get("acodec") == "none":
        aviso = "Este formato pode não ter áudio (vídeo e áudio separados na origem)."

    return RespostaMidia(
        plataforma=detectar_plataforma(url),
        tipo="video",
        titulo=info.get("title"),
        url_midia=url_midia,
        thumbnail=info.get("thumbnail"),
        aviso=aviso,
    )


def extrair_imagem_pinterest(url: str) -> Optional[RespostaMidia]:
    """Fallback para pins de imagem do Pinterest, que o yt-dlp não cobre bem."""
    import requests
    from bs4 import BeautifulSoup

    resposta = requests.get(url, headers=HEADERS_NAVEGADOR, timeout=15)
    if resposta.status_code != 200:
        return None

    soup = BeautifulSoup(resposta.text, "html.parser")
    og_image = soup.find("meta", property="og:image")
    if not og_image or not og_image.get("content"):
        return None

    url_original = re.sub(r"/\d+x(/|$)", "/originals/", og_image["content"])
    titulo_tag = soup.find("meta", property="og:title")

    return RespostaMidia(
        plataforma="pinterest",
        tipo="imagem",
        titulo=titulo_tag["content"] if titulo_tag else None,
        url_midia=url_original,
        thumbnail=og_image["content"],
    )


@app.get("/")
def raiz():
    return {"status": "ok", "servico": "MidiaSaver API"}


@app.get("/api/extract", response_model=RespostaMidia)
def extrair(url: str = Query(..., description="Link do post/vídeo/pin")):
    if not url.startswith("http"):
        raise HTTPException(400, "URL inválida.")

    plataforma = detectar_plataforma(url)
    if plataforma == "desconhecida":
        raise HTTPException(400, "Plataforma não suportada.")

    resultado = extrair_com_ytdlp(url)

    if not resultado and plataforma == "pinterest":
        resultado = extrair_imagem_pinterest(url)

    if not resultado:
        raise HTTPException(
            422,
            "Não consegui extrair mídia desse link. Pode ser conteúdo privado, "
            "removido, ou a plataforma mudou algo no site.",
        )

    return resultado
