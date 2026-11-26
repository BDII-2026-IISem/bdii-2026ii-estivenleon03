# Frontend de HuellaVet

Esta carpeta contiene la interfaz web de **HuellaVet**, construida con **Angular 19**. El frontend permite que un usuario inicie sesión y administre propietarios, mascotas, veterinarios, citas, consultas, tratamientos, productos, ventas, pagos y la seguridad basada en roles y permisos.

El frontend no guarda ni procesa la información principal: envía solicitudes HTTP al backend Django y presenta las respuestas en tablas y formularios.

## Arquitectura general

```text
Navegador
   |
   | Angular Router y componentes
   v
Servicios Angular --> HttpClient --> API REST de Django
                                         |
                                         v
                                   Base de datos
```

Direcciones habituales en desarrollo:

- Frontend: `http://localhost:4200`
- Backend: `http://localhost:8000`
- API REST: `http://localhost:8000/api/v1`

El backend debe estar ejecutándose antes de usar las funciones que consultan datos.

## Tecnologías utilizadas

| Tecnología | Para qué se usa en este proyecto |
|---|---|
| Angular 19 | Framework principal, enrutamiento y componentes independientes. |
| TypeScript | Lenguaje utilizado para el código de modelos, servicios y componentes. |
| RxJS | Administración de respuestas HTTP asíncronas mediante observables. |
| Angular Router | Cambio de página sin recargar el navegador. |
| PrimeNG | Tablas, diálogos, botones, notificaciones y otros controles visuales. |
| Tailwind CSS | Utilidades de diseño, espaciado, cuadrículas y estilos responsivos. |
| PrimeIcons | Iconos utilizados en el menú y las acciones. |
| Karma/Jasmine | Ejecución de pruebas unitarias en el navegador. |

## Requisitos

- Node.js compatible con Angular 19.
- npm.
- Angular CLI opcional para los comandos `ng`.
- Backend Django disponible en `http://localhost:8000`.

## Instalación y ejecución

1. Entrar a la carpeta del frontend:

   ```bash
   cd huellavet
   ```

2. Instalar las dependencias:

   ```bash
   npm install
   ```

3. Iniciar el servidor de desarrollo:

   ```bash
   npm start
   ```

   El comando equivalente es `npx ng serve`.

4. Abrir `http://localhost:4200`.

Angular actualiza automáticamente la página cuando se modifica un archivo fuente.

## Configuración de la API

Las URLs del backend se encuentran en:

- `src/environments/environment.ts`: configuración de producción.
- `src/environments/environment.development.ts`: configuración de desarrollo.

El valor principal es `apiUrl`. Por defecto apunta a:

```text
http://localhost:8000/api/v1
```

Si el backend usa otro puerto, host o ruta, debe modificarse allí. Los servicios que necesitan autenticación también utilizan las rutas de `auth`, por ejemplo `/auth/login/`.

## Punto de entrada

| Archivo | Función |
|---|---|
| `src/main.ts` | Arranca la aplicación Angular y carga `appConfig`. |
| `src/index.html` | Documento HTML que contiene la aplicación. |
| `src/styles.css` | Estilos globales, Tailwind CSS y PrimeIcons. |
| `src/app/app.component.ts` | Componente raíz de Angular. |
| `src/app/app.component.html` | Contiene el `router-outlet`, donde Angular muestra las páginas. |
| `src/app/app.config.ts` | Configura el router, HttpClient, interceptores, PrimeNG, animaciones y el idioma `es-CO`. |
| `src/app/app.routes.ts` | Define las páginas disponibles y sus permisos. |

## Estructura de `src/app`

```text
src/app/
├── core/          Servicios, modelos, interceptores, guardas y utilidades generales
├── features/      Páginas funcionales del sistema veterinario
├── layout/        Marco visual: encabezado, menú lateral, pie de página y shell
├── shared/        Elementos reutilizables, como directivas
├── app.component  Componente raíz
├── app.config     Configuración global
└── app.routes     Mapa de rutas
```

### `core`: infraestructura compartida

#### Modelos

La carpeta `core/models/` describe con interfaces TypeScript la forma esperada de los datos. Por ejemplo, define propietarios, mascotas, citas, pagos, ventas, productos y usuarios.

Esto ayuda a que los componentes conozcan qué propiedades tienen los objetos recibidos del backend y permite detectar errores de tipos durante la compilación.

#### Servicios

La carpeta `core/services/` contiene clases que hablan con la API. Cada servicio agrupa operaciones relacionadas:

- `auth.ts`: inicio de sesión, perfil, permisos, renovación y cierre de sesión.
- `session-store.ts`: conserva en `localStorage` el usuario, tokens, roles y permisos.
- `appointment-api.ts`: operaciones sobre citas.
- `appointment-payment-api.ts` y `payment-api.ts`: operaciones sobre pagos.
- `consulta.service.ts` y `clinical-treatment-api.ts`: consultas y tratamientos clínicos.
- `mascota.service.ts`: operaciones sobre mascotas.
- `propietario-api.ts`: operaciones sobre propietarios.
- `veterinarian-api.ts`: operaciones sobre veterinarios.
- `product-api.ts` y `product-type-api.ts`: productos e inventario.
- `sale-api.ts` y `product-sale-api.ts`: ventas y detalles de venta.
- `notification.service.ts`: muestra mensajes de éxito o error con PrimeNG.

Los servicios usan `HttpClient`, que convierte las solicitudes HTTP en observables. Los componentes se suscriben a esos observables para actualizar la interfaz cuando llega una respuesta.

#### Interceptores HTTP

Los interceptores procesan todas las solicitudes HTTP en `core/interceptors/`:

- `auth-interceptor.ts`: agrega el token de acceso a las solicitudes protegidas. Si el token vence, intenta renovarlo con el refresh token y vuelve a ejecutar la solicitud.
- `error-interceptor.ts`: transforma respuestas HTTP comunes como `0`, `403`, `404`, `409` y errores `5xx` en notificaciones comprensibles.

#### Guardas de rutas

Las guardas deciden si Angular permite abrir una página:

- `auth-guard.ts`: exige que exista una sesión iniciada.
- `permission-guard.ts`: exige el permiso HTTP asociado a una ruta.
- Los demás archivos de `core/guards/` contienen variantes o pruebas de guardas utilizadas por el proyecto.

Si no se cumple una autorización, el usuario puede ser enviado al inicio de sesión o a la página de acceso denegado.

#### Utilidades

`core/utils/` contiene funciones pequeñas compartidas, por ejemplo para convertir errores a mensajes, filtrar filas, consultar media queries y transformar fechas o métodos HTTP.

### `features`: pantallas del negocio

Cada pantalla agrupa su TypeScript, plantilla HTML y estilos CSS.

| Ruta | Función |
|---|---|
| `/login` | Iniciar sesión y recuperar la ruta solicitada antes de ser redirigido. |
| `/dashboard` | Resumen operativo del sistema. |
| `/profile` | Información de la cuenta y permisos actuales. |
| `/owners` | Registrar, consultar, modificar y desactivar propietarios. |
| `/mascotas` | Administrar las mascotas y su relación con el propietario. |
| `/veterinarios` | Administrar el personal veterinario. |
| `/citas` | Crear y gestionar citas médicas. |
| `/consultas` | Registrar consultas clínicas asociadas a mascotas y citas. |
| `/tratamientos` | Administrar prescripciones y aplicaciones de vacunas. |
| `/tipos-producto` | Clasificar productos e insumos. |
| `/productos` | Gestionar productos, precios e inventario. |
| `/ventas` | Crear y consultar ventas o servicios. |
| `/detalle-ventas` | Consultar los productos incluidos en las ventas. |
| `/ventas/:id` | Ver el detalle de una venta específica. |
| `/pagos-citas` | Registrar y consultar pagos asociados a citas. |
| `/auditoria-pagos` | Revisar el historial y los cambios de los pagos. |
| `/admin/usuarios` | Administración de usuarios. |
| `/admin/roles` | Administración de roles. |
| `/admin/recursos` | Administración de recursos o permisos HTTP disponibles. |
| `/admin/asignaciones` | Asignar roles a usuarios. |
| `/admin/permisos` | Conceder recursos a roles. |

Las rutas protegidas se cargan de forma diferida con carga dinámica. Así, el navegador descarga el código de una página solo cuando el usuario navega hacia ella.

### `layout`: estructura visual

- `shell/`: plantilla principal, navegación por permisos y distribución de escritorio/móvil.
- `header/`: barra superior y acción para abrir o contraer el menú.
- `aside/`: menú lateral y navegación entre módulos.
- `footer/`: pie de página de la aplicación.

La navegación no muestra opciones para las que el usuario no tiene permiso. Esta comprobación utiliza las cadenas `METHOD /ruta`, por ejemplo `GET /api/v1/pets`.

### `shared`: elementos reutilizables

La carpeta `shared/directives/` contiene directivas Angular compartidas. `HasPermissionDirective` está disponible para controlar elementos según permisos, aunque el menú principal actualmente filtra sus opciones desde `nav.config.ts`.

## Autenticación y permisos

El flujo de inicio de sesión es:

1. El componente de login envía usuario y contraseña a `POST /api/v1/auth/login/`.
2. La respuesta contiene los tokens `access` y `refresh`.
3. `SessionStore` guarda la sesión en `localStorage`.
4. `AuthService.me()` consulta el perfil y los permisos.
5. El interceptor agrega el token de acceso a las solicitudes protegidas.
6. Las rutas se habilitan o bloquean según el usuario y sus permisos.

Cuando el token expira, el interceptor intenta usar el refresh token. Si la renovación falla, limpia la sesión y devuelve al usuario al login.

La interfaz oculta operaciones no permitidas, pero la autorización real también debe existir en Django. Un control visual no impide por sí solo una llamada HTTP directa.

## Pruebas

Ejecutar las pruebas unitarias:

```bash
npm test
```

Las pruebas buscan archivos `*.spec.ts` dentro de `src/app/`. Algunas cubren guardas, servicios HTTP, modelos de servicios y componentes.

Para ejecutar una vez sin modo interactivo, según la configuración local de Karma:

```bash
npx ng test --watch=false
```

## Construcción

Crear el paquete de producción:

```bash
npm run build
```

El resultado se guarda en `dist/huellavet/`. Este directorio contiene los archivos que se pueden publicar en un servidor web.

Configuraciones principales de Angular:

- `angular.json`: rutas de código, estilos, activos, compilación y pruebas.
- `tsconfig.json`, `tsconfig.app.json`, `tsconfig.spec.json`: opciones de TypeScript.
- `tailwind.config.js`: archivos analizados por Tailwind.
- `package.json`: dependencias y comandos npm.

## Desarrollo de una nueva página

Para añadir una pantalla, conviene seguir este esquema:

1. Crear la carpeta dentro de `src/app/features/nombre-modulo/`.
2. Crear el componente, su HTML y sus estilos.
3. Crear o reutilizar un servicio en `core/services/` para hablar con Django.
4. Crear interfaces en `core/models/` para los datos del endpoint.
5. Registrar la ruta en `src/app/app.routes.ts`.
6. Añadir la opción al menú en `src/app/layout/shell/nav.config.ts`, si corresponde.
7. Asociar la opción a su permiso HTTP.
8. Añadir una prueba `*.spec.ts` para el comportamiento que se debe garantizar.

Ejemplo de generación con Angular CLI:

```bash
npx ng generate component features/nombre-modulo/nombre-pagina --standalone
```

## Convenciones importantes

- Los componentes independientes utilizan archivos separados para la clase, la plantilla y los estilos.
- Las rutas se cargan de forma diferida.
- Los servicios contienen comunicación HTTP; los componentes deben concentrarse en la interacción visual.
- Los datos que llegan o salen de la API deben representarse con interfaces o modelos.
- Los textos visibles pueden usar español, pero los nombres técnicos deben mantenerse consistentes.
- Los permisos usan formato `METHOD /api/v1/ruta`.
- No deben modificarse los tokens ni datos reales dentro de archivos versionados.
