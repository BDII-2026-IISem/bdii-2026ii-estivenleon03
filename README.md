# Documentación: 4 motores de base de datos en WSL2 con Docker

## 1. Introducción

Este proyecto consistió en levantar cuatro motores de base de datos dentro de WSL2 usando Docker Compose:

- MySQL
- PostgreSQL
- SQL Server
- Oracle XE

La finalidad fue crear un entorno de práctica para aprender la instalación, configuración y uso de diferentes sistemas gestores de bases de datos, además de comprobar que todos pudieran ejecutarse de forma simultánea en el mismo entorno de laboratorio.

Las fuentes de apoyo consultadas fueron las siguientes:

- https://tecnogua.com/academic/site/bd/introduccion/
- https://tecnogua.com/academic/site/bd/instalacion/mysql/
- https://tecnogua.com/academic/site/bd/instalacion/postgresql/
- https://tecnogua.com/academic/site/bd/instalacion/mssql/
- https://tecnogua.com/academic/site/bd/instalacion/oracle/

---

## 2. Objetivo del proyecto

El objetivo principal fue:

- instalar y configurar WSL2 correctamente,
- preparar Docker en Ubuntu,
- crear una red Docker común para todos los contenedores,
- levantar cuatro motores de base de datos en contenedores,
- comprobar que cada uno quedara funcionando,
- documentar el proceso y las evidencias del trabajo realizado.

---

## 3. Requisitos previos

Para cumplir con la actividad se necesitó lo siguiente:

- WSL2 funcionando en Windows
- Ubuntu como distribución principal
- Docker y Docker Compose instalados
- acceso a terminal de Ubuntu
- permiso para ejecutar comandos con sudo
- conexión a internet para descargar imágenes de los motores

---

## 4. Proceso realizado

### 4.1 Actualización del sistema

Lo primero fue actualizar Ubuntu y preparar el entorno base del sistema. Esto fue necesario para evitar errores de dependencias y asegurar compatibilidad con Docker.

![Actualización del sistema](evidencias/actualizacion%20del%20sistema%20de%20ubuntu%20.png)

También se aplicaron las actualizaciones del sistema mediante `sudo apt upgrade`.

![Actualización con apt upgrade](evidencias/aplicando%20todas%20las%20actualizacion%20con%20sudo%20apt%20upgrade.png)

---

### 4.2 Instalación de Docker

Se procedió a instalar Docker en WSL, con los pasos habituales de actualización de paquetes y configuración del repositorio oficial.

![Instalación de Docker](evidencias/instalando%20docker.png)

La idea era dejar WSL listo para trabajar con contenedores, ya que cada motor se desplegaría como servicio aislado con Docker Compose.

---

### 4.3 Creación de la estructura de carpetas

Se creó la estructura de trabajo para organizar cada motor y sus datos persistentes.

La estructura general era similar a esta:

```bash
~/ia-lab/
├── services/
│   └── motores-bd/
│       ├── mysql/
│       ├── postgres/
│       ├── mssql/
│       └── oracle/
└── data/
    ├── mysql/
    ├── postgres/
    ├── mssql/
    └── oracle/
```

Esto permitió separar cada instalación y conservar los datos en persistencia para que los contenedores no perdieran su información al reiniciarse.

---

### 4.4 Red Docker compartida

Se creó una red Docker común llamada `ia-lab-network` para que todos los motores se pudieran comunicar entre sí si era necesario.

Este paso fue importante para mantener una infraestructura organizada y uniforme.

---

## 5. MySQL

### 5.1 Configuración inicial

Se creó el archivo `docker-compose.yml` para MySQL 8.0 y se configuró el archivo `.env` con la contraseña raíz y la base de datos inicial.

Se levantó el contenedor y quedó en ejecución.

![MySQL creado correctamente](evidencias/contenedor%20de%20mySQL%20creado%20correctamente.png)

![MySQL ejecutándose](evidencias/contenedor%20ejecutandose%20perfectamente.png)

### 5.2 Evidencia de funcionamiento

Dentro del motor se pudo entrar al contenedor y verificar que MySQL quedaba operativo.

![Dentro del motor MySQL](evidencias/dentro%20del%20moto%20mySQL.png)

Esto evidenció que el servicio ya estaba levantado y listo para crear bases de datos y ejecutar comandos SQL.

---

## 6. PostgreSQL

### 6.1 Instalación y levantamiento

Se descargó la imagen oficial de PostgreSQL y se configuró el contenedor con el puerto `5432` y la base de datos inicial.

![Descarga de PostgreSQL](evidencias/descargando%20postgree.png)

Posteriormente, el servicio quedó levantado y funcionando junto con MySQL.

![PostgreSQL y MySQL funcionando](evidencias/postgree%20y%20MyAQL%20levantados%20y%20funcionando.png)

### 6.2 Observación

El motor se configuró para escuchar en todas las interfaces y se habilitó el acceso por puerto para poder conectarse desde otras herramientas y clientes.

---

## 7. SQL Server

### 7.1 Configuración y levantamiento

Se procedió a crear el contenedor de SQL Server usando su imagen oficial de Microsoft. La configuración incluyó:

- puerto `1433`
- contraseña del usuario administrador `SA`
- edición `Developer`
- volumen persistente

![Levantando SQL Server](evidencias/levantando%20SQL%20server%20.png)

### 7.2 Verificación de funcionamiento

Después de la configuración, el servicio quedó levantado y operativo.

![SQL Server funcionando](evidencias/sql%20server%20levantado%20y%20funcionando%20perfectamente.png)

---

## 8. Oracle XE

### 8.1 Primera configuración

Se creó el contenedor de Oracle usando la imagen `gvenzl/oracle-xe` y se definieron las variables de entorno para la contraseña y la base de datos.

![Creando el compose de Oracle](evidencias/creamos%20oracle%20compose.png)

![Definimos contraseña y usuario de Oracle](evidencias/definimos%20contraseña%20y%20uruario%20de%20oracle.png)

### 8.2 Inicio del contenedor

Se inició el contenedor Oracle y se realizó la validación de su estado.

![Creando y arrancando Oracle](evidencias/creando%20y%20arrancando%20el%20contenedor%20de%20oracle.png)

![Oracle inicializado](evidencias/creado%20e%20inicializado%20oracle.png)

### 8.3 Problema encontrado y solución

Durante el proceso se presentó un problema de inicio del contenedor de Oracle. El servicio no arrancaba como se esperaba en un momento inicial, por lo que fue necesario revisar la configuración y ajustar el proceso para que quedara funcionando correctamente.

![Error de starting](evidencias/error%20de%20starting%202.png)

![Problema solucionado](evidencias/problema%20con%20oracle%20starting%20solucionado.png)

![Oracle arrancando nuevamente](evidencias/arrancando%20nuevamente%20oracle.png)

Esto evidencia que el proceso no fue lineal y que hubo una corrección de configuración para estabilizar el entorno.

---

## 9. Evidencia final de los cuatro motores funcionando

Una vez resueltos los detalles de configuración, se logró tener los cuatro motores funcionando simultáneamente en WSL2.

![Los 4 motores instalándose y corriendo](evidencias/los%204%20moteres%20instalandos%20y%20corriendo%20correctamente.png)

![Los 4 motores funcionando correctamente](evidencias/los%204%20motores%20funcionando%20correctamente.png)

![Captura final general](evidencias/Captura%20de%20pantalla%202026-08-26%20101500.png)

Este fue el punto culminante del trabajo: comprobar que MySQL, PostgreSQL, SQL Server y Oracle XE pudieron ejecutarse de forma correcta dentro del mismo entorno de WSL2.

---

## 10. Conclusión

El proyecto se desarrolló con éxito y permitió comprobar que:

- WSL2 es un entorno compatible para ejecutar motores de base de datos con Docker.
- Docker Compose facilita la creación, gestión y reutilización de contenedores.
- Cada motor tiene sus propias particularidades de configuración, puertos y variables de entorno.
- Oracle fue el más delicado por su tiempo de arranque y requisitos de configuración.
- Se logró obtener un entorno funcional con cuatros bases de datos diferentes en conjunto.

Este tipo de práctica es altamente útil para aprender la administración de sistemas de información, la virtualización con contenedores y la comparación entre distintos motores de datos.

---

## 11. Referencias utilizadas

- Introducción a bases de datos: https://tecnogua.com/academic/site/bd/introduccion/
- Instalación de MySQL: https://tecnogua.com/academic/site/bd/instalacion/mysql/
- Instalación de PostgreSQL: https://tecnogua.com/academic/site/bd/instalacion/postgresql/
- Instalación de SQL Server: https://tecnogua.com/academic/site/bd/instalacion/mssql/
- Instalación de Oracle: https://tecnogua.com/academic/site/bd/instalacion/oracle/

---

## 12. Archivo del proyecto

El archivo principal del proyecto en este workspace es:

- `4motreswsl2.py`

La documentación quedó registrada en este archivo:

- `documentacion_motores_wsl2.md`

Además, las evidencias fotográficas fueron copiadas a la carpeta:

- `evidencias/`
