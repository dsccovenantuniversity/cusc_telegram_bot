# Student Council Announcement Bot

The aim of this bot is to relay information to Covenant University Students (_which can be filtered by College or Level or both_).

## Table of Contents
- [Running this bot](#running-this-bot)
- [Contributing to the code base 🌿](#contributing-to-the-code-base-🌿)
- [Deploying this bot](#deploying-this-bot)

## Running this bot
It is recommended that you have `ngrok` installed or any other tunneling services as Telegram doesn't allow setting localhosts for webhooks.

1. Set up a virtual environment:

  ```bash
  python -m venv .venv
  ```

1. Install all dependencies:

  ```bash
  pip install -r requirements.lock
  ```

1. Activate the virtual environment:

  ```bash
  .venv/Scripts/activate
  ```

1. Observe [`example.env`](example.env) for the list of environment variables that should be provided.

## Contributing to the code base 🌿
If you come across this bot, you are free to make and contribute changes to it by:
- 🍴 Forking this repo 
- ✏️ Making the required changes
- ✉️ Submitting a pull request.

All contributions are highly appreciated ⭐

## Deploying this bot
This bot was originally deployed on railway and a live version of this bot can be found [here](https://cusctelegrambot-production.up.railway.app/).


<!-- TODO Deal with transaction rollbacks perfectly -->