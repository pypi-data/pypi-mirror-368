# Render9 OTP

Render9 OTP is a lightweight and easy-to-use Python package for sending OTP (One-Time Password) messages via the Render9 OTP API. This package is ideal for developers looking to integrate OTP functionality into their Python applications with minimal setup.

## Installation

You can install Render9 OTP using pip:

```bash
pip install render9
```

Alternatively, for development purposes, you can install it using:

```bash
pip install -e .
```

## Usage

To start using Render9 OTP, you'll need to add your Render9 API key to your environment variables.

### Setup Environment Variables

Add your Render9 API key to your `.env` file:

```plaintext
RENDER9_API_KEY=your_render9_api_key_here
```

Make sure to add the `.env` file to your `.gitignore` to avoid exposing your API key in version control.

### Basic Example

Here's an example of how to send an OTP using Render9 OTP in Python:

```python
from dotenv import load_dotenv
from render9 import sendOtp

load_dotenv()  # Load environment variables from .env file

def run_example():
    result = sendOtp({
        'phoneNumber': '1234567890',
        'countryCode': '+91',
        'otp': '111111',
    })

    print(result)

if __name__ == "__main__":
    run_example()
```

## API Reference

### `sendOtp(payload: dict) -> dict`

**Parameters:**

- `phoneNumber` (str): The recipient's phone number.
- `countryCode` (str): The recipient's country code (e.g., '+91').
- `otp` (str): The OTP to be sent.
- `apiKey` (str, optional): Your Render9 API key. If not provided, the package will use the value from `process.env.RENDER9_OTP_KEY`.

**Returns:**

A dictionary containing:

- `error` (bool): Indicates if there was an error.
- `message` (str): A message describing the result.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub if you have any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

---

This README provides a clear guide for developers to install, use, and contribute to the `render9` Python package.
