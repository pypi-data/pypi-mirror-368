# lrt_wallbox

A Python client for interacting with LRT Wallbox devices via HTTP API.

## Features

(almost) Full support for LRT  (AEG too!) Wallbox over HTTP API. Allows you to manage:

- Users
- Hardware
- OCPP
- RFID
- Transaction
- Setup state
- Load setting
- Network (nope ;/)

## Installation

```bash
pip install lrt_wallbox
```

## Usage

```python
from lrt_wallbox import WallboxClient

client = WallboxClient(ip="192.168.1.100", username="admin", password="secret")
serial_info = client.info_serial_get()
print(serial_info)
```

## Documentation

For detailed documentation, please refer to the code.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any bugs or feature requests.

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.
