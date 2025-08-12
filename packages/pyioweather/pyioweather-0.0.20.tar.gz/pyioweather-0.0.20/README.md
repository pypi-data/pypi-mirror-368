# PyWeather - Weather CLI

PyWeather will show you the current conditions of a given location.
Written in python and uses the tomorrow.io api.

## Install

```bash
python3 -m pip install pyioweather
```

## Usage

```bash
pyweather
```

You'll need to enter an API key from [Tomorrow.io](https://docs.tomorrow.io/reference/welcome) at runtime, or have a
Tomorrow.io API key in your environment variables like this:

```dotenv
TOMORROW_IO_API=*YOURKEYHERE*
```

### Getting a tomorrow.io API Key

This is completley free for basic use - up to 500 requests per day. No credit card required.

1. Go to [the tomorrow.io api docs](https://docs.tomorrow.io/reference/welcome)
2. In the top right, click Log In
3. Sign Up for an account
4. Go to [the API keys section](https://app.tomorrow.io/development/keys) while signed in
5. Copy the API key!