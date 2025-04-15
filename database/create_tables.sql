CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- Se requiere la extensión para la generacion automatica de UUIDS de las entidades 
CREATE SCHEMA IF NOT EXISTS meli; --se crea schema para la base de datos



CREATE TABLE "meli"."dim_customer" (
	"customer_id" UUID DEFAULT gen_random_uuid(),
	"email" VARCHAR(255),
	"first_name" VARCHAR(255),
	"last_name" VARCHAR(255),
	"gender" CHAR(1),
	"address_street_name" VARCHAR(255),
	"address_zip_code" VARCHAR(255),
	"birth_date" DATE,
	"phone_area_code" VARCHAR(10),
	"phone_number" VARCHAR(20),
	"identification_type" VARCHAR(255),
	"identification_number" VARCHAR(255),
	"date_created" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	"last_updated" TIMESTAMP,
	PRIMARY KEY("customer_id")
);

CREATE TABLE "meli"."dim_item" (
	"item_id" UUID DEFAULT gen_random_uuid(),
	"status" VARCHAR(255) DEFAULT 'Active',
	"deactivation_date" TIMESTAMP,
	"category_id" UUID,
	"description" VARCHAR(255),
	"price" DECIMAL(10,2),
	"currency" VARCHAR(3),
	"sku" VARCHAR(12) UNIQUE,
	"date_created" TIMESTAMP,
	"last_updated" TIMESTAMP,
	PRIMARY KEY("item_id")
);

CREATE INDEX "dim_item_index_0"
ON "meli"."dim_item" ("category_id", "status");

CREATE TABLE "meli"."dim_category_item" (
	"category_id" UUID DEFAULT gen_random_uuid(),
	"name" VARCHAR(255),
	"path" TEXT,
	-- referencia a la categoria padre.
	"parent_category_id" UUID,
	"date_created" TIMESTAMP,
	"last_updated" TIMESTAMP,
	PRIMARY KEY("category_id")
);

CREATE INDEX "dim_category_item_index_0"
ON "meli"."dim_category_item" ("parent_category_id", "path");

CREATE TABLE "meli"."fact_order" (
	"order_id" UUID DEFAULT gen_random_uuid(),
	"client_id" UUID,
	"buyer_id" UUID,
	"status" VARCHAR(255),
	"created_date" TIMESTAMP,
	"payment_method" UUID,
	"quantity" INTEGER,
	"item_id" UUID,
	"unit_price" DECIMAL(10,2),
	"total_amount" DECIMAL,
	"payment_id" UUID NULL,
	PRIMARY KEY("order_id")
);

CREATE TABLE "meli"."fact_payment" (
	"payment_id" UUID DEFAULT gen_random_uuid(),
	"date_created" TIMESTAMP,
	"date_approved" TIMESTAMP,
	"payment_type" VARCHAR(255),
	"status" VARCHAR(255),
	"currency" VARCHAR(3),
	"description" TEXT,
	"payer_id" UUID,
	"transaction_amount" DECIMAL(10,2),
	PRIMARY KEY("payment_id")
);

ALTER TABLE "meli"."dim_category_item"
ADD FOREIGN KEY("parent_category_id") REFERENCES "meli"."dim_category_item"("category_id")
ON UPDATE NO ACTION ON DELETE SET NULL;

ALTER TABLE "meli"."dim_item"
ADD FOREIGN KEY("category_id") REFERENCES "meli"."dim_category_item"("category_id")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "meli"."fact_order"
ADD FOREIGN KEY("client_id") REFERENCES "meli"."dim_customer"("customer_id")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "meli"."fact_order"
ADD FOREIGN KEY("buyer_id") REFERENCES "meli"."dim_customer"("customer_id")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "meli"."fact_order"
ADD FOREIGN KEY("item_id") REFERENCES "meli"."dim_item"("item_id")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "meli"."fact_order"
ADD FOREIGN KEY("payment_id") REFERENCES "meli"."fact_payment"("payment_id")
ON UPDATE NO ACTION ON DELETE NO ACTION;