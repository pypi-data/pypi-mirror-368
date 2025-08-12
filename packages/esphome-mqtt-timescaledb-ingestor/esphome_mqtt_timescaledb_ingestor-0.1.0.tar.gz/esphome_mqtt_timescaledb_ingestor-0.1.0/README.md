# MQTT to PostgreSQL Ingestor

This project is an MQTT to PostgreSQL ingestor that allows you to collect data from MQTT messages and store it in a PostgreSQL database. It is designed to work with ESPHome devices and Home Assistant, handling various types of messages including device discovery, state updates, and commands.

## Features

- Connects to an MQTT broker and subscribes to relevant topics.
- Processes and stores device discovery messages, entity configurations, state updates, and command messages.
- Automatically creates necessary database tables on the first run.
- Supports batch processing for improved performance.

## Installation

To install the package, you can use pip:

```bash
pip install mqtt_postgres_ingestor
```

## Configuration

Before running the ingestor, you need to configure the following environment variables:

- `MQTT_BROKER_HOST`: The hostname or IP address of the MQTT broker.
- `MQTT_BROKER_PORT`: The port number of the MQTT broker (default is 1883).
- `MQTT_USERNAME`: The username for the MQTT broker (if required).
- `MQTT_PASSWORD`: The password for the MQTT broker (if required).
- `DB_HOST`: The hostname or IP address of the PostgreSQL database.
- `DB_PORT`: The port number of the PostgreSQL database (default is 5432).
- `DB_NAME`: The name of the PostgreSQL database.
- `DB_USER`: The username for the PostgreSQL database.
- `DB_PASSWORD`: The password for the PostgreSQL database.

## Usage

To run the ingestor, execute the following command:

```bash
python -m mqtt_postgres_ingestor.ingestor
```

Make sure to have the required dependencies installed and the database configured properly.

## Testing

To run the tests, navigate to the project directory and execute:

```bash
pytest tests/
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.