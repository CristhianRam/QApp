from nicegui import ui, app, native
from bs4 import BeautifulSoup   
import sqlite3
import pandas as pd
import os
from haystack import Document
from haystack.components.readers import ExtractiveReader
import re
import sys

    
# Cargar Componentes del modelo
docs = [] # Lista de documentos a los que tendrá acceso el modelo
reader = ExtractiveReader(model="deepset/roberta-base-squad2") # Modelo
reader.warm_up() # Activar el modelo
# Conectarse a la base de datos de notas (se crea si no existe)
if getattr(sys, 'frozen', False):
    # Estamos en un ejecutable
    app_dir = sys._MEIPASS
else:
    # Estamos en un entorno normal
    app_dir = os.path.dirname(os.path.abspath(__file__))

db_path = os.path.join(app_dir, 'db\\notes.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear tabla si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS notas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo VARCHAR(35),
        contenido TEXT,
        contenido_html TEXT
    )
''')

# Variables globales
table = None
label_respuesta = None
label_ID = None
label_titulo = None

# Generar dataframe a partir de notas de la base de datos
cursor.execute('SELECT id, titulo, contenido FROM notas') # Obtenemos las notas
notas = cursor.fetchall()
df = pd.DataFrame(data={
                    'ID': [n[0] for n in notas],
                    'Título': [n[1] for n in notas],
                    'Contenido': [n[2] for n in notas],
                }) # llenado del dataframe
# Añadimos a la lista de documentos los objetos Document basados en las notas
for n in notas:
    docs.append(Document(id=n[0], content=n[2], meta={'titulo':n[1]}))

""" Funcion que es ejecutada al presionar el botón Shutdown:
    Cierra la conexión a la base de datos y termina el programa """
def finalizar_sesion():
    conn.close()
    app.shutdown()

""" ---------------------------
    Pagina Principal de la APP 
-------------------------------"""
@ui.page('/')
def main_page():
    # Header de la app
    with ui.header().classes(replace='row items-center justify-between') as header:
        # Añadimos pestañas
        with ui.tabs() as tabs:
            ui.tab('Notas')
            ui.tab('Nueva Nota')
            ui.tab('Asistente')
        # Boton de cierre
        ui.button('Shutdown', on_click=finalizar_sesion) # Boton de apagado

    # Footer de la app
    with ui.footer(value=False).classes('flex justify-between items-center') as footer:
        ui.label('Procesamiento de Lenguaje Natural: Proyecto Final\n').classes('text-left')
        ui.label('Equipo TreeCiclo 🫡').classes('text-right')

    # Declaracion de contenido de las diferentes pestañas
    with ui.tab_panels(tabs, value='Notas').classes('w-full'):
        # --- PESTAÑA DE NOTAS ---
        with ui.tab_panel('Notas'):
            ui.label('Todas las notas almacenadas:').classes('text-lg font-bold')
            # Crear una tabla para mostrar las notas
            table = ui.table.from_pandas(df, pagination=5, row_key='ID').classes('w-full')
            # Personalizar el encabezado de la tabla
            table.add_slot('header', r'''
                <q-tr :props="props">
                    <q-th auto-width>
                        Expand
                    </q-th>
                    <q-th v-for="col in props.cols" :key="col.name" :props="props">
                        {{ col.label }}
                    </q-th>
                </q-tr>
            ''')
            # Personalizar el cuerpo de la tabla con filas expandibles
            table.add_slot('body', r'''
                <q-tr :props="props">
                    <q-td auto-width>
                        <q-btn size="sm" color="accent" round dense
                            @click="props.expand = !props.expand"
                            :icon="props.expand ? 'remove' : 'add'" />
                    </q-td>
                    <q-td v-for="col in props.cols" :key="col.name" :props="props">
                        <template v-if="col.name === 'Contenido'">
                            {{ props.row[col.name].substring(0, 50) }}...
                        </template>
                        <template v-else>
                            {{ props.row[col.name] }}
                        </template>
                    </q-td>
                </q-tr>
                <q-tr v-show="props.expand" :props="props">
                    <q-td colspan="100%">
                        <div class="text-left" style="white-space: normal; word-wrap: break-word;">
                            {{ props.row['Contenido'] }}
                        </div>
                    </q-td>
                </q-tr>
            ''')
            

        # --- PESTAÑA DE NUEVA NOTA ---
        with ui.tab_panel('Nueva Nota'):
            # Input para el titulo del documento
            input_titulo = ui.input(label='Titulo', placeholder='Ingresa el titulo', validation={'Input too long': lambda value: len(value) <= 35})
            # Editor de texto
            editor = ui.editor(placeholder='Type something here').classes('w-full h-full')
            # Predeclaramos un cuadro de dialogo para Guardado Exitoso
            with ui.dialog() as saved_dialog, ui.card():
                    ui.label('Nota Guardada!')
                    ui.button('Close', on_click=saved_dialog.close)

            """Funcion que almacena la nota en la base de datos,
                la añade al dataframe de notas y actualiza la tabla en la pestaña de notas
            """
            def store_note():
                # Parseamos el html del contenido del editor
                soup = BeautifulSoup(editor.value, 'html.parser') 
                texto_plano = soup.get_text(separator=" ")
                texto_plano = re.sub(r'\s+', ' ', texto_plano).strip()
            
                titulo = input_titulo.value # Obtener el titulo del input
                # Validamos el input del titulo
                if len(titulo)>0 and len(titulo)<=35:
                    cursor.execute('''
                        INSERT INTO notas (titulo, contenido, contenido_html) VALUES (?, ?, ?)
                    ''', (titulo, texto_plano, editor.value)) # Insertar la nota en la base de datos
                    conn.commit() # Confirmar los cambios en la base de datos
                    editor.set_value("") # Limpiar el editor
                    input_titulo.set_value("") # Limpiar el titulo
                    # Obtener la nota recién agregada
                    cursor.execute('SELECT id, titulo, contenido FROM notas ORDER BY id DESC LIMIT 1') 
                    notas = cursor.fetchall()
                    n = notas[0]
                    # Añadir nota al dataframe y a la lista de documentos
                    df.loc[len(df.index)] = [n[0], n[1], n[2]] 
                    docs.append(Document(id=n[0], content=n[2], meta={'titulo':n[1]}))
                    table.update_from_pandas(df) # Actualizamos la tabla de la pestaña de notas
                    saved_dialog.open() # Abrimos el cuadro de dialogo de exito
                else:
                    ui.notify('El título debe tener entre 1 y 35 caracteres.', color='red') # Notificar si el titulo es muy largo o no está presente

            # Botón para llamar a la funcion para almacenar la nota
            ui.button('Guardar Nota', on_click=store_note)

        # --- VENTANA DEL ASISTENTE --
        with ui.tab_panel('Asistente').classes('flex flex-col justify-end h-full p-4'):
            """Funcion que limpia los resultados"""
            def limpiar_labels():
                label_respuesta.set_text("")
                label_ID.set_text(f"ID del documento: {""}")
                label_titulo.set_text(f"Titulo del documento: {""}")

            """ Funcion que obtiene los resultados del modelo dada la pregunta
            y despliega los resultados en la app"""
            def send():
                # Verificamos que tenemos documentos disponibles
                if not docs: 
                    label_respuesta.set_text("No hay notas disponibles.")
                    return
                question =input_query.value # Obtenemos el contenido del input de la pregunta
                # Generar resultado
                try:
                    # Llamamos al modelo y almacenamos resultados
                    result = reader.run(query=question, documents=docs)
                    # Verificamos que hay resultados
                    if result:
                        # Obtenemos datos específicos
                        answer = result["answers"][0].data
                        titulo_doc =result["answers"][0].document.meta["titulo"]
                        id_doc = result["answers"][0].document.id
                        # Actualizamos en la app
                        label_respuesta.set_text(answer)
                        label_ID.set_text(f"ID del documento: {id_doc}")
                        label_titulo.set_text(f"Titulo del documento: {titulo_doc}")
                    else:
                        limpiar_labels()
                        label_respuesta.set_text("No hay información disponible en las notas.")

                except:
                    limpiar_labels()
                    label_respuesta.set_text("Respuesta no disponible.") # En caso de error, desplegar este texto


            
            
            # Elementos de la pestaña
            ui.markdown('#### Asistente de estudio') # Titulo de la pestaña
            # Input para la pregunta
            with ui.row().classes('items-center w-full p-4'):
                input_query = ui.input(placeholder='Escribe tu pregunta aquí...')
                input_query.classes('w-full bg-white border rounded-full p-3 text-base shadow-md') \
                    .style('outline: none; width: 80%;')  
                ui.button("Enviar",on_click=send) # Boton para obtener resultados

            ui.separator() # Separador de elementos de la ui
            # Elementos que despliegan el resultado
            ui.markdown('**Respuesta**:')
            label_respuesta = ui.label("")
            ui.separator()
            ui.markdown('**Encontrado en**:')
            label_ID = ui.label(f"ID del documento: {""}")
            label_titulo = ui.label(f"Titulo del documento: {""}")
            ui.button("Limpiar resultados", on_click=limpiar_labels)
            ui.separator()

    # Boton para desplegar el footer
    with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20):
        ui.button(on_click=footer.toggle, icon='contact_support').props('fab')

ui.run(native=True, reload=False, frameless=True, port=native.find_open_port())
