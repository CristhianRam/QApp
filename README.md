# QApp
Proyecto desarrollado para la asignatura "Procesamiento de Lenguaje Natural" de la Licenciatura en Ciencias de la Computación. 

QApp es un asistente de Estudio que hace uso de un modelo de Question Answering para responder a tus preguntas dado un conjunto de notas disponibles.

Esta aplicación permite la creación de notas, su almacenamiento persistente y como punto clave permite la ejecución de un modelo de Question Answering para hacer uso de un sistema de resolución de dudas de acuerdo a los contenidos recabados a lo largo de las notas.

## Tecnologías utilizadas
- Framework NiceGUI en Python para el desarrollo de la interfaz gráfica basada en la web.
  - [Más Información](https://nicegui.io/)

- Modelo **tinyroberta-squad2**: Versión destilada del modelo roberta-base para Extractive QA. Implementado haciendo uso de Haystack, un framework de orquestación para IA que permite construir aplicaciones de LLM listas para desplegar.
  - [Más Información](https://huggingface.co/deepset/tinyroberta-squad2)



