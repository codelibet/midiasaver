# MidiaSaver

Site pra baixar vídeos/imagens de Instagram, TikTok, Twitter/X, YouTube,
Facebook e Pinterest. Frontend estático (GitHub Pages) + backend com yt-dlp
(Render, free tier) — **tudo num repositório só**.

## Estrutura do repositório

```
midiasaver/
├── render.yaml          ← configuração de deploy do Render (fica na raiz)
├── backend/              ← API em FastAPI + yt-dlp
│   ├── main.py
│   ├── requirements.txt
│   └── runtime.txt
└── docs/                 ← site estático (GitHub Pages serve direto desta pasta)
    ├── index.html
    ├── manifest.json
    └── icons/
```

## Parte 1 — Subir o repositório

1. Crie **um único repositório** no GitHub, ex: `midiasaver`.
2. Suba todo o conteúdo desta pasta (`render.yaml`, `backend/`, `docs/`,
   este `README.md`) pra raiz do repositório, mantendo essa estrutura de
   pastas.

## Parte 2 — Deploy do backend (Render)

1. Crie conta grátis em [render.com](https://render.com) (dá pra logar
   direto com GitHub).
2. No painel: **New → Blueprint** (não "Web Service" dessa vez — o
   Blueprint lê o `render.yaml` da raiz automaticamente).
3. Conecte o repositório `midiasaver`.
4. O Render vai ler o `render.yaml`, ver o `rootDir: backend` e configurar
   tudo sozinho: build, start command, versão do Python. Clique em
   **Apply** / **Create**.
5. O primeiro deploy leva uns 3-5 minutos. Quando terminar, copie a URL
   gerada — algo como `https://midiasaver-api.onrender.com`.
6. Teste no navegador: a URL raiz deve responder `{"status":"ok",...}`.

**Sobre o "sono" do free tier:** depois de 15 minutos sem receber
requisições, o Render coloca o serviço pra dormir. A próxima requisição
demora ~30-50 segundos pra "acordar" — o frontend já avisa o usuário disso.

## Parte 3 — Configurar e publicar o frontend (GitHub Pages)

1. No **mesmo repositório**, abra `docs/index.html` e troque esta linha:
   ```js
   const API_BASE = "https://SEU-BACKEND.onrender.com";
   ```
   pela URL real do backend que você copiou no passo anterior (sem barra
   no final).
2. No GitHub: **Settings → Pages** → em "Source" escolha a branch `main`
   e a pasta **`/docs`** (não `/root` — é por isso que a pasta se chama
   `docs`, o GitHub Pages reconhece esse nome nativamente sem precisar de
   configuração extra).
3. Espere 1-2 minutos. Sua URL final:
   `https://SEU-USUARIO.github.io/midiasaver/`
4. Abra no Chrome do Android e teste colando links das plataformas
   suportadas.

## Atualizando depois

Como é tudo no mesmo repo, qualquer commit novo:
- Se mexeu em algo dentro de `backend/` → Render redeploya sozinho.
- Se mexeu em algo dentro de `docs/` → GitHub Pages atualiza sozinho.
Não precisa fazer nada manual em nenhum dos dois depois da configuração
inicial.

## Limitações que você vai encontrar (sendo honesto)

- **YouTube:** o modo atual (`format: "best"`) pega um único arquivo já com
  vídeo+áudio juntos, mas isso limita a qualidade máxima (geralmente até
  720p, dependendo do vídeo) — pra pegar 1080p+ seria necessário baixar
  vídeo e áudio separados e juntar com ffmpeg no servidor, o que é mais
  pesado pro free tier do Render.
- **Instagram/Facebook:** posts privados ou que exigem login não vão
  funcionar — só conteúdo público. Login programático nessas plataformas
  quebra os Termos de Serviço delas com bastante frequência.
- **Twitter/X:** mudanças recentes de API tornaram a extração mais instável;
  se parar de funcionar, normalmente é questão de atualizar o yt-dlp.
- **Stories** (Instagram/Facebook) não são tratadas nessa versão, só posts
  e vídeos permanentes.
- Todas essas plataformas mudam a estrutura do site com frequência. Quando
  algo parar de funcionar, o primeiro passo é sempre atualizar a versão do
  `yt-dlp` (ele já está sem versão travada no `requirements.txt`, então
  um redeploy manual no Render já costuma puxar a versão mais nova).

