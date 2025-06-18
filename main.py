from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Monta a pasta de estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configura os templates Jinja2
templates = Jinja2Templates(directory="templates")

# Rota principal
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Rota para o formulário de contato
@app.post("/contato/")
async def contato(request: Request):
    data = await request.json()
    # Aqui você pode tratar/salvar/enviar email com os dados recebidos
    return JSONResponse({"msg": "Mensagem recebida com sucesso!"})