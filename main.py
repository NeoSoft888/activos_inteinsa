from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from db import conectar
import uvicorn

app = FastAPI()

# Montar carpeta de archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- INICIO / REGISTRO DE ACTIVO ---
@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "success": False
    })

@app.post("/", response_class=HTMLResponse)
async def form_post(request: Request,
                    codigo: str = Form(...),
                    descripcion: str = Form(...),
                    modelo: str = Form(...),
                    serial: str = Form(...),
                    usuario: str = Form(...),
                    equipo: str = Form(...),
                    observaciones: str = Form("")):
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO activos (codigo, descripcion, modelo, serial, usuario, equipo, observaciones, asignado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
            ON CONFLICT (codigo) DO UPDATE SET
                descripcion = EXCLUDED.descripcion,
                modelo = EXCLUDED.modelo,
                serial = EXCLUDED.serial,
                usuario = EXCLUDED.usuario,
                equipo = EXCLUDED.equipo,
                observaciones = EXCLUDED.observaciones,
                asignado = TRUE
        """, (codigo, descripcion, modelo, serial, usuario, equipo, observaciones))
        conn.commit()
        cur.close()
        conn.close()
        return templates.TemplateResponse("index.html", {
            "request": request,
            "success": True
        })
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "success": False,
            "error": str(e)
        })

# --- ASIGNAR ACTIVO ---
@app.get("/asignar", response_class=HTMLResponse)
async def asignar_get(request: Request):
    return templates.TemplateResponse("asignar.html", {"request": request, "success": False})

@app.post("/asignar", response_class=HTMLResponse)
async def asignar_post(request: Request,
                       codigo: str = Form(...),
                       modelo: str = Form(""),
                       serial: str = Form(""),
                       usuario: str = Form(...),
                       equipo: str = Form(...),
                       observaciones: str = Form("")):
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            UPDATE activos
            SET modelo = COALESCE(NULLIF(%s, ''), modelo),
                serial = COALESCE(NULLIF(%s, ''), serial),
                usuario = %s,
                equipo = %s,
                observaciones = %s,
                asignado = TRUE
            WHERE codigo = %s
        """, (modelo, serial, usuario, equipo, observaciones, codigo))
        conn.commit()
        cur.close()
        conn.close()
        return templates.TemplateResponse("asignar.html", {
            "request": request,
            "success": True
        })
    except Exception as e:
        return templates.TemplateResponse("asignar.html", {
            "request": request,
            "success": False,
            "error": str(e)
        })

# --- BUSCAR ACTIVO ---
@app.get("/buscar", response_class=HTMLResponse)
async def buscar_get(request: Request):
    return templates.TemplateResponse("buscar.html", {
        "request": request,
        "activos": [],
        "criterio": ""
    })

@app.post("/buscar", response_class=HTMLResponse)
async def buscar_post(request: Request, criterio: str = Form(...)):
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            SELECT codigo, descripcion, modelo, serial, usuario, equipo, observaciones, asignado
            FROM activos
            WHERE usuario ILIKE %s OR equipo ILIKE %s
        """, (f"%{criterio}%", f"%{criterio}%"))
        resultados = cur.fetchall()
        cur.close()
        conn.close()

        return templates.TemplateResponse("buscar.html", {
            "request": request,
            "activos": resultados,
            "criterio": criterio
        })
    except Exception as e:
        return templates.TemplateResponse("buscar.html", {
            "request": request,
            "activos": [],
            "criterio": criterio,
            "error": str(e)
        })

# --- EJECUCIÓN LOCAL ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
