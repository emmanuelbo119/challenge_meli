import requests
import datetime
import csv
import os
import uuid
import logging
import time
from typing import List, Dict, Any
from pydantic import BaseModel, validator
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Numeric, DateTime, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from app.models import *
import pytz



# Cargamos las variables de entorno desde el archivo .env
load_dotenv()

DB_URL = os.getenv('DATABASE_URL')  # Cadena de conexión a la base de datos
API_URL= os.getenv('URL_API')  # API URL
OUTPUT_FILE = 'data_currencies.csv'

# Set up logging
logging.basicConfig(
    level=logging.INFO,  # Set to INFO level
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Logs to console
        logging.FileHandler('currency_extraction.log')  ]# Logs file
)
logger = logging.getLogger()

# Create the database engine and session
engine = create_engine(DB_URL)

# Crear todas las tablas definidas en los modelos
Base.metadata.create_all(engine)

#Make a session factory
Session = sessionmaker(autoflush=False, bind=engine)
session = Session()



def fetch_api_currencies():
    """
    Fetches currency data from the API and returns a dictionary with currency codes and names.
    If an error occurs, logs the error and returns an empty dictionary.
    """
    try:
        response = requests.get(f'{API_URL}json/available/uniq')
        response.raise_for_status()  # Exception error 
        currencies_data = response.json()

        # Guardar los datos en la base de datos
        for code, name in currencies_data.items():
            # Verifica si ya existe la moneda en la base de datos
            existing_currency = session.query(Currency).filter_by(code=code).first()
            if not existing_currency:
                # Crear una nueva instancia de Currency
                new_currency = Currency(code=code, name=name)
                session.add(new_currency)

        # Commit los cambios en la base de datos
        session.commit()
        logger.info("Currencies data successfully saved to the database.")
        
        return currencies_data
    except requests.RequestException as e:
        logger.error(f"Error fetching data from API: {e}")
        return {}


def fetch_currency_conversions():
    """
    Fetches available currency conversions from the API and saves them to the database.
    Each conversion is stored with references to the base and destination currencies.
    """
    try:
        response = requests.get(f'{API_URL}json/available')
        response.raise_for_status()
        conversions_data = response.json()
        
        logger.info(f"Retrieved {len(conversions_data)} currency conversions from API")
        
        # Para cada par de conversión
        for conversion_code, conversion_name in conversions_data.items():
            # Dividir la clave para obtener los códigos de moneda base y destino
            base_code, dest_code = conversion_code.split('-')
            
            # Buscar las monedas en la base de datos
            base_currency = session.query(Currency).filter_by(code=base_code).first()
            dest_currency = session.query(Currency).filter_by(code=dest_code).first()
            
            # Verificar si ambas monedas existen en la base de datos
            if base_currency and dest_currency:
                # Verificar si la conversión ya existe
                existing_conversion = session.query(CurrencyConversion).filter_by(
                    base_currency_id=base_currency.id,
                    destination_currency_id=dest_currency.id
                ).first()
                
                if not existing_conversion:
                    # Crear nueva conversión
                    new_conversion = CurrencyConversion(
                        base_currency_id=base_currency.id,
                        destination_currency_id=dest_currency.id,
                        name=conversion_name,
                        date_time=datetime.datetime.utcnow()
                    )
                    session.add(new_conversion)
                    logger.info(f"Added new conversion: {conversion_code} - {conversion_name}")
            else:
                logger.warning(f"Could not find currencies for conversion {conversion_code}")
        
        # Commit de todos los cambios
        session.commit()
        logger.info("Currency conversions successfully saved to database")
        
        return conversions_data
    except requests.RequestException as e:
        logger.error(f"Error fetching currency conversions: {e}")
        return {}


def fetch_currency_quotes():
    """
    Fetches currency quotes from the API for available currency conversions
    and saves them to the database.
    """
    try:
        # Obtener todas las conversiones disponibles de la base de datos
        conversions = session.query(CurrencyConversion).all()
        
        if not conversions:
            logger.warning("No currency conversions found in the database")
            return {}
        
        # Crear listas para procesar los datos en lotes
        all_quotes_data = {}
        
        # Procesar las conversiones en lotes de 10
        for i in range(0, len(conversions), 10):
            batch = conversions[i:i+10]
            
            # Construir la cadena de pares de monedas para la consulta
            moedas = []
            for conv in batch:
                # Obtener las monedas base y destino
                base_currency = session.query(Currency).filter_by(id=conv.base_currency_id).first()
                dest_currency = session.query(Currency).filter_by(id=conv.destination_currency_id).first()
                
                if base_currency and dest_currency:
                    moedas.append(f"{base_currency.code}-{dest_currency.code}")
            
            # Si no hay pares válidos en este lote, continuar con el siguiente
            if not moedas:
                continue
            
            # Construir la URL con los pares de monedas
            moedas_str = ','.join(moedas)
            quote_url = f'{API_URL}json/last/{moedas_str}'
            
            logger.info(f"Fetching quotes for: {moedas_str}")
            
            # Hacer la solicitud a la API
            response = requests.get(quote_url)
            response.raise_for_status()
            quotes_data = response.json()
            
            # Actualizar el diccionario con los datos obtenidos
            all_quotes_data.update(quotes_data)
            
            # Guardar cada cotización en la base de datos
            for key, quote in quotes_data.items():
                # Extraer los códigos base y destino del par
                base_code = quote.get("code")
                dest_code = quote.get("codein")
                
                # Buscar la conversión correspondiente
                base_currency = session.query(Currency).filter_by(code=base_code).first()
                dest_currency = session.query(Currency).filter_by(code=dest_code).first()
                
                if base_currency and dest_currency:
                    conversion = session.query(CurrencyConversion).filter_by(
                        base_currency_id=base_currency.id,
                        destination_currency_id=dest_currency.id
                    ).first()
                    
                    if conversion:
                        # Crear nueva cotización
                        new_quote = CurrencyQuote(
                            conversion_id=conversion.id,
                            code=quote.get("code"),
                            codein=quote.get("codein"),
                            name=quote.get("name"),
                            high=quote.get("high"),
                            low=quote.get("low"),
                            var_bid=quote.get("varBid"),
                            pct_change=quote.get("pctChange"),
                            bid=quote.get("bid"),
                            ask=quote.get("ask"),
                            timestamp=quote.get("timestamp"),
                            create_date=quote.get("create_date")
                        )
                        session.add(new_quote)
                        logger.info(f"Added quote for: {quote.get('name')}")
            
            # Confirmar cambios en cada lote
            session.commit()
            
            # Esperar un poco para no sobrecargar la API
            time.sleep(1)
        
        logger.info("Currency quotes successfully saved to database")
        return all_quotes_data
    
    except requests.RequestException as e:
        logger.error(f"Error fetching currency quotes: {e}")
        session.rollback()
        return {}
    except Exception as e:
        logger.error(f"Error processing currency quotes: {e}")
        session.rollback()
        return {}




def normalize_data(session):
    """
    Normalizes the data from the database to create a list of dictionaries.
    """
    # Realizar la consulta para obtener los datos de CurrencyQuotes
    query = session.query(
        CurrencyQuote.code,
        CurrencyQuote.codein,
        CurrencyQuote.bid,
        CurrencyQuote.ask,
        CurrencyQuote.create_date
    ).all()

    normalized_data = []
    for row in query:
        # Crear un diccionario con los datos normalizados
        normalized_data.append({
            "base_currency": row.code,
            "destination_currency": row.codein,
            "purchase_value": row.bid,
            "sale_value": row.ask,
            "date_time": row.create_date
        })
    
    return normalized_data

def save_csv(data, output_file):
    """
    Saves the normalized data to a CSV file.
    """
    fieldnames = ['base_currency', 'destination_currency', 'purchase_value', 'sale_value', 'date_time']
    
    with open(output_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"Data successfully saved to {output_file}")


def show_menu():
    print("\nMenu:")
    print("1. Consumir datos de las monedas")
    print("2. Consumir datos de las tasas de cambio")
    print("3. Consumir datos de cotizaciones de monedas")
    print("4. Guardar los datos en un archivo CSV")
    print("5. Salir")

def main():
    while True:
        show_menu()
        choice = input("Elige una opción (1-5): ")
        
        if choice == '1':
            logger.info("Inicio de consumo de API de monedas...")
            fetch_api_currencies()
            logger.info("Data extraction Currencies completed successfully!")
        
        elif choice == '2':
            logger.info("Inicio de consumo de API de tasas de cambio...")
            fetch_currency_conversions()
            logger.info("Data extraction Currencies conversions completed successfully!")
        
        elif choice == '3':
            logger.info("Inicio de consumo de API de cotizaciones de monedas...")
            fetch_currency_quotes()
            logger.info("Data extraction Currencies Quotes successfully!")
        
        elif choice == '4':
            logger.info("Inicio de la normalización de datos...")
            normalized_data = normalize_data(session)
            logger.info("Data normalization completed successfully!")
            logger.info("Guardando los datos en un archivo CSV...")
            output_file = 'currency_quotes.csv'
            save_csv(normalized_data, output_file)
            logger.info(f"Data saved successfully to {output_file}")       
        elif choice == '5':
            logger.info("Saliendo del programa...")
            break
        
        else:
            print("Opción inválida. Por favor, elija una opción entre 1 y 6.")

if __name__ == "__main__":
    main()
