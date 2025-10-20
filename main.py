""" main.py """

import os
import smtplib
import ssl
import logging
from email.message import EmailMessage
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# Carrega variáveis de ambiente do .env
load_dotenv()

app = FastAPI()

# CORS Config (ajuste allowed_origins para seu domínio de produção)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, troque para seu domínio!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

EMAIL_SENDER = os.getenv("EMAIL_SENDER", "ferzion.dev@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "warley.ferraz.wf@gmail.com")

def is_valid_email(email: str) -> bool:
    import re
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/contato/")
async def contato(request: Request):
    data = await request.json()
    nome = data.get("nome", "").strip()
    email = data.get("email", "").strip()
    mensagem = data.get("mensagem", "").strip()

    # Validação dos campos
    if not nome or not email or not mensagem:
        return JSONResponse(
            {"msg": "Por favor, preencha todos os campos."},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    if not is_valid_email(email):
        return JSONResponse(
            {"msg": "Por favor, insira um e-mail válido."},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Validação de variáveis de ambiente
    missing_envs = []
    if not EMAIL_SENDER:
        missing_envs.append("EMAIL_SENDER")
    if not EMAIL_PASSWORD:
        missing_envs.append("EMAIL_PASSWORD")
    if not EMAIL_RECEIVER:
        missing_envs.append("EMAIL_RECEIVER")

    if missing_envs:
        logging.error(f"Faltando variáveis: {missing_envs}")
        return JSONResponse(
            {"msg": f"Erro de configuração: faltando variável(éis) {', '.join(missing_envs)} no .env"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    subject = f"Contato do Portfólio: {nome}"
    body = f"""
Você recebeu uma nova mensagem pelo portfólio:

Nome: {nome}
E-mail: {email}
Mensagem:
{mensagem}
    """

    em = EmailMessage()
    em["From"] = EMAIL_SENDER
    em["To"] = EMAIL_RECEIVER
    em["Subject"] = subject
    em.set_content(body)

    # Envia e-mail via Gmail SMTP
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(em)
        return JSONResponse({"msg": "Mensagem enviada com sucesso!"})
    except Exception as e:
        logging.exception("Erro ao enviar e-mail")
        return JSONResponse(
            {"msg": "Erro ao enviar mensagem, tente novamente mais tarde."},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )