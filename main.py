import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import pytz
from flask import Flask
from threading import Thread
from twilio.rest import Client

# Configuración de Twilio
TWILIO_ACCOUNT_SID = "AC3a8d94fa878f91570d4075024b1b33ee"  # Reemplaza con tu SID de Twilio
TWILIO_AUTH_TOKEN = "ab8445da9e30a48ed1a81d8cc7cd41c5"  # Reemplaza con tu token de autenticación de Twilio
TWILIO_PHONE_NUMBER = "+16814164395"  # Reemplaza con tu número de teléfono de Twilio

def enviar_sms(destinatario: str, valor: int) -> None:
    # Crear cliente de Twilio
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    # Mensaje a enviar
    mensaje = f"{destinatario} te ha enviado {valor} a tu Nequi, puedes ver el valor reflejado en la aplicación."

    try:
        # Enviar el SMS
        client.messages.create(
            to=destinatario,
            from_=TWILIO_PHONE_NUMBER,
            body=mensaje
        )
        logging.info(f"Mensaje enviado a {destinatario} con éxito.")
    except Exception as e:
        logging.error(f"Error al enviar el mensaje: {e}")
        

# Configuración básica del servidor Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "¡El bot está corriendo correctamente!"

def run_server():
    port = int(os.environ.get("PORT", 8080))  # Render asigna dinámicamente este puerto
    app.run(host="0.0.0.0", port=port)

# Ejecutar Flask en un hilo secundario
Thread(target=run_server).start()

# Configuración de logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Lista de IDs de usuarios autorizadoqs
USUARIOS_AUTORIZADOS = [7142146578, 7400707912, 7339703547, 6273674602, 5461399002, 5475503020, 6816220486, 6625965336, 7674096632, 6903942837, 5355499275, 6595190536, 5238277683, 7382698094, 8140244372, 7601814018, 7725197596, 7771334101, 6929700217, 7179881530]  # Sustituye con los IDs reales

# Configuración de rutas de plantillas y salidas
FONT_PATH = "fuente.ttf"  # Asegúrate de que la ruta sea correcta
FONT_MOVIMIENTOS_PATH = "fuente.ttf"  # Asegúrate de que la ruta sea correcta
COMPROBANTES = {
    "comprobante1": {
        "template": "plantilla1.jpeg",
        "output": "comprobante1_generado.png",
        "styles": {
            "nombre": {"size": 28, "color": "#1b0b19", "pos": (570, 572)},
            "telefono": {"size": 28, "color": "#1b0b19", "pos": (495, 695)},
            "valor1": {"size": 28, 
                       "color": "#1b0b19", "pos":(630, 632)},
            "fecha": {"size": 28, "color": "#1b0b19", "pos": (60, 790)},
        },
    },
    "comprobante2": {
        "template": "plantilla2.jpeg",
        "output": "comprobante2_generado.png",
        "styles": {
            "nombre": {"size": 28, "color": "#1b0b19", "pos": (86, 575)},
            "telefono": {"size": 28, "color": "#1b0b19", "pos": (86, 735)},
            "valor1": {"size": 28, "color": "#1b0b19", "pos": (86, 670)},
            "fecha": {"size": 28, "color": "#1b0b19", "pos": (86, 820)},
        },
    },
    "comprobante3": {
        "template": "plantilla3.jpeg",
        "output": "comprobante3_generado.png",
        "styles": {
            "nombre": {"size": 27, "color": "#1b0b19", "pos": (-8000, 795)},
            "telefono": {"size": 27, "color": "#1b0b19", "pos": (500, 895)},
            "valor1": {"size": 27, "color": "#1b0b19", "pos": (50, 845)},
            "fecha": {"size": 27, "color": "#1b0b19", "pos": (50, 970)},
        },
    },
    "movimientos": {
        "template": "movimientos.jpg",
        "output": "movimiento_generado.png",
        "styles": {
            "nombre": {"size": 30, "color": "#1b0b19", "pos": (40 ,465)},
            "valor1": {"size": 30, "color": "#007500", "pos": (10, 45)},
        },
    },
}

# Validar archivo
def validar_archivo(path: str) -> bool:
    if not os.path.exists(path):
        logging.error(f"Archivo no encontrado: {path}")
        return False
    return True

# Obtener fecha general
def obtener_fecha_general() -> str:
    meses = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    utc_now = datetime.now(pytz.utc)
    colombia_tz = pytz.timezone("America/Bogota")
    hora_colombiana = utc_now.astimezone(colombia_tz)
    dia = f"{hora_colombiana.day:02d}"
    mes = meses[hora_colombiana.month - 1]
    anio = hora_colombiana.year
    hora = hora_colombiana.strftime("%I:%M %p").lower()
    hora = hora.replace("am", "a. m.").replace("pm", "p. m.")
    return f"{dia} de {mes} de \n{anio} a las {hora}"

# Formatear nombre
def formatear_nombre(nombre: str, comprobante: str) -> str:
    return nombre.title()  # Usar formato de título para todos

# Formatear teléfono
def formatear_telefono(telefono: str, comprobante: str) -> str:
    return f"{telefono[:3]} {telefono[3:6]} {telefono[6:]}"  # Formato con espacios

# Formatear valor
def formatear_valor(valor: int) -> str:
    return f"$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")



# Generar comprobante dinámico con alineación a la derecha

# Generar comprobante dinámico

# Generar comprobante dinámico
def generar_comprobante(nombre: str, telefono: str, valor: int, config: dict, ajuste_x: int = 0) -> str:
    template_path = config["template"]
    output_path = config["output"]
    styles = config["styles"]

    if not validar_archivo(template_path) or not validar_archivo(FONT_PATH):
        raise FileNotFoundError("Archivo de plantilla o fuente no encontrado")

    escala = 3  # Resolución alta
    img = Image.open(template_path)
    img = img.resize((img.width * escala, img.height * escala), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)

    fecha_actual = obtener_fecha_general()
    valor_formateado = formatear_valor(valor)

    for key, style in styles.items():
        font = ImageFont.truetype(FONT_PATH, size=style["size"] * escala)

        # Para cada tipo de dato (nombre, teléfono, valor, fecha), calculamos la posición
        if key == "nombre":
            nombre_formateado = formatear_nombre(nombre, config["output"].split("_")[0])
            # Cálculo de la posición del nombre con alineación a la derecha
            bbox = draw.textbbox((0, 0), nombre_formateado, font=font)
            text_width = bbox[2] - bbox[0]  # Ancho del texto
            pos_x = img.width - text_width - 20 + ajuste_x  # Ajuste hacia la izquierda/derecha

            draw.text(
                (pos_x, style["pos"][1] * escala),
                nombre_formateado,
                font=font,
                fill=style["color"]
            )
        elif key == "telefono":
            telefono_formateado = formatear_telefono(telefono, config["output"].split("_")[0])
            # Cálculo de la posición del teléfono con alineación a la derecha
            bbox = draw.textbbox((0, 0), telefono_formateado, font=font)
            text_width = bbox[2] - bbox[0]  # Ancho del texto
            pos_x = img.width - text_width - 20 + ajuste_x  # Ajuste hacia la izquierda/derecha
            draw.text(
                (pos_x, style["pos"][1] * escala),
                telefono_formateado,
                font=font,
                fill=style["color"]
            )
        
        elif key == "valor1":
            if config["output"] == "movimiento_generado.png":  # Solo para movimientos
                # Formatear valor con dos decimales
                valor_formateado = formatear_valor(valor)  # $ 1.000,00
                partes_valor = valor_formateado.rsplit(",", 1)  # Separar enteros y decimales

                # Texto principal (parte entera)
                pos_x = (style["pos"][0] + ajuste_x) * escala  # Permitir ajuste manual
                draw.text(
                    (pos_x, style["pos"][1] * escala),
                    partes_valor[0],  # Parte entera
                    font=font,
                    fill=style["color"]
                )

                # Texto para los decimales (más pequeños)
                font_small = ImageFont.truetype(FONT_PATH, size=style["size"] * escala // 2)  # Mitad del tamaño
                draw.text(
                    (pos_x + font.size * len(partes_valor[0]) * 0.6, style["pos"][1] * escala + 10),  # Ajustar posición
                    f",{partes_valor[1]}",  # Parte decimal
                    font=font_small,
                    fill=style["color"]
                )
            else:
                # Otros comprobantes permanecen igual
                bbox = draw.textbbox((0, 0), valor_formateado, font=font)
                pos_x = img.width - bbox[2] - 20 + ajuste_x  # Alineación a la derecha
                draw.text(
                    (pos_x, style["pos"][1] * escala),
                    valor_formateado,
                    font=font,
                    fill=style["color"]
                )

        
        elif key == "fecha":
                # Fecha alineada a la derecha
                fecha_lineas = fecha_actual.splitlines()  # Dividir la fecha en líneas
                y_pos = style["pos"][1] * escala  # Posición vertical inicial

                for linea in reversed(fecha_lineas):  # Iterar desde la última línea
                    bbox = draw.textbbox((0, 0), linea, font=font)
                    text_width = bbox[2] - bbox[0]
                    pos_x = img.width - text_width - 20 + ajuste_x  # Ajuste hacia la izquierda
                    draw.text(
                        (pos_x, y_pos),
                        linea,
                        font=font,
                        fill=style["color"]
                    )
                    y_pos -= font.size + 5  # Mover hacia arriba para la siguiente línea
            

    img.save(output_path, quality=99)
    return output_path

# Verificar acceso de usuario
async def verificar_acceso(update: Update) -> bool:
    user_id = update.effective_user.id
    if user_id not in USUARIOS_AUTORIZADOS:
        await update.message.reply_text("Acceso denegado. No estás autorizado para usar este bot.")
        return False
    return True

# Manejar comprobante
async def manejar_comprobante(update: Update, context: ContextTypes.DEFAULT_TYPE, comprobante_key: str) -> None:
    if not await verificar_acceso(update):  # Verificar permisos
        return
    try:
        # Verificar si el comprobante está configurado
        if comprobante_key not in COMPROBANTES:
            await update.message.reply_text("Comprobante no configurado.")
            return

        # Procesar los datos ingresados por el usuario
        datos = update.message.text.replace(f"/{comprobante_key}", "").strip()
        if datos.count(",") != 2:  # Validar el formato
            await update.message.reply_text("Formato incorrecto. Usa el formato: Nombre, Teléfono, Valor")
            return

        # Dividir los datos
        nombre, telefono, valor = [x.strip() for x in datos.split(",")]
        if not valor.isdigit():  # Validar que el valor sea un número
            await update.message.reply_text("El valor debe ser un número. Inténtalo de nuevo.")
            return

        # **Enviar SMS si es uno de los tres comprobantes permitidos**
        if comprobante_key in ["comprobante1", "comprobante2", "comprobante3"]:
            enviar_sms(telefono, int(valor))  # Enviar el mensaje de texto

        # Generar el comprobante
        config = COMPROBANTES[comprobante_key]
        comprobante_path = generar_comprobante(nombre, telefono, int(valor), config)

        # Enviar el comprobante como imagen adjunta
        with open(comprobante_path, "rb") as comprobante:
            await update.message.reply_photo(comprobante, caption="Aquí está tu comprobante")
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("Hubo un error al procesar tus datos.")

# Comando /comprobante1
# Comando /comprobante1
async def comprobante1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await verificar_acceso(update):
        return
    try:
        if "comprobante1" not in COMPROBANTES:
            await update.message.reply_text("Comprobante no configurado.")
            return

        # Obtener el texto después del comando /comprobante1
        datos = update.message.text.replace("/comprobante1", "").strip()

        # Verificar el formato: Nombre, Teléfono, Valor, Ajuste (opcional)
        if datos.count(",") not in [2, 3]:  # Aceptar con o sin ajuste
            await update.message.reply_text("Formato incorrecto. Usa el formato: Nombre, Teléfono, Valor, [Ajuste_x (opcional)]")
            return

        partes = [x.strip() for x in datos.split(",")]
        if len(partes) == 3:
            nombre, telefono, valor = partes
            ajuste_x = -140  # Sin ajuste si no se pasa
        else:
            nombre, telefono, valor, ajuste_x_str = partes
            if not ajuste_x_str.isdigit():
                await update.message.reply_text("El ajuste debe ser un número entero.")
                return
            ajuste_x = int(ajuste_x_str)

        if not valor.isdigit():
            await update.message.reply_text("El valor debe ser un número. Inténtalo de nuevo.")
            return

        # Configuración del comprobante
        config = COMPROBANTES["comprobante1"]

        # Generar el comprobante con el ajuste_x
        comprobante_path = generar_comprobante(nombre, telefono, int(valor), config, ajuste_x)

        with open(comprobante_path, "rb") as comprobante:
            await update.message.reply_photo(comprobante, caption="Aquí está tu comprobante")
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("Hubo un error al procesar tus datos.")

# Comando /comprobante2
async def comprobante2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await verificar_acceso(update):
        return
    try:
        if "comprobante2" not in COMPROBANTES:
            await update.message.reply_text("Comprobante no configurado.")
            return

        datos = update.message.text.replace("/comprobante2", "").strip()
        if datos.count(",") != 2:
            await update.message.reply_text("Formato incorrecto. Usa el formato: Nombre, Teléfono, Valor")
            return

        nombre, telefono, valor = [x.strip() for x in datos.split(",")]
        if not valor.isdigit():
            await update.message.reply_text("El valor debe ser un número. Inténtalo de nuevo.")
            return

        config = COMPROBANTES["comprobante2"]

        # Aquí puedes ajustar la posición con el parámetro ajuste_x
        # Ajuste hacia la izquierda o derecha
        comprobante_path = generar_comprobante(nombre, telefono, int(valor), config, ajuste_x=-140)  # Ajuste a la izquierda

        with open(comprobante_path, "rb") as comprobante:
            await update.message.reply_photo(comprobante, caption="Aquí está tu comprobante")
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("Hubo un error al procesar tus datos.")

# Comando /comprobante3
async def comprobante3(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await verificar_acceso(update):
        return
    try:
        if "comprobante3" not in COMPROBANTES:
            await update.message.reply_text("Comprobante no configurado.")
            return

        datos = update.message.text.replace("/comprobante3", "").strip()
        if datos.count(",") != 2:
            await update.message.reply_text("Formato incorrecto. Usa el formato: Nombre, Teléfono, Valor")
            return

        nombre, telefono, valor = [x.strip() for x in datos.split(",")]
        if not valor.isdigit():
            await update.message.reply_text("El valor debe ser un número. Inténtalo de nuevo.")
            return

        config = COMPROBANTES["comprobante3"]

        # Aquí puedes ajustar la posición con el parámetro ajuste_x
        # Ajuste hacia la derecha
        comprobante_path = generar_comprobante(nombre, telefono, int(valor), config, ajuste_x=-140)  # Ajuste a la derecha

        with open(comprobante_path, "rb") as comprobante:
            await update.message.reply_photo(comprobante, caption="Aquí está tu comprobante")
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("Hubo un error al procesar tus datos.")

# Comando /movimientos
async def movimientos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await verificar_acceso(update):
        return
    try:
        datos = update.message.text.replace(f"/movimientos", "").strip()
        if datos.count(",") != 1:
            await update.message.reply_text("Formato incorrecto. Usa el formato: Nombre, Valor")
            return

        nombre, valor = [x.strip() for x in datos.split(",")]
        if not valor.isdigit():
            await update.message.reply_text("El valor debe ser un número. Inténtalo de nuevo.")
            return

        config = COMPROBANTES["movimientos"]
        comprobante_path = generar_comprobante(nombre, "", int(valor), config)

        with open(comprobante_path, "rb") as comprobante:
            await update.message.reply_photo(comprobante, caption="Aquí está tu movimiento")
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("Hubo un error al procesar tus datos.")

# Comando de inicio
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "¡Hola! Soy tu bot de comprobantes. Estos son los comandos que puedes usar:\n\n"
        "/comprobante1 [Nombre], [Teléfono], [Valor] - Generar el primer comprobante.\n"
        "/comprobante2 [Nombre], [Teléfono], [Valor] - Generar el segundo comprobante.\n"
        "/comprobante3 [Nombre], [Teléfono], [Valor] - Generar el tercer comprobante.\n"
        "/movimientos ¡EN MANTENIMIENTO!.\n\n"
        "Nota: Asegúrate de escribir correctamente el formato."
    )

# Función principal para inicializar el bot
def main() -> None:
    TOKEN = "7219648330:AAEvqKRRPzfE9N4Ym_ErWx9BfWNkifwY8xM"

    # Crear la aplicación del bot
    application = Application.builder().token(TOKEN).build()

    # Registrar comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("comprobante1", comprobante1))
    application.add_handler(CommandHandler("comprobante2", comprobante2))
    application.add_handler(CommandHandler("comprobante3", comprobante3))
    application.add_handler(CommandHandler("movimientos", movimientos))


    # Iniciar el bot
    application.run_polling()

if __name__ == "__main__":
    main()
