/* 
1. Listar los usuarios que cumplan años el día de hoy cuya cantidad de ventas realizadas en enero 2020 sea superior a 1500. 
*/

SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    c.birth_date,
    COUNT(o.order_id) AS total_ventas_enero_2020  -- Contador de Ventas
FROM 
    meli.dim_customer c
left JOIN 
    meli.fact_order o ON c.customer_id = o.client_id
WHERE 
    -- Filtra usuarios que cumplen años hoy comparando por Mes y Dia 
    TO_CHAR(c.birth_date, 'MM-DD') = TO_CHAR(CURRENT_DATE, 'MM-DD')
    -- Filtra ventas de enero 2020
    AND o.created_date >= '2020-01-01 00:00:00'
    AND o.created_date < '2020-02-01 00:00:00'
    -- Asegura que sean ventas completadas
GROUP BY 
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    c.birth_date
HAVING 
    COUNT(o.order_id) > 1500;


/* 
2. Por cada mes del 2020, se solicita el top 5 de usuarios que más vendieron($) en la categoría Celulares. 
Se requiere el mes y año de análisis, nombre y apellido del vendedor, cantidad de ventas realizadas, cantidad de productos vendidos y el monto total transaccionado.  
*/

WITH ventas_mensuales AS (
    -- Cálculo de ventas mensuales por vendedor en categoría Celulares con tabla auxiliar o intermedia 
    SELECT 
        TO_CHAR(o.created_date, 'YYYY-MM') AS mes_anio,
        EXTRACT(MONTH FROM o.created_date) AS mes_num,
        c.customer_id,
        c.first_name,
        c.last_name,
        COUNT(DISTINCT o.order_id) AS cantidad_ventas,
        SUM(o.quantity) AS cantidad_productos,
        SUM(o.total_amount) AS monto_total,
        -- Calculamos el Ranking en base al monto total dentro de cada mes
        RANK() OVER (
            PARTITION BY TO_CHAR(o.created_date, 'YYYY-MM') 
            ORDER BY SUM(o.total_amount) DESC
        ) AS ranking
    FROM meli.fact_order o
    JOIN meli.dim_customer c ON o.client_id = c.customer_id
    JOIN meli.dim_item i ON o.item_id = i.item_id
    JOIN meli.dim_category_item cat ON i.category_id = cat.category_id
    WHERE 
        -- Filtro por año 2020
        date_part('year',o.created_date)=2020
        -- Filtro por categoría Celulares se toma la categoria, o totas las categorias que en el path tengan Celulares
        AND (cat.name = 'Celulares' OR cat.path LIKE '%Celulares%')
        -- Solo ordenes con estado completada
        AND o.status = 'Completed'
    GROUP BY 
        TO_CHAR(o.created_date, 'YYYY-MM'),
        EXTRACT(MONTH FROM o.created_date),
        c.customer_id,
        c.first_name,
        c.last_name
)
-- Selección y filtro del top 5  de usuarios por mes
SELECT 
    mes_anio,
    first_name AS nombre,
    last_name AS apellido,
    cantidad_ventas,
    cantidad_productos,
    monto_total
FROM 
    ventas_mensuales
WHERE 
    ranking <= 5
ORDER BY 
    mes_num, ranking;


/*3. Se solicita poblar una nueva tabla con el precio y estado de los Ítems a fin del día. Tener en cuenta que debe ser reprocesable. 
Vale resaltar que en la tabla Item, vamos a tener únicamente el último estado informado por la PK definida.(Se puede resolver a través de StoredProcedure) 
*/

-- Creamos la nueva tabla para almacenar el precio y estado de los ítems
CREATE TABLE meli.item_price_status_end_of_day (
    snapshot_id uuid DEFAULT gen_random_uuid(),  -- ID del snapshot
    item_id uuid NOT NULL,           -- ID del ítem
    status varchar(255),             -- Estado del ítem
    price numeric(10, 2),            -- Precio del ítem
    record_date timestamp,           -- Fecha y hora en que se registró
    processed_at timestamp DEFAULT CURRENT_TIMESTAMP,  -- Fecha y hora de la ejecución del proceso
    PRIMARY KEY (snapshot_id)  -- Clave primaria compuesta por el ID y la fecha
);

-- Creamos el SP para registrar el estado y precio de los ítems al final del día
CREATE OR REPLACE PROCEDURE meli.record_item_price_status_end_of_day()
LANGUAGE plpgsql
AS $$
BEGIN
    -- Select e insert de  estado, precio y la fecha del snapshot
    INSERT INTO meli.item_price_status_end_of_day (item_id, status, price, record_date)
    SELECT 
        item_id,
        status,
        price,
        CURRENT_DATE  -- La fecha del snapshot es la fecha en la que se procesa el insert
    FROM meli.dim_item
END;
$$;

