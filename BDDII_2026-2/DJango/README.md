# Guía de estudio del backend HuellaVet

Esta guía explica el backend con conceptos y ejemplos para estudiantes. El backend recibe solicitudes de la aplicación web, aplica las reglas del negocio y consulta o modifica la base de datos.

## 1. ¿Qué hace este backend?

El proyecto está construido con **Django** y **Django REST Framework (DRF)**. Expone una API REST que la aplicación Angular consume para gestionar propietarios, mascotas, citas, consultas, inventario, ventas y pagos.

En desarrollo, las direcciones habituales son:

- Backend: `http://localhost:8000`
- API principal: `http://localhost:8000/api/v1/`
- Frontend Angular: `http://localhost:4200`

Una **API** es una puerta de comunicación entre programas. Por ejemplo, Angular puede pedirle al backend la lista de ventas; el backend la consulta en la base de datos y responde con datos JSON.

## 2. Mapa de carpetas

```text
DJango/
├── manage.py                 # Comandos de Django
├── requirements.txt          # Dependencias de Python
├── .env.example              # Plantilla de configuración local
├── config/
│   ├── settings/             # Configuración del proyecto
│   ├── database.py           # Selección y configuración del motor de base de datos
│   └── urls.py               # Registro central de las rutas HTTP
└── apps/
    ├── common/               # Clases y utilidades compartidas
    ├── security/             # Usuarios, inicio de sesión y permisos
    ├── client/               # Alias de cliente para Owner
    ├── patient/              # Propietarios y mascotas
    ├── staff/                # Veterinarios
    ├── appointment/          # Citas
    ├── clinical/             # Consultas, recetas y vacunas
    ├── product/              # Tipos de producto e inventario
    ├── sale/                 # Ventas, artículos y pagos de venta
    └── billing/              # Pagos asociados a citas y auditoría de pagos
```

Las rutas están centralizadas en [`config/urls.py`](config/urls.py); las aplicaciones no necesitan tener un archivo `urls.py` propio para que sus endpoints funcionen.

### ¿Qué significa `apps/`?

Cada aplicación agrupa una parte del negocio. Es como separar un cuaderno grande por materias: los archivos de citas se mantienen en `appointment`, mientras que los de ventas viven en `sale`.

Dentro de una aplicación suelen aparecer:

- `models.py`: describe los datos y sus relaciones.
- `serializers.py`: valida datos de entrada y prepara datos de salida JSON.
- `views.py`: ejecuta las acciones que pide el cliente web.
- `tests.py`: comprueba que las acciones se comporten como se espera.
- `migrations/`: historial de cambios al esquema de la base de datos.

## 3. Conceptos básicos

| Término | Explicación sencilla |
|---|---|
| **Modelo** | La descripción de un tipo de dato. `Pet`, por ejemplo, describe qué campos tiene una mascota. |
| **Base de datos** | Donde se guardan los datos de forma persistente. |
| **Migración** | Un cambio versionado en la estructura de la base de datos, como agregar una columna. |
| **Serializer** | Un traductor y validador entre JSON y los objetos Python del backend. |
| **Vista / ViewSet** | El código que atiende una solicitud, aplica reglas y devuelve una respuesta. |
| **Ruta / endpoint** | La dirección HTTP de una operación, como `GET /api/v1/pets/`. |
| **QuerySet** | Una consulta de Django que permite buscar registros sin escribir SQL directamente. |
| **CRUD** | Crear, leer, actualizar y eliminar registros. |
| **Clave foránea** | Un vínculo entre registros. Por ejemplo, una mascota tiene un propietario. |
| **Autenticación** | Comprobar quién es el usuario. |
| **Autorización** | Comprobar qué acciones puede realizar ese usuario. |
| **Transacción** | Un conjunto de cambios que se guardan juntos o se cancelan juntos si algo falla. |

### Ejemplo: modelo y serializer

[`apps/patient/models.py`](apps/patient/models.py) define `Pet` con campos como nombre y especie, y una relación con `Owner`. [`apps/patient/serializers.py`](apps/patient/serializers.py) define qué datos de la mascota acepta o devuelve la API.

En palabras sencillas: el modelo es el formulario guardado en el sistema; el serializer revisa que lo que llegó en el formulario tenga sentido.

## 4. Cómo viaja una solicitud por el backend

Ejemplo: Angular quiere consultar las ventas.

1. El navegador envía `GET /api/v1/sales/`.
2. Django busca esa ruta en [`config/urls.py`](config/urls.py) y la conecta con `SaleViewSet`.
3. La autenticación revisa el token del usuario.
4. Los permisos comprueban si el usuario puede consultar ventas.
5. La vista filtra los registros permitidos y consulta la base de datos.
6. El serializer convierte los objetos en JSON.
7. Django devuelve la respuesta al navegador.

Este recorrido es parecido a pedir un libro en una biblioteca: la ruta indica qué libro buscas, los permisos comprueban si puedes acceder y la respuesta contiene el resultado.

## 5. Aplicaciones y datos principales

### Seguridad: `apps/security/`

- Usa el usuario de autenticación de Django para iniciar sesión.
- Administra roles como `ADMIN`, `VETERINARIO`, `RECEPCIONISTA` y `PROPIETARIO`.
- Relaciona permisos con un método HTTP y una ruta, por ejemplo `GET /api/v1/sales/`.
- Emite tokens de acceso y administra tokens de renovación.

**Importante:** el usuario de autenticación de Django (`auth.User`) y el modelo histórico `User` de HuellaVet no son lo mismo. La autenticación actual usa Django; ciertos modelos históricos se conservan para compatibilidad con los datos existentes.

`API_ACCESS` tiene el valor predeterminado `rbac`, que aplica permisos por rol. La opción `open` cambia el acceso a algunos recursos y no debe usarse a la ligera, especialmente en un entorno publicado.

### Clientes y pacientes

- `Owner` representa al propietario y está definido en `apps/patient/`.
- `Pet` representa a una mascota y apunta a su propietario.
- `Client` es un modelo proxy de `Owner`: ofrece el nombre “cliente” en el código y una ruta alternativa, pero comparte la misma tabla. No crea una segunda tabla de clientes.
- Al desactivar un propietario o una mascota se conserva el historial; en general, no se borra físicamente el registro.

### Atención veterinaria

- `Veterinarian` representa a un veterinario.
- `Appointment` relaciona una mascota con un veterinario en un horario.
- `Consultation` guarda la atención clínica y puede relacionarse con una cita.
- `Prescription` guarda medicamentos indicados durante una consulta.
- `Vaccine`, `VaccineBatch` y `VaccineApplication` representan vacunas, lotes y aplicaciones.

### Productos y ventas

- `ProductType` agrupa productos.
- `Product` guarda precio y existencias.
- `Sale` pertenece a un propietario y puede referirse a una mascota.
- `SaleItem` representa cada producto vendido y la cantidad.
- `SalePayment` registra pagos de una venta.

Al crear una venta, el backend valida propietario, mascota, productos y existencias; calcula subtotal, descuento, impuesto y total; crea los detalles y descuenta el inventario dentro de una transacción. Si una validación falla, no debe quedar una venta a medias.

[`apps/billing/`](apps/billing/) contiene otro modelo llamado `Payment`, relacionado con citas. No hay que confundirlo con `SalePayment`, que corresponde a pagos de ventas.

## 6. Endpoints importantes

La mayoría de los recursos usa las operaciones CRUD de DRF:

- `GET /coleccion/`: listar.
- `POST /coleccion/`: crear.
- `GET /coleccion/{id}/`: consultar un elemento.
- `PUT` o `PATCH /coleccion/{id}/`: actualizar.
- `DELETE /coleccion/{id}/`: eliminar o desactivar, según las reglas del recurso.

Las rutas principales bajo `/api/v1/` son:

| Recurso | Ruta |
|---|---|
| Usuarios y roles | `users`, `roles`, `permissions`, `user-roles`, `role-users` |
| Recursos y roles | `resources`, `role-permissions`, `resource-roles` |
| Propietarios y mascotas | `owners`, `clients`, `pets` |
| Personal y citas | `veterinarians`, `appointments` |
| Atención clínica | `consultations`, `prescriptions`, `vaccines`, `vaccine-batches`, `vaccine-applications` |
| Inventario | `product-types`, `products` |
| Ventas y pagos | `sales`, `payments`, `payment-audits` |

Otras rutas:

- Inicio de sesión: `POST /api/v1/auth/login/`
- Cerrar sesión: `POST /api/v1/auth/logout/`
- Renovar token: `POST /api/v1/auth/refresh/`
- Perfil: `/api/v1/auth/profile/`
- Permisos del usuario: `GET /api/v1/auth/permissions/`
- Documentación Swagger: `/api/schema/swagger-ui/`
- Documentación ReDoc: `/api/schema/redoc/`

## 7. Ejemplo: iniciar sesión

La solicitud de ejemplo usa datos ficticios. En una terminal:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"usuario_demo","password":"contraseña_de_ejemplo"}'
```

Una respuesta correcta incluye un token `access` y un `refresh`. Para una ruta protegida se envía el token de acceso:

```http
Authorization: Bearer <access>
```

El token de acceso permite hacer solicitudes durante un tiempo limitado. El token de renovación permite solicitar otro token de acceso. No se deben publicar ni guardar tokens reales en el código.

## 8. Ejemplo: crear una venta

`POST /api/v1/sales/` acepta campos como `clientId`, `saleDate` y una lista `items`. Los identificadores deben existir en la base de datos. El ejemplo ilustra la forma del JSON; reemplaza los IDs por registros válidos:

```json
{
  "clientId": 12,
  "petId": 35,
  "saleDate": "2026-11-23T14:00:00-05:00",
  "discounts": "5000.00",
  "items": [
    { "productId": 8, "quantity": 2 },
    { "productId": 11, "quantity": 1 }
  ],
  "paymentMethod": "CASH",
  "paymentAmount": "20000.00"
}
```

Puntos para observar en [`apps/sale/serializers.py`](apps/sale/serializers.py):

- `productId` y `quantity` son los datos que el cliente envía por cada artículo.
- El backend busca el precio real del producto; no confía en un precio enviado por el navegador.
- `paymentMethod` y `paymentAmount` se envían juntos o se omiten juntos.
- El pago inicial no puede superar el total.
- El producto no puede venderse si está inactivo o no tiene suficiente stock.
- Las cantidades y valores monetarios se validan antes de guardar.

## 9. Configuración y ejecución local

1. Abre una terminal en la carpeta `DJango/`.
2. Instala las dependencias:

   ```bash
   python -m venv .venv
   # Linux o macOS
   source .venv/bin/activate
   # Windows PowerShell: .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. Copia `.env.example` a `.env` y completa la configuración:

   ```bash
   cp .env.example .env
   ```

   En Windows puedes copiar el archivo desde el explorador. Configura `DJANGO_SECRET_KEY` y un solo bloque de base de datos, según `DB_ENGINE`: `mysql`, `postgresql`, `mssql`, `oracle` o `sqlite`.

4. Asegúrate de que la base de datos exista y que sus credenciales sean correctas. No subas `.env` al repositorio.
5. Comprueba el proyecto y aplica migraciones:

   ```bash
   python manage.py check
   python manage.py migrate
   ```

6. Inicia el servidor:

   ```bash
   python manage.py runserver 8000
   ```

Para un entorno nuevo, el comando `python manage.py seed_rbac` sincroniza los roles y permisos. Se puede asignar el rol de administrador a un usuario existente usando `python manage.py seed_rbac --username nombre_de_usuario`. Revisa con cuidado el usuario indicado.

## 10. Migraciones y pruebas

Una migración registra cambios en los modelos para aplicarlos a la base de datos. Comandos útiles:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations
python manage.py test
```

Antes de generar una migración, revisa qué modelos cambiaste y lee el archivo generado. Antes de aplicar cambios a una base de datos con información importante, haz una copia de seguridad. No borres migraciones históricas solo porque parezcan antiguas: Django las utiliza para reconstruir la evolución del esquema.

Las pruebas están distribuidas en `apps/*/tests.py` y archivos de prueba relacionados. Una prueba automatizada comprueba un comportamiento sin tener que repetir manualmente todos los pasos en el navegador.

## 11. Problemas comunes

- **`Http failure response ... 0 Unknown Error`**: el navegador no recibió una respuesta HTTP. Comprueba que Django esté iniciado en el puerto 8000, que la URL de Angular sea correcta y que el origen esté incluido en `CORS_ALLOWED_ORIGINS`.
- **Respuesta `401`**: faltan credenciales o el token no es válido/expiró. Inicia sesión y usa el token de acceso.
- **Respuesta `403`**: el usuario pudo autenticarse, pero su rol no tiene permiso para esa operación. Revisa la asignación del rol y sus permisos.
- **Respuesta `404`**: revisa la ruta y el identificador solicitado.
- **Error `500`**: consulta la terminal donde corre Django. Puede ser un error de programación, de conexión o que falte aplicar una migración.
- **No conecta a la base de datos**: revisa `DB_ENGINE`, el bloque correspondiente del `.env`, que el servicio de base de datos esté iniciado y que sus credenciales sean correctas.

## 12. Orden recomendado para estudiar el código

1. Lee [`config/urls.py`](config/urls.py) y localiza las rutas.
2. Sigue un recurso sencillo: [`apps/patient/models.py`](apps/patient/models.py), [`apps/patient/serializers.py`](apps/patient/serializers.py) y [`apps/patient/views.py`](apps/patient/views.py).
3. Compara el flujo de validación y escritura de ventas en [`apps/sale/serializers.py`](apps/sale/serializers.py) y [`apps/sale/views.py`](apps/sale/views.py).
4. Revisa autenticación y permisos en [`apps/security/auth_views.py`](apps/security/auth_views.py), [`apps/security/tokens.py`](apps/security/tokens.py) y [`apps/security/permissions.py`](apps/security/permissions.py).
5. Ejecuta las pruebas y cambia un caso pequeño; luego vuelve a correrlas para entender qué comportamiento protegen.

Una buena pregunta para cada archivo es: **¿qué recibe, qué valida, qué cambia y qué devuelve?** Esa pregunta ayuda a seguir el recorrido de los datos por todo el backend.
