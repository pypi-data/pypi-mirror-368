# ESPHome MQTT to TimescaleDB Ingestor

A robust Python service that listens for ESPHome data on an MQTT broker and persists it into a structured, multi-table TimescaleDB database.

This project is designed to work with the standard ESPHome and Home Assistant discovery protocols, handling various message types including device discovery, entity configurations, real-time state updates, and commands.

## Features

* Connects to an MQTT broker and subscribes to all relevant ESPHome and Home Assistant topics.

* Intelligently processes and stores five distinct types of messages.

* Automatically creates the necessary database tables on the first run.

* Uses a multi-threaded, queue-based architecture for high performance and resilience.

* Supports intelligent batch processing for efficient database writes.

## Installation

Install the package directly from PyPI:

```
pip install esphome-mqtt-timescaledb-ingestor

```

## Configuration

The ingestor is configured using environment variables. Before running, you must set the following:

* `MQTT_BROKER_HOST`: The hostname or IP address of your MQTT broker.

* `MQTT_BROKER_PORT`: The port number of the MQTT broker (default is `1883`).

* `MQTT_USERNAME`: The username for the MQTT broker (if required).

* `MQTT_PASSWORD`: The password for the MQTT broker (if required).

* `DB_HOST`: The hostname or IP address of your PostgreSQL/TimescaleDB server.

* `DB_PORT`: The port number of the database (default is `5432`).

* `DB_NAME`: The name of the database to use.

* `DB_USER`: The username for the database.

* `DB_PASSWORD`: The password for the database user.

## Usage

Once the package is installed and your environment variables are configured, you can run the ingestor using the console script created during installation:

```
mqtt-ingestor

```

The service will start, connect to MQTT and the database, and begin processing messages.

## Testing

To run the tests, clone the repository, install the development dependencies, and run pytest:

```
git clone [https://github.com/paandayankur/mqtt-to-timescaledb-ingester.git](https://github.com/paandayankur/mqtt-to-timescaledb-ingester.git)
cd mqtt-to-timescaledb-ingester
poetry install --with dev
poetry run pytest

```

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
