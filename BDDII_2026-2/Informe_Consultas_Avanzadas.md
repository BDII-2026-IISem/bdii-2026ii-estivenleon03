# INFORME DE CONSULTAS AVANZADAS Y PROCEDIMIENTOS ALMACENADOS - HUELLAVET

## 1. Consultas avanzadas en MySQL

### 1.1 Proyección de datos de propietarios

**1. Título del punto:** Proyección básica sobre `owners`.

**2. Narrativa explicativa:** La consulta selecciona solo los datos necesarios para identificar y verificar a los propietarios activos. En HuellaVet, esto facilita revisar la información de contacto e identificación sin transferir todas las columnas de la tabla.

**3. Código SQL de la consulta:**

```sql
SELECT name, doc_type, doc_number, is_active
FROM owners;
```

**4. Imagen 1 (evidencia de consulta):**

![Consulta y resultado de propietarios](evidencias/consultas_avanzadas/Captura%20de%20pantalla%202026-09-30%20114910.png)

**5. Código SQL del procedimiento almacenado:**

```sql
DELIMITER //
CREATE PROCEDURE sp_get_basic_owners()
BEGIN
	SELECT name, doc_type, doc_number, is_active
	FROM owners;
END //
DELIMITER ;
```

**6. Imagen 2 (evidencia de ejecución del procedimiento):**

![Ejecución de sp_get_basic_owners](evidencias/consultas_avanzadas/Captura%20de%20pantalla%202026-09-30%20114910.png)

### 1.2 Cruce de propietarios, mascotas y citas

**1. Título del punto:** Combinación de tablas mediante `INNER JOIN` y `WHERE` implícito.

**2. Narrativa explicativa:** Los cruces relacionan a cada propietario con sus mascotas y citas para mostrar información útil en una sola consulta. Esto permite al personal de HuellaVet revisar quién es responsable de cada mascota y consultar el contexto de sus atenciones. La rutina llamada `sp_get_appointments_full_join` usa `INNER JOIN`; no realiza un `FULL JOIN`.

**3. Código SQL de la consulta:**

```sql
-- Relacionar propietarios, mascotas y citas con INNER JOIN
SELECT o.name AS propietario,
	   p.name AS mascota,
	   a.start_time,
	   a.reason,
	   a.status
FROM owners AS o
INNER JOIN pets AS p ON p.owner_id = o.id
INNER JOIN appointments AS a ON a.pet_id = p.id;

-- Relacionar propietarios y mascotas mediante la condición WHERE
SELECT o.name AS propietario,
	   o.doc_number,
	   p.name AS mascota,
	   p.species,
	   p.breed
FROM owners AS o, pets AS p
WHERE o.id = p.owner_id;
```

**4. Imagen 1 (evidencia de consulta):**

![Resultados del cruce de propietarios, mascotas y citas](evidencias/consultas_avanzadas/Captura%20de%20pantalla%202026-09-30%20113539.png)

**5. Código SQL del procedimiento almacenado:**

```sql
DELIMITER //
CREATE PROCEDURE sp_get_appointments_full_join()
BEGIN
	SELECT o.name AS propietario,
		   p.name AS mascota,
		   a.start_time,
		   a.reason,
		   a.status
	FROM owners AS o
	INNER JOIN pets AS p ON p.owner_id = o.id
	INNER JOIN appointments AS a ON a.pet_id = p.id;
END //

CREATE PROCEDURE sp_get_owners_pets_where()
BEGIN
	SELECT o.name AS propietario,
		   o.doc_number,
		   p.name AS mascota,
		   p.species,
		   p.breed
	FROM owners AS o, pets AS p
	WHERE o.id = p.owner_id;
END //
DELIMITER ;
```

**6. Imagen 2 (evidencia de ejecución del procedimiento):**

![Ejecución de los procedimientos de cruce](evidencias/consultas_avanzadas/Captura%20de%20pantalla%202026-09-30%20121826.png)

### 1.3 Orden descendente de citas

**1. Título del punto:** Ordenamiento de citas con `ORDER BY ... DESC`.

**2. Narrativa explicativa:** Ordenar por fecha de inicio descendente muestra primero las citas más recientes. Esta presentación ayuda al equipo de HuellaVet a revisar rápidamente la agenda próxima y comprobar el estado de las últimas citas registradas.

**3. Código SQL de la consulta:**

```sql
SELECT id, pet_id, veterinarian_id, start_time, end_time, status
FROM appointments
ORDER BY start_time DESC;
```

**4. Imagen 1 (evidencia de consulta):**

![Citas ordenadas por fecha descendente](evidencias/consultas_avanzadas/Captura%20de%20pantalla%202026-09-30%20120750.png)

**5. Código SQL del procedimiento almacenado:**

```sql
DELIMITER //
CREATE PROCEDURE sp_get_appointments_desc()
BEGIN
	SELECT id, pet_id, veterinarian_id, start_time, end_time, status
	FROM appointments
	ORDER BY start_time DESC;
END //
DELIMITER ;
```

**6. Imagen 2 (evidencia de ejecución del procedimiento):**

![Ejecución de sp_get_appointments_desc](evidencias/consultas_avanzadas/Captura%20de%20pantalla%202026-09-30%20120848.png)

### 1.4 Filtrado de citas por estado

**1. Título del punto:** Filtrado de citas con `WHERE` y parámetro de procedimiento.

**2. Narrativa explicativa:** Filtrar por estado permite separar citas completadas de las que siguen programadas. En HuellaVet, esta distinción sirve para hacer seguimiento operativo y consultar únicamente las atenciones relevantes para cada tarea.

**3. Código SQL de la consulta:**

```sql
-- Citas completadas con JOIN explícito
SELECT o.name AS propietario,
	   p.name AS mascota,
	   a.start_time,
	   a.status
FROM owners AS o
JOIN pets AS p ON p.owner_id = o.id
JOIN appointments AS a ON a.pet_id = p.id
WHERE a.status = 'COMPLETED';

-- Citas programadas con condición de unión en WHERE
SELECT o.name AS propietario,
	   p.name AS mascota,
	   a.start_time,
	   a.status
FROM owners AS o, pets AS p, appointments AS a
WHERE o.id = p.owner_id
  AND p.id = a.pet_id
  AND a.status = 'SCHEDULED';
```

**4. Imagen 1 (evidencia de consulta):**

![Resultados de citas completadas y programadas](evidencias/consultas_avanzadas/Captura%20de%20pantalla%202026-09-30%20120950.png)

**5. Código SQL del procedimiento almacenado:**

```sql
DELIMITER //
CREATE PROCEDURE sp_get_appointments_by_status(IN p_status VARCHAR(20))
BEGIN
	SELECT o.name AS propietario,
		   p.name AS mascota,
		   a.start_time,
		   a.status
	FROM owners AS o
	JOIN pets AS p ON p.owner_id = o.id
	JOIN appointments AS a ON a.pet_id = p.id
	WHERE a.status = p_status;
END //
DELIMITER ;
```

**6. Imagen 2 (evidencia de ejecución del procedimiento):**

![Ejecución de sp_get_appointments_by_status](evidencias/consultas_avanzadas/Captura%20de%20pantalla%202026-09-30%20121012.png)

### 1.5 Búsqueda de propietarios por correo

**1. Título del punto:** Búsqueda de patrones de correo con `LIKE`.

**2. Narrativa explicativa:** `LIKE` permite localizar correos por prefijo o por dominio sin conocer la dirección completa. Esta búsqueda ayuda a encontrar clientes de un proveedor específico o a revisar grupos de contacto; el cruce adicional identifica las mascotas y citas asociadas.

**3. Código SQL de la consulta:**

```sql
-- Correos que comienzan por la letra m
SELECT name, email, phone
FROM owners
WHERE email LIKE 'm%';

-- Correos que contienen gmail
SELECT name, email, phone
FROM owners
WHERE email LIKE '%gmail%';

-- Citas completadas de propietarios cuyo correo comienza por m
SELECT o.name AS propietario,
	   o.email,
	   p.name AS mascota,
	   a.status
FROM owners AS o
JOIN pets AS p ON p.owner_id = o.id
JOIN appointments AS a ON a.pet_id = p.id
WHERE a.status = 'COMPLETED'
  AND o.email LIKE 'm%';
```

**4. Imagen 1 (evidencia de consulta):**

![Consultas de búsqueda de propietarios por correo](evidencias/consultas_avanzadas/Captura%20de%20pantalla%202026-09-30%20122007.png)

**5. Código SQL del procedimiento almacenado:**

```sql
DELIMITER //
CREATE PROCEDURE sp_search_owners_by_email_pattern(IN p_pattern VARCHAR(100))
BEGIN
	SELECT o.name AS propietario,
		   o.email,
		   p.name AS mascota,
		   a.status
	FROM owners AS o
	JOIN pets AS p ON p.owner_id = o.id
	JOIN appointments AS a ON a.pet_id = p.id
	WHERE o.email LIKE CONCAT('%', p_pattern, '%');
END //
DELIMITER ;
```

**6. Imagen 2 (evidencia de ejecución del procedimiento):**

![Ejecución de la búsqueda de correo por patrón](evidencias/consultas_avanzadas/Captura%20de%20pantalla%202026-09-30%20121925.png)

### 1.6 Consulta de pagos en un intervalo de fechas

**1. Título del punto:** Filtrado temporal con `BETWEEN`.

**2. Narrativa explicativa:** El intervalo de fechas permite consultar pagos efectuados dentro de un periodo definido y ordenarlos cronológicamente. HuellaVet puede utilizarlo para conciliaciones, reportes de ingresos y revisión de pagos asociados a cada mascota.

**3. Código SQL de la consulta:**

```sql
SELECT o.name AS propietario,
	   p.name AS mascota,
	   pay.amount,
	   pay.method,
	   pay.payment_date
FROM owners AS o
JOIN pets AS p ON p.owner_id = o.id
JOIN appointments AS a ON a.pet_id = p.id
JOIN payments AS pay ON pay.appointment_id = a.id
WHERE pay.payment_date BETWEEN '2025-01-01 00:00:00'
						   AND '2026-12-31 23:59:59'
ORDER BY pay.payment_date ASC;
```

**4. Imagen 1 (evidencia de consulta):**

![Pagos consultados por intervalo de fechas](evidencias/consultas_avanzadas/Captura%20de%20pantalla%202026-09-30%20122205.png)

**5. Código SQL del procedimiento almacenado:**

```sql
DELIMITER //
CREATE PROCEDURE sp_get_payments_between_dates(
	IN p_start_date DATETIME,
	IN p_end_date DATETIME
)
BEGIN
	SELECT o.name AS propietario,
		   p.name AS mascota,
		   pay.amount,
		   pay.method,
		   pay.payment_date
	FROM owners AS o
	JOIN pets AS p ON p.owner_id = o.id
	JOIN appointments AS a ON a.pet_id = p.id
	JOIN payments AS pay ON pay.appointment_id = a.id
	WHERE pay.payment_date BETWEEN p_start_date AND p_end_date
	ORDER BY pay.payment_date ASC;
END //
DELIMITER ;
```

**6. Imagen 2 (evidencia de ejecución del procedimiento):**

![Ejecución de sp_get_payments_between_dates](evidencias/consultas_avanzadas/Captura%20de%20pantalla%202026-09-30%20122420.png)

### 1.7 Propietarios con mayor gasto

**1. Título del punto:** Agregación de pagos por propietario con `GROUP BY` y `HAVING`.

**2. Narrativa explicativa:** Agrupar pagos por propietario permite identificar el gasto total y el número de pagos de cada cliente. El umbral parametrizado ayuda a HuellaVet a preparar reportes de clientes con mayor volumen de pagos sin cambiar la consulta.

**3. Código SQL de la consulta:**

```sql
SELECT o.id,
	   o.name AS propietario,
	   o.email,
	   SUM(pay.amount) AS total_anual,
	   COUNT(pay.id) AS total_pagos
FROM owners AS o
JOIN pets AS p ON p.owner_id = o.id
JOIN appointments AS a ON a.pet_id = p.id
JOIN payments AS pay ON pay.appointment_id = a.id
GROUP BY o.id, o.name, o.email
HAVING SUM(pay.amount) >= 50000.00
ORDER BY total_anual DESC;
```

**4. Imagen 1 (evidencia de consulta):**

![Resumen de gasto por propietario](evidencias/consultas_avanzadas/Captura%20de%20pantalla%202026-09-30%20122558.png)

**5. Código SQL del procedimiento almacenado:**

```sql
DELIMITER //
CREATE PROCEDURE sp_get_top_spending_owners(IN p_min_amount DECIMAL(10, 2))
BEGIN
	SELECT o.id,
		   o.name AS propietario,
		   o.email,
		   SUM(pay.amount) AS total_anual,
		   COUNT(pay.id) AS total_pagos
	FROM owners AS o
	JOIN pets AS p ON p.owner_id = o.id
	JOIN appointments AS a ON a.pet_id = p.id
	JOIN payments AS pay ON pay.appointment_id = a.id
	GROUP BY o.id, o.name, o.email
	HAVING SUM(pay.amount) >= p_min_amount
	ORDER BY total_anual DESC;
END //
DELIMITER ;
```

**6. Imagen 2 (evidencia de ejecución del procedimiento):**

![Ejecución de sp_get_top_spending_owners](evidencias/consultas_avanzadas/Captura%20de%20pantalla%202026-09-30%20122253.png)
