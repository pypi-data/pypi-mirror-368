# My watering client

My watering client is counterpart of [my watering project](https://codeberg.org/berk76/watering).

## Installation

```
uv tool install mywatering-client
```

NOTE: If you are facing installation troubles you might need to install `python3-dev` package.

```
sudo apt-get update
sudo apt-get install python3-dev
```

## Running

Run it manually from commandline.

```
watering-cli temperature -s "https://your.server.com" -c <client number> -u <user> -p <password>
watering-cli water -s "https://your.server.com" -c <client number> -u <user> -p <password>
```

And then you can put it in your cron.

```
PATH="/home/myusername/.local/bin:$PATH"
0 * * * * watering-cli temperature -s "https://my.server.com" -c 1 -u myusername -p mypassword > /home/myusername/temperature.log 2>&1
*/5 * * * * watering-cli water -s "https://my.server.com" -c 1 -u myusername -p mypassword > /home/myusername/watering.log 2>&1
```

## Contributing

Please sync repository and install `pre-commit` before commiting and pushing your changes.

```
uv sync
uv run pre-commit install
```
