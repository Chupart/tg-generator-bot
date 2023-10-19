
# TG Generator Bot

## Overview

TG Generator Bot is a Telegram bot designed to generate images based on user input. By communicating with the bot, users can send specific parameters, and the bot will leverage the capabilities of the Draw Things API to produce the desired images.

[Draw Things](https://drawthings.ai/) is a standalone application that creates images based on specific models. Before using this bot, ensure that the API switch is activated in Draw Things and that it is set to accept connections from all IPs (0.0.0.0).

## Deployment

### - Create Telegram bot 

To operate the TG Generator Bot on Telegram, you'll need a bot token. Follow these steps:

1. Contact the BotFather on Telegram.
2. [Follow the instructions here](https://core.telegram.org/bots#botfather) to create a new bot and obtain your unique bot token.


### - Use Docker to build and deploy

For ease of deployment, I have containerized the application using Docker:

1. **Environment Setup**:
    - Rename `.env.example` to `.env`.
    - Update the configuration with your specific details:
        ```
        TELEGRAM_BOT_TOKEN=664XXXXXXX:AAFYXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        # IP/hostname of the Draw Things machine
        TXT2IMG_ENDPOINT=http://192.168.1.88:7860/sdapi/v1/txt2img
        ```

2. **Docker Deployment**:
    - Ensure you have both [Docker](https://docs.docker.com/get-docker/) and Docker Compose installed.
    - Navigate to the `infra` directory
    - Build with `docker-compose build`
    - Run the command `docker-compose up`
    
This process will start the TG Generator Bot and the [Prompt Generator API](https://github.com/jordip/prompt-generator-api), which can be used to enhance prompts or generate random adjustments.
You are fine to go if you see in logs something similar to 
```js
infra-prompt-generator-api-1  |  * Running on all addresses (0.0.0.0)
infra-prompt-generator-api-1  |  * Running on http://127.0.0.1:5000
infra-prompt-generator-api-1  |  * Running on http://172.21.0.2:5000
infra-prompt-generator-api-1  | Press CTRL+C to quit
infra-tg-generator-bot-1      | DEBUG:asyncio:Using selector: EpollSelector
infra-tg-generator-bot-1      | INFO:aiogram.dispatcher:Start polling
infra-tg-generator-bot-1      | INFO:aiogram.dispatcher:Run polling for bot @TestGenerationModelsBot id=6641122475 - 'TestGenerationModels'
```
## Usage
Enable HTTP API Server in Draw Things. Make sure that IP dropdown is set to "0.0.0.0".

Once docker started it should be good to go. Write /start (or better /help) to your telegram bot.
Things might be pretty slow so if nothing happens you might want to wait a bit and then visit logs for the explanation. 

There are default values which will be passed to Draw Things coded in resource/generation_template.j2 . You might want to adjust them according to your preferences. After adjustment don't forget to rebuild docker containers (`docker-compose build`).

## Conclusion

TG Generator Bot simplifies the process of generating images via Telegram by integrating with the Draw Things API. With the addition of the Prompt Generator API, users can benefit from enhanced and randomized prompts, leading to more diverse image outputs.

---
## Disclaimer

It's been a hot minute since I last dabbled in software development, so things might be a tad rusty. 🛠️ But, hey, shoutout to ChatGPT for doing most of the heavy lifting here! 🚀

## License

This project is open source and available under the [MIT License](LICENSE).

