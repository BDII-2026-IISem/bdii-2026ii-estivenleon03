# Revisión de los ISS de Frontend-Django en HuellaVet

**Fecha:** 4 de noviembre de 2026  
**Proyecto revisado:** HuellaVet (Angular y Django)

## Introducción

Este informe compara HuellaVet con los ISS publicados en la [ruta académica Frontend 2026 · Django](https://tecnogua.com/academic/site/frontend2026/django/). El material propone construir **StoreLab**, una aplicación de tienda con Angular y Django. Por eso, la comparación se centra en los objetivos que sí se relacionan con HuellaVet —por ejemplo, productos, ventas y permisos— y no en copiar sus nombres de rutas o su modelo de clientes.

Para organizar la revisión tomé los **ISS-01 a ISS-11** como los once entregables principales del índice. El ISS-00 es un requisito previo y los ISS-01A/01B son unidades complementarias de estructura y navegación; no los cuento como ISS principales adicionales.

Los estados de la tabla describen la correspondencia encontrada en el código. “Funcional” significa que existe una implementación equivalente; no significa que se hayan vuelto a ejecutar pruebas de extremo a extremo contra MySQL en esta revisión.

## Comparación

| ISS | Qué propone el material | Situación en HuellaVet |
|---|---|---|
| **01 · Inicio del proyecto** | Crear la aplicación con Angular 22, PrimeNG 22/Aura y Tailwind 4. | La aplicación usa Angular **19.2**, PrimeNG **19.1** y Tailwind 4 ([package.json](../huellavet/package.json)). La base tecnológica está implementada, pero las versiones no coinciden con las que pide el ISS. Si la rúbrica exige Angular 22 y PrimeNG 22, habría que planificar una actualización. **Parcial.** |
| **02 · Núcleo y navegación** | Configurar la URL de la API, los modelos, servicios, rutas y estructura de la aplicación. | HuellaVet cuenta con configuración de API, servicios por dominio, modelos, rutas y navegación ([app.config.ts](../huellavet/src/app/app.config.ts), [app.routes.ts](../huellavet/src/app/app.routes.ts), [environment.ts](../huellavet/src/environments/environment.ts)). Su API está bajo `/api/v1/` y representa procesos veterinarios, por lo que su contrato es distinto al de StoreLab. **Implementado.** |
| **03 · Clientes** | Crear un CRUD con listado, búsqueda, edición y baja. | La función equivalente está en el módulo de **propietarios**, con servicios y pantallas propias ([propietario-api](../huellavet/src/app/core/services/propietario-api.ts), [módulo de propietarios](../huellavet/src/app/features/propietarios/)). En HuellaVet, el propietario es la entidad adecuada y se relaciona con las mascotas. **Implementado como equivalente.** |
| **04 · Tipos de producto** | Administrar los tipos o categorías de producto. | Existe el módulo de tipos de producto y su API está registrada en Django ([lista de tipos de producto](../huellavet/src/app/features/product-types/product-type-list/product-type-list.ts), [rutas Django](../DJango/config/urls.py)). **Implementado.** |
| **05 · Productos** | Administrar productos y consultar los disponibles, incluido su stock. | HuellaVet tiene pantallas de productos y un endpoint para consultar los disponibles. El inventario se utiliza también en las ventas ([módulo de productos](../huellavet/src/app/features/products/), [vistas de productos](../DJango/apps/product/views.py)). **Implementado.** |
| **06 · Ventas y detalle** | Registrar ventas con sus productos y dejar que el servidor calcule los importes y descuente existencias. | Angular permite registrar ventas y consultar su información; Django gestiona la creación de la venta y el inventario dentro de una transacción ([módulo de ventas](../huellavet/src/app/features/sales/), [vistas de ventas](../DJango/apps/sale/views.py)). Los campos y relaciones se adaptan al modelo de HuellaVet y no son iguales a los del ejemplo StoreLab. **Implementado como equivalente.** |
| **07 · Detalle y panel** | Consultar el detalle de una venta, anularla y mostrar un resumen diario. | HuellaVet dispone de detalle de venta, consulta de líneas, anulación y panel. Los valores monetarios se presentan en pesos colombianos y el cálculo diario usa la zona horaria de Bogotá ([detalle de venta](../huellavet/src/app/features/sales/sale-detail/sale-detail.ts), [panel](../huellavet/src/app/features/dashboard/dashboard.ts)). El panel reúne información de otros recursos en el frontend; por ello, su carga depende de que esas consultas respondan correctamente. **Implementado, con esa dependencia.** |
| **08 · Autenticación** | Implementar login, sesión, perfil, permisos, cierre de sesión y renovación de tokens. | Django ofrece los endpoints de autenticación bajo `/api/v1/auth/`. Angular cuenta con el servicio de autenticación, almacenamiento de sesión e interceptor para adjuntar y renovar el token ([servicio de autenticación](../huellavet/src/app/core/services/auth.ts), [interceptor](../huellavet/src/app/core/interceptors/auth-interceptor.ts), [rutas Django](../DJango/config/urls.py)). **Implementado.** |
| **09 · Guards y permisos** | Restringir las rutas y mostrar acciones según los permisos concedidos. | Hay guards, una directiva para permisos y un menú filtrado ([rutas Angular](../huellavet/src/app/app.routes.ts), [menú](../huellavet/src/app/layout/shell/nav.config.ts), [sesión y permisos](../huellavet/src/app/core/services/session-store.ts)). Sin embargo, los guards de permiso están aplicados solo a algunas rutas: varias páginas clínicas, comerciales y administrativas quedan protegidas por autenticación, pero no por un permiso de ruta específico. Esto no sustituye la autorización del backend, aunque sí deja una brecha en la protección y experiencia de navegación del frontend. **Parcial; requiere atención.** |
| **10 · Administración RBAC** | Administrar usuarios, roles, recursos, asignaciones y permisos desde la interfaz. | HuellaVet tiene pantallas para esos cinco aspectos y endpoints asociados en Django ([módulos administrativos](../huellavet/src/app/features/admin/), [vistas de seguridad](../DJango/apps/security/views.py), [rutas Django](../DJango/config/urls.py)). Su nomenclatura corresponde al modelo propio del sistema. La navegación directa a varias de estas páginas debe quedar cubierta al completar el guard de permisos del ISS-09. **Parcial.** |
| **11 · Calidad y entrega** | Revisar compilación, pruebas, accesibilidad, adaptación a pantallas y recorrido con la API real. | En validaciones anteriores quedaron registrados un build Angular satisfactorio, **31 pruebas frontend** y **84 pruebas Django** ejecutadas con SQLite aislada. Estas pruebas no confirman por sí solas el comportamiento con MySQL. Además, `environment.ts` contiene `http://localhost:8000/api/v1`; para desplegar fuera del equipo local se necesita configurar la URL del servidor correspondiente. En esta revisión no se repitieron pruebas ni se hizo una evaluación completa de accesibilidad y diseño responsive. **Parcial.** |

## Observaciones para continuar

La brecha más importante que encontré en la comparación es la aplicación desigual de los permisos a las rutas de Angular. Conviene completar esa protección y verificar, para cada perfil, tanto el acceso a las páginas como la visibilidad de sus acciones. Django debe seguir validando los permisos en cada operación: ocultar un botón en Angular no es una medida de autorización suficiente.

También hace falta revisar la configuración de producción. La dirección `localhost` sirve para desarrollo local, pero no permitirá que una aplicación desplegada en otro equipo alcance el backend. La URL debe definirse para el entorno de despliegue, sin alterar credenciales.

Por último, la diferencia entre Angular 19/PrimeNG 19 y las versiones 22 del material solo sería un incumplimiento si esas versiones están expresamente exigidas por el profesor. Antes de actualizar dependencias, conviene confirmarlo y evaluar el impacto en la compatibilidad del proyecto.

## Procesos propios de HuellaVet

El material de StoreLab no cubre los procesos veterinarios. Por esa razón, esta comparación no califica como faltantes los módulos de mascotas, veterinarios, citas, consultas e historias clínicas, recetas, vacunas y lotes. Tampoco evalúa los pagos de citas ni su auditoría como si fueran parte de las ventas de StoreLab. HuellaVet mantiene diferenciados los pagos de citas (`payments`) y los abonos de ventas (`sale_payments`).

## Alcance de esta revisión

La comparación se realizó mediante la documentación de los ISS y la inspección de archivos del proyecto. No se modificó el código, no se ejecutaron migraciones y no se realizaron escrituras en MySQL. Los resultados de pruebas mencionados corresponden a validaciones previas del proyecto; no se volvieron a ejecutar para preparar este informe.

## Fuentes consultadas

- [Ruta académica Frontend 2026 · Django](https://tecnogua.com/academic/site/frontend2026/django/)
- [Informe local de ISS Django](../Informes-Django/ISS_informes.md), usado como referencia complementaria. Corresponde al backend y no reemplaza el índice Frontend-Django.
