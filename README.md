
# Challenge MELI


## Descripción

Este repositorio contiene la totalidad de consignas resolutoras del challenge para **Analytics Engineer Administration Risk & Compliance - IT Staff**

Esto incluye: 

1. **Challenge Analytics.**
2. **Challenge Engineer - SQL** 
3. **Challenge Engineer - API - Extração e Normalização de Dados Financeiros via API.**


## 1. Challenge Analytics
**Objetivo**  
Construir un dashboard en alguna herramienta (Ejemplo: Tableau, Looker, PowerBI) de visualización de datos analizando la evolución, crecimiento de internet, usuarios, suscriptores, etc. en Argentina y sus causas.  

**Resolución:**  
Se construyó un tablero de Power BI Público que se puede acceder desde el siguiente enlace: [Ver Tablero](https://app.powerbi.com/view?r=eyJrIjoiZWRkYjJlMDgtZjA1NS00ODY2LWJkMzUtYjZiMzQ4Mjg4OGMzIiwidCI6Ijg1NzhhMzVmLTQ2MTEtNGNhNC04Y2NiLWFkNzhmYmJiNTdmZCIsImMiOjR9).


## 2.Challenge Engineer - SQL
**Objetivo**  
A partir de la siguiente necesidad, se requiere diseñar un DER que responda al modelo del negocio. Luego, se debe responder mediante SQL diferentes preguntas.     
Backlog de Tareas
A partir de la situación planteada, te pedimos: 

    ● Diseñar un DER del modelo de datos que logre responder cada una de las preguntas mencionadas anteriormente. 

    ● Generar el script DDL para la creación de cada una de las tablas representadas en el DER. Enviarlo con el nombre “create_tables.sql”. 

    ● Generar el código SQL para responder cada una de las situaciones mencionadas anteriormente sobre el modelo diseñado. Nombre solicitado: “respuestas_negocio.sql”

**Resolución**  
Se dispone a continuacion el diagrama de Entidad relación desarrollado 
![Diagrama de entidad relacion](/images/DER_SQL.png)

Este modelo corresponde a tablas, campos y relaciones de una Base de Datos PostgreSQL. Para facilitar la creación de la misma, se utilizó docker-compose que crea la instancia de BBDD y ejecuta el DDL. 


El script DDL para la creacion de cada una de las tablas se encuentra a continuación: 
[create_tables.sql](/database/create_tables.sql)

Para ejecutar automaticamente este DDL se pueden utilizar el siguiente comando: 


```bash 
docker-compose up -d
```
> [!IMPORTANT]
> Requisitos


- Contar con **Docker Compose** instalado.

> [!IMPORTANT]
> Esto hará que se ejecute la base de datos local en el puerto 5432 con la configuración de usuario y contraseña definida en docker-compose (por ser una base de test)

Para responder las respuestas de negocio se creó el archivo SQL [respuestas_negocio.sql](/database/respuestas_negocio.sql), donde esta cada una de las consignas desarrolladas con sus correspondientes coementarios. 


## 3.Challenge Engineer - API - Extração e Normalização de Dados Financeiros via API   
**Objetivo** 

Desenvolver uma aplicação que consome dados financeiros de uma API pública, realiza a normalização das informações e armazena os dados para consultas futuras.

**Resolución - Entregables**

1. **Script del desafío principal**: el archivo [main.py](/app/main.py) es el encargado de manejar la lógica de cada uno de los puntos (Extracción, Normalización y Almacenamiento).

2. **Archivo de exportación .csv**: se puede visualizar aqui:  [data_currencies.py](currency_quotes.csv)
3. **Script para crear una tabla e insertarla en la base de datos** : Para este punto se realizo un diagrama de Base de datos para almacenar la información en la misma Base de datos del Punto 2. 

## **Diagrama del modelado**  
![Diagrama de entidad relacion](/images/DER_API.png)


> [!IMPORTANT]
> Se debe tener corriendo docker compose con la bbdd para que el escript pueda leer y escribirla


## Pasos para ejecutar el Script 

1. Crear un entorno virtual  dentro de la carpeta del proyecto
```bash 
python3 -m venv env
```
2. instalar las dependencias 
```bash 
pip install -r requirements.txt 
```
3. Ejecutar el script main.py
```bash 
python3 -m app.main
```
> [!NOTE]
> Tegnologías usadas:
> 1. Python.
> 2. SQLAlchemy como ORM.
> 3. Pydantic como validador de schemas.
> 4. Logging para logs de cada etapa.


> [!TIP]
> Para mejorar el proyecto se debria profundizar en la configuración de Docker y docker-compose para agilizar el proceso de despligue del proyecto.