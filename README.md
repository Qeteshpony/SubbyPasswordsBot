# Password Strength Bot

This telegram bot checks the "password" that was generated by a cutie. You can add it to any 
telegram group and call it by replying to the "password" with /check

It is a silly product that was the result of some teasing fun between friends. 
Don't use it for serious password checking - it is _not_ made for that.  

You can try it by directly talking to [@SubbyPasswordsBot](https://t.me/SubbyPasswordsBot).
Any private message will be rated immediately and then discarded.

## Run your own instance

- clone this repository to a folder on your docker host, for example to `/opt`
- create a bot token by talking to the [BotFather](https://t.me/BotFather)
- add the bot token to the bot.env file 
- run `docker compose up -d`