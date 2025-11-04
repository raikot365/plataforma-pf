import asyncio, ssl, certifi, logging, os, aiomysql, json, traceback
import aiomqtt

logging.basicConfig(format='%(asctime)s - cliente mqtt - %(levelname)s:%(message)s',
                    level=logging.INFO, datefmt='%d/%m/%Y %H:%M:%S %z')

async def guardar_en_db(sql, valores):
    try:
        conn = await aiomysql.connect(
            host=os.environ["MARIADB_SERVER"],
            port=3306,
            user=os.environ["MARIADB_USER"],
            password=os.environ["MARIADB_USER_PASS"],
            db=os.environ["MARIADB_DB"]
        )
        async with conn.cursor() as cur:
            await cur.execute(sql, valores)
            await conn.commit()
        await conn.ensure_closed()
    except Exception:
        logging.error(traceback.format_exc())

async def main():
    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True
    tls_context.load_default_certs()

    async with aiomqtt.Client(
        os.environ["SERVIDOR"],
        username=os.environ["MQTT_USR"],
        password=os.environ["MQTT_PASS"],
        port=int(os.environ["PUERTO_MQTTS"]),
        tls_context=tls_context,
    ) as client:

        topico1 = os.environ.get('TOPICO1', 'consumos')
        topico2 = os.environ.get('TOPICO2', 'totales')

        await client.subscribe([(topico1, 0), (topico2, 0)])
        logging.info(f"Suscrito a: {topico1} y {topico2}")

        async for message in client.messages:
            try:
                topic = str(message.topic)
                datos = json.loads(message.payload.decode('utf-8'))
                logging.info(f"Mensaje en {topic}: {datos}")

                if topic == topico1:
                    # Insertar en la tabla consumos
                    sql = """INSERT INTO consumos (nodo, consumo, prioridad)
                             VALUES (%s, %s, %s)"""
                    valores = (datos.get('nodo'), datos.get('consumo'), datos.get('prioridad'))
                    await guardar_en_db(sql, valores)

                elif topic == topico2:
                    # Insertar en la tabla totales
                    sql = """INSERT INTO totales (potencia, corriente, tension, consumo_total)
                             VALUES (%s, %s, %s, %s)"""
                    valores = (
                        datos.get('potencia'),
                        datos.get('corriente'),
                        datos.get('tension'),
                        datos.get('consumo_total')
                    )
                    await guardar_en_db(sql, valores)

                else:
                    logging.warning(f"Mensaje recibido en tópico no esperado: {topic}")

            except Exception:
                logging.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
