# filepath: mqtt_postgres_ingestor/mqtt_postgres_ingestor/ingestor.py

import paho.mqtt.client as mqtt
import psycopg2
import psycopg2.extras
import json
import time
import os
import threading
from queue import Queue

# --- PERFORMANCE TUNING CONFIGURATION ---
BATCH_SIZE = 100
FLUSH_INTERVAL = 1.0  # seconds

# --- MQTT BROKER CONFIGURATION ---
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "127.0.0.1")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "default_username")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "default_password")
HA_DISCOVERY_PREFIX = "homeassistant"
ESPHOME_DISCOVERY_PREFIX = "esphome/discover"

# --- POSTGRESQL/TIMESCALE DB CONFIGURATION ---
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "telemetry_db")
DB_USER = os.getenv("DB_USER", "telegraf_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "default_password")

# Use separate queues for each table for clarity and robustness
discovery_queue = Queue()
entity_queue = Queue()
state_queue = Queue()
status_queue = Queue()
command_queue = Queue()
stop_event = threading.Event()

def setup_database_tables(conn):
    """Creates the necessary tables if they don't exist."""
    with conn.cursor() as cursor:
        print("Ensuring database tables exist...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discovery_data (
                time TIMESTAMPTZ NOT NULL,
                device_name TEXT PRIMARY KEY,
                ip_address TEXT,
                mac_address TEXT,
                version TEXT,
                platform TEXT,
                board TEXT,
                network TEXT,
                raw_payload JSONB
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entity (
                time TIMESTAMPTZ NOT NULL,
                unique_id TEXT PRIMARY KEY,
                device_name TEXT,
                component_type TEXT,
                name TEXT,
                state_topic TEXT,
                command_topic TEXT,
                raw_payload JSONB
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_status (
                time TIMESTAMPTZ NOT NULL,
                device_name TEXT,
                status TEXT,
                raw_payload JSONB
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command (
                time TIMESTAMPTZ NOT NULL,
                device_id TEXT,
                component_id TEXT,
                command TEXT,
                raw_payload JSONB
            );
        """)
        conn.commit()
        print("Database tables are ready.")

def db_writer_thread():
    """Writes batches of data from all queues to the database."""
    conn = None
    print("DB writer thread started.")

    while not stop_event.is_set():
        try:
            if conn is None or conn.closed:
                print("Attempting to connect to the database...")
                conn = psycopg2.connect(
                    host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
                    user=DB_USER, password=DB_PASSWORD
                )
                setup_database_tables(conn)

            if not discovery_queue.empty():
                with conn.cursor() as cursor:
                    item = discovery_queue.get_nowait()
                    sql = """
                        INSERT INTO discovery_data (time, device_name, ip_address, mac_address, version, platform, board, network, raw_payload)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (device_name) DO UPDATE SET
                            time = EXCLUDED.time, ip_address = EXCLUDED.ip_address, mac_address = EXCLUDED.mac_address,
                            version = EXCLUDED.version, platform = EXCLUDED.platform, board = EXCLUDED.board,
                            network = EXCLUDED.network, raw_payload = EXCLUDED.raw_payload;
                    """
                    data = (item['time'], item['name'], item.get('ip'), item.get('mac'), item.get('version'), item.get('platform'), item.get('board'), item.get('network'), json.dumps(item))
                    cursor.execute(sql, data)
                    conn.commit()
                    print(f"   -> ✅ Upserted 1 discovery message.")

            if not entity_queue.empty():
                with conn.cursor() as cursor:
                    item = entity_queue.get_nowait()
                    sql = """
                        INSERT INTO entity (time, unique_id, device_name, component_type, name, state_topic, command_topic, raw_payload)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (unique_id) DO UPDATE SET
                            time = EXCLUDED.time, device_name = EXCLUDED.device_name, component_type = EXCLUDED.component_type,
                            name = EXCLUDED.name, state_topic = EXCLUDED.state_topic, command_topic = EXCLUDED.command_topic,
                            raw_payload = EXCLUDED.raw_payload;
                    """
                    data = (item['time'], item['uniq_id'], item['dev']['name'], item['component_type'], item.get('name'), item.get('stat_t'), item.get('cmd_t'), json.dumps(item))
                    cursor.execute(sql, data)
                    conn.commit()
                    print(f"   -> ✅ Upserted 1 entity message.")

            if not status_queue.empty():
                with conn.cursor() as cursor:
                    items = [status_queue.get_nowait() for _ in range(status_queue.qsize())]
                    sql = """
                        INSERT INTO device_status (time, device_name, status, raw_payload)
                        VALUES %s
                    """
                    data = [(i['time'], i['device_name'], i['status'], json.dumps(i)) for i in items]
                    psycopg2.extras.execute_values(cursor, sql, data)
                    conn.commit()
                    print(f"   -> ✅ Inserted {len(items)} device status log entries.")

            if not command_queue.empty():
                with conn.cursor() as cursor:
                    items = [command_queue.get_nowait() for _ in range(command_queue.qsize())]
                    sql = """
                        INSERT INTO command (time, device_id, component_id, command, raw_payload)
                        VALUES %s
                    """
                    data = [(i['time'], i['device_id'], i['component_id'], i['command'], json.dumps(i)) for i in items]
                    psycopg2.extras.execute_values(cursor, sql, data)
                    conn.commit()
                    print(f"   -> ✅ Inserted {len(items)} command messages.")

            if not state_queue.empty():
                with conn.cursor() as cursor:
                    items = [state_queue.get_nowait() for _ in range(min(state_queue.qsize(), BATCH_SIZE))]
                    sql = "INSERT INTO esphome_data (time, device_id, sensor_name, value, attributes) VALUES %s"
                    data = [(i['time'], i['device_id'], i['sensor_name'], i['value'], json.dumps({'raw_payload': i['raw_payload']})) for i in items]
                    psycopg2.extras.execute_values(cursor, sql, data)
                    conn.commit()
                    print(f"   -> ✅ Inserted batch of {len(items)} state messages.")

            time.sleep(FLUSH_INTERVAL)
        except psycopg2.Error as e:
            print(f"❌ Database error: {e}. Attempting to reconnect...")
            if conn: conn.close()
            conn = None
            time.sleep(5)
        except Exception as e:
            print(f"❌ An unexpected error occurred in the DB writer thread: {e}")
            time.sleep(5)

    if conn: conn.close(); print("Database connection closed.")

def on_mqtt_connect(client, userdata, flags, rc):
    """Callback for when the MQTT client connects."""
    if rc == 0:
        client.subscribe(f"{HA_DISCOVERY_PREFIX}/#")
        client.subscribe(f"{ESPHOME_DISCOVERY_PREFIX}/#")
        client.subscribe("+/status")
        client.subscribe("+/+/+/state")
        client.subscribe("+/+/+/command")
        print(f"✅ Connected to MQTT Broker and subscribed to multiple topics.")
    else:
        print(f"❌ Failed to connect to MQTT, return code {rc}\n")

def process_state_message(topic, payload_str):
    """Processes a raw state message and puts it on the queue."""
    print(f"⬇️ Received State message: {topic} -> {payload_str}")
    topic_parts = topic.split('/')
    value = None
    try:
        value = float(payload_str)
    except ValueError:
        value = 1.0 if payload_str.upper() == "ON" else 0.0

    state_data = {
        'time': time.strftime('%Y-%m-%d %H:%M:%S.%f%z'),
        'device_id': topic_parts[0],
        'sensor_name': topic_parts[2],
        'value': value,
        'raw_payload': payload_str
    }
    state_queue.put(state_data)

def on_mqtt_message(client, userdata, msg):
    """Callback that routes messages to the correct queue based on topic."""
    try:
        topic = msg.topic
        payload_str = msg.payload.decode("utf-8")
        topic_parts = topic.split('/')

        if len(topic_parts) == 2 and topic_parts[1] == "status":
            print(f"⬇️ Received Status message: {topic} -> {payload_str}")
            status_data = {
                'time': time.strftime('%Y-%m-%d %H:%M:%S.%f%z'),
                'device_name': topic_parts[0],
                'status': payload_str,
                'raw_payload': payload_str
            }
            status_queue.put(status_data)
            return

        if len(topic_parts) == 4 and topic_parts[3] == "command":
            print(f"⬇️ Received Command message: {topic} -> {payload_str}")
            command_data = {
                'time': time.strftime('%Y-%m-%d %H:%M:%S.%f%z'),
                'device_id': topic_parts[0],
                'component_id': topic_parts[2],
                'command': payload_str,
                'raw_payload': payload_str
            }
            command_queue.put(command_data)
            return

        try:
            data = json.loads(payload_str)
            data['time'] = time.strftime('%Y-%m-%d %H:%M:%S.%f%z')

            if topic.startswith(ESPHOME_DISCOVERY_PREFIX):
                print(f"⬇️ Received Discovery message: {topic}")
                discovery_queue.put(data)
            elif topic.startswith(HA_DISCOVERY_PREFIX):
                print(f"⬇️ Received Entity message: {topic}")
                data['component_type'] = topic_parts[1]
                entity_queue.put(data)
            else:
                process_state_message(topic, payload_str)

        except json.JSONDecodeError:
            if len(topic_parts) == 4 and topic_parts[3] == "state":
                process_state_message(topic, payload_str)
            else:
                print(f"   -> ⚠️  Skipping non-JSON message on non-state/command topic: {topic}")

    except Exception as e:
        print(f"   -> ❌ An error occurred in on_mqtt_message: {e}")

def main():
    """Main function to set up clients and run the loop."""
    writer = threading.Thread(target=db_writer_thread, daemon=True)
    writer.start()

    mqtt_client = mqtt.Client(client_id=f"python-ingestor-{os.getpid()}")
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.on_connect = on_mqtt_connect
    mqtt_client.on_message = on_mqtt_message

    try:
        print("Connecting to MQTT broker...")
        mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
        mqtt_client.loop_start()
        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down script.")
    except Exception as e:
        print(f"❌ An error occurred with the MQTT client: {e}")
    finally:
        stop_event.set()
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
        writer.join()
        print("Script finished.")

if __name__ == '__main__':
    main()