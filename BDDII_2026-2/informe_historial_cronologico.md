# Informe: historial cronológico de cambios en `huellavet_db`

## 1. Introducción

El historial cronológico permite revisar las operaciones que se realizan sobre las tablas seleccionadas de `huellavet_db`. Cada evento registra la tabla afectada, la clave del registro, el tipo de operación, la fecha y hora, la cuenta MySQL de la conexión y, cuando corresponde, una copia de los valores anteriores y nuevos.

La captura de los eventos se realiza mediante triggers; DBeaver se utiliza para conectarse, ejecutar el SQL y consultar los resultados. Este procedimiento está planteado para MySQL 8.0. La estructura y los scripts deben verificarse contra el esquema real de HuellaVet antes de su implementación.

> **Estado actual:** la tabla de auditoría y los triggers todavía están pendientes de instalación en `huellavet_db`. Este informe describe el procedimiento previsto. Las capturas fotográficas se tomarán en DBeaver a medida que se realicen los pasos y se incorporarán progresivamente.
>
> **Nota de alcance:** no se encontraron scripts SQL ni el esquema de `huellavet_db` en los archivos disponibles. Deben sustituirse los nombres de ejemplo por los objetos reales de la base de datos.

## 2. Objetivo

Implementar y consultar un registro ordenado de cambios para poder identificar qué operación ocurrió, sobre qué registro y cuándo, conservando los valores auditados aunque el registro original se actualice o elimine.

## 3. Diseño del registro histórico

La tabla propuesta `historial_cronologico` tendrá los siguientes datos una vez creada dentro de `huellavet_db`:

| Campo | Uso |
| --- | --- |
| `id_historial` | Identificador único del evento; permite desempatar eventos con la misma hora. |
| `tabla_afectada` | Nombre de la tabla en la que ocurrió el cambio. |
| `id_registro` | Clave del registro afectado, guardada como texto para aceptar claves de distintos tipos. |
| `operacion` | Tipo de cambio: `INSERT`, `UPDATE` o `DELETE`. |
| `fecha_evento` | Fecha y hora con fracciones de segundo en que el trigger registró el evento. |
| `usuario_bd` | Cuenta MySQL de la conexión que ejecutó la operación. |
| `datos_anteriores` | Valores anteriores en formato JSON; aplica a `UPDATE` y `DELETE`. |
| `datos_nuevos` | Valores nuevos en formato JSON; aplica a `INSERT` y `UPDATE`. |

El índice compuesto por tabla, clave del registro y fecha ayuda a recuperar la secuencia de cambios de una entidad concreta. El informe de [implementación de triggers](informe_Triggers.md) contiene el SQL de creación y las plantillas para registrar operaciones.

## 4. Procedimiento en DBeaver

1. Abrir DBeaver y conectarse al servidor MySQL correspondiente.
2. En el navegador de bases de datos, ubicar `huellavet_db` y abrir un editor SQL asociado a esa conexión.
3. Comprobar el contexto antes de ejecutar comandos:

```sql
SELECT DATABASE() AS base_actual, VERSION() AS version_mysql;
```

4. Crear `historial_cronologico` usando el script del informe de triggers, si la tabla todavía no existe.
5. Crear y ejecutar los triggers adaptados a la tabla que se desea auditar.
6. Actualizar el navegador de objetos y confirmar que la tabla de auditoría y los triggers aparezcan en `huellavet_db`.
7. Ejecutar operaciones de prueba autorizadas sobre un registro de laboratorio.
8. Consultar el historial y comprobar el tipo de operación y los valores que guardó el trigger.

## 5. Consultas del historial

### 5.1 Consultar todos los eventos, del más reciente al más antiguo

```sql
SELECT id_historial, tabla_afectada, id_registro, operacion,
			 fecha_evento, usuario_bd, datos_anteriores, datos_nuevos
FROM historial_cronologico
ORDER BY fecha_evento DESC, id_historial DESC;
```

### 5.2 Consultar en orden cronológico ascendente

```sql
SELECT id_historial, tabla_afectada, id_registro, operacion,
			 fecha_evento, usuario_bd, datos_anteriores, datos_nuevos
FROM historial_cronologico
ORDER BY fecha_evento ASC, id_historial ASC;
```

El identificador del evento se incluye como segundo criterio de orden para que el resultado sea estable si dos operaciones reciben la misma marca de tiempo.

### 5.3 Consultar los cambios de un registro

Sustituir los valores de ejemplo por el nombre real de la tabla y la clave del registro que se quiera revisar:

```sql
SELECT id_historial, operacion, fecha_evento, usuario_bd,
			 datos_anteriores, datos_nuevos
FROM historial_cronologico
WHERE tabla_afectada = 'NOMBRE_TABLA'
	AND id_registro = 'ID_DEL_REGISTRO'
ORDER BY fecha_evento ASC, id_historial ASC;
```

### 5.4 Contar eventos por operación

```sql
SELECT operacion, COUNT(*) AS cantidad
FROM historial_cronologico
GROUP BY operacion
ORDER BY operacion;
```

## 6. Validación funcional

La prueba debe realizarse en un ambiente controlado y con un registro destinado a pruebas. Guardar o respaldar los datos antes de ejecutar cambios; una eliminación no debe probarse sobre información real sin autorización.

1. Insertar el registro de prueba en la tabla elegida. El historial debe mostrar una fila `INSERT`, con `datos_anteriores` nulo y `datos_nuevos` con los valores capturados.
2. Actualizar uno o más campos del mismo registro. Debe aparecer una fila `UPDATE` con los valores previos y posteriores.
3. Eliminar el registro de prueba. Debe aparecer una fila `DELETE` con los valores anteriores y `datos_nuevos` nulo.
4. Ejecutar la consulta del registro específico en orden ascendente. La secuencia esperada es `INSERT`, `UPDATE` y `DELETE`.
5. Verificar que `fecha_evento` avance en la secuencia y que `id_historial` permita ordenar eventos ocurridos en el mismo instante.
6. Comprobar que las filas históricas continúan presentes después de eliminar el registro original.

Si una operación no aparece, comprobar que el trigger correspondiente exista, esté asociado a la tabla esperada y no haya errores en el panel de ejecución de DBeaver.

## 7. Interpretación y límites

- El historial refleja solamente las tablas y columnas cubiertas por los triggers instalados.
- Los datos anteriores y nuevos dependen de las columnas incluidas por el desarrollador en `JSON_OBJECT`.
- `usuario_bd` es la cuenta MySQL, no necesariamente la identidad de la persona que inició sesión en una aplicación.
- La hora depende de la configuración horaria del servidor MySQL.
- Las sentencias que modifican datos de forma directa y los permisos del usuario deben controlarse; la auditoría no reemplaza respaldos ni controles de acceso.

## 8. Evidencias fotográficas

Tomar las capturas en DBeaver conforme se complete cada paso de la implementación. Incorporarlas progresivamente en esta sección, evitando exponer contraseñas o datos personales:

- conexión activa y selección de `huellavet_db`;
- definición de la tabla `historial_cronologico`;
- triggers creados y asociados a la tabla auditada;
- resultado de la consulta que muestre la secuencia de prueba `INSERT`, `UPDATE` y `DELETE`.

## 9. Conclusión

Un historial cronológico basado en triggers ofrece trazabilidad de las operaciones seleccionadas y conserva una representación de los valores auditados en el momento del cambio. Para validar la implementación en HuellaVet, se deben completar los nombres reales del esquema, ejecutar las pruebas desde DBeaver y adjuntar las evidencias obtenidas.

## 10. Referencias dentro del proyecto

- [Informe de implementación de triggers](informe_Triggers.md)
- [Informe de instalación de motores](INFORME_INSTALACION_MOTORES.md)
