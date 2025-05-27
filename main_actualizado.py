
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
import os
from openai import OpenAI
import PyPDF2
from io import BytesIO

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/form", methods=["POST"])
def form():
    option = request.form.get("option")
    return render_template("form.html", option=option)

@app.route("/result", methods=["POST"])
def result():
    option = request.form.get("option")
    comunidad = request.form.get("comunidad")
    hijos = request.form.get("hijos")
    salario = request.form.get("salario")
    pagadores = request.form.get("pagadores")
    edad = request.form.get("edad")
    alquiler = request.form.get("alquiler")
    hipoteca = request.form.get("hipoteca")
    discapacidad = request.form.get("discapacidad")
    pension = request.form.get("pension")

    extracted_text = ""
    if option == "subir":
        pdf = request.files.get("borrador_pdf")
        if pdf:
            reader = PyPDF2.PdfReader(BytesIO(pdf.read()))
            extracted_text = "\n".join(page.extract_text() for page in reader.pages)

    prompt = f"""
Eres un asesor fiscal. Analiza los siguientes datos y/o texto del borrador de la renta. Comprueba:
1. Si están aplicadas las deducciones correctas.
2. Si faltan deducciones según la comunidad autónoma ({comunidad}), como gimnasio en Valencia o cuidadora de hijos en Galicia.
3. Si sería mejor presentar complementaria.

Datos del usuario:
- Comunidad: {comunidad}
- Hijos: {hijos}
- Salario bruto: {salario}
- Nº pagadores: {pagadores}
- Edad: {edad}
- Alquiler: {alquiler}
- Hipoteca: {hipoteca}
- Discapacidad: {discapacidad}
- Plan pensiones: {pension}

Texto extraído del borrador:
{extracted_text}

Genera una respuesta clara y amable con la estimación de ahorro, si aplica. Añade una llamada a la acción como: “¿Quieres que uno de nuestros expertos la revise contigo?”
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    result_text = response.choices[0].message.content
    return render_template("result.html", result=result_text)

if __name__ == "__main__":
    app.run(debug=True)
