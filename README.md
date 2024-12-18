# QApp
Proyecto desarrollado para la asignatura "Procesamiento de Lenguaje Natural" de la Licenciatura en Ciencias de la Computación por parte del equipo TreeCiclo. 

QApp es un asistente de Estudio que hace uso de un modelo de Question Answering para responder a tus preguntas dado un conjunto de notas disponibles.

Esta aplicación permite la creación de notas, su almacenamiento persistente y como punto clave permite la ejecución de un modelo de Question Answering para hacer uso de un sistema de resolución de dudas de acuerdo a los contenidos recabados a lo largo de las notas.

[Descarga el ejecutable](https://alumnosuady-my.sharepoint.com/:u:/g/personal/a19201757_alumnos_uady_mx/EUZw4fMQ-J1PhN62DnURXRMBV2D3rrAcmdaWRtGaIYC5YQ?e=tGHpM6)

**NOTA:** El modelo utilizado solo es compatible con el **idioma inglés**, tanto para las notas como para las preguntas a responder.

## Tecnologías utilizadas
- Framework NiceGUI en Python para el desarrollo de la interfaz gráfica basada en la web.
  - [Más Información](https://nicegui.io/)

- Modelo **deepset/roberta-base-squad2**: este es el modelo *roberta-base* entrenado específicamente para Extractive QA en idioma Inglés. Implementado haciendo uso de Haystack, un framework de orquestación para IA que permite construir aplicaciones de LLM listas para desplegar.
  - [Más Información](https://huggingface.co/deepset/tinyroberta-squad2)
 
- Base de datos: Este proyecto utiliza SQLite como sistema de gestión de base de datos relacional de manera local.
  - [Más Información](https://www.sqlite.org/index.html)

## Cómo generar un ejecutable
Para generar un archivo ejecutable para la aplicación se utilizó la herramienta **nicegui-pack**.
    - [Más Información](https://nicegui.io/documentation/section_configuration_deployment#package_for_installation)


