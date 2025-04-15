# 

# README - Challenge MELI


## Descripción

Este proyecto contiene las consultas SQL desarrolladas sobre una base de datos relacional utilizando PostgreSQL. Se utilizó **Docker Compose** para facilitar la creación de la base de datos, se configura un entorno para ejecutar las consultas que analizan datos de ventas, usuarios y productos. Las tareas resueltas en el proyecto incluyen:

1. **Listar usuarios que cumplen años hoy y han realizado más de 1500 ventas en enero de 2020.**
2. **Obtener el top 5 de usuarios con más ventas en la categoría "Celulares" en 2020.**
3. **Poblar una nueva tabla con el precio y estado de los ítems al final del día, asegurando que sea reprocesable.**


## Requisitos

- **Docker** y **Docker Compose** instalados.
- Una máquina con acceso a Internet para descargar las imágenes necesarias.

---

## Instrucciones para levantar el proyecto

### 1. Clonar el repositorio

Con el siguiente comando:

```bash
git clone https://github.com/tu_usuario/tu_repositorio.git
cd tu_repositorio
```

### 2. Levantar los contenedores con Docker Compose

```bash 
docker-compose up -d
```

Este comando descargará las imágenes necesarias y levantará los contenedores en segundo plano. PostgreSQL estará disponible en el contenedor db.

> [!IMPORTANT]
> Dentro de la carpeta app se encuentran los archivos .sql con las queries, de igual manera se ha dejado el archivo init.sql en la raiz para que la configuración de docker-compose lo tome desde allí.
