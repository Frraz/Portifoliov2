import os
import smtplib
import ssl
from email.message import EmailMessage
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

# Carrega variáveis de ambiente do .env
load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates Jinja2
templates = Jinja2Templates(directory="templates")

# --- CONFIGURAÇÕES DE E-MAIL ---
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "ferzion.dev@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "warley.ferraz.wf@gmail.com")  # Atualizado para o e-mail de recebimento

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/contato/")
async def contato(request: Request):
    data = await request.json()
    nome = data.get("nome", "").strip()
    email = data.get("email", "").strip()
    mensagem = data.get("mensagem", "").strip()

    # Validação simples dos campos
    if not nome or not email or not mensagem:
        return JSONResponse(
            {"msg": "Por favor, preencha todos os campos."},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Validação das variáveis de ambiente críticas
    missing_envs = []
    if not EMAIL_SENDER:
        missing_envs.append("EMAIL_SENDER")
    if not EMAIL_PASSWORD:
        missing_envs.append("EMAIL_PASSWORD")
    if not EMAIL_RECEIVER:
        missing_envs.append("EMAIL_RECEIVER")

    if missing_envs:
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
        print("Erro ao enviar e-mail:", e)
        # Retorna o erro detalhado para facilitar debug em ambiente local
        return JSONResponse(
            {"msg": f"Erro ao enviar mensagem, tente novamente. Detalhe: {str(e)}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )