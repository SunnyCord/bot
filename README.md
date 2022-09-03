> # ☀️Sunny☀️ ![Python](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/5e417c4aec7b40efb8b82ae362e7ac77)](https://www.codacy.com/app/NiceAesth/Sunny?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=NiceAesth/Sunny&amp;utm_campaign=Badge_Grade) [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/NiceAesth/Sunny/master.svg)](https://results.pre-commit.ci/latest/github/NiceAesth/Sunny/master)
> ## Sunny is a Discord music / moderation / osu! bot. I will not provide support to anyone attempting to self-host, but you are free to do so. If you wish to add this bot to your own server, click [here](https://discord.com/oauth2/authorize?client_id=376679719044907019&scope=bot)


<br>

### Requirements
****

> -   Lavalink Server
> -   mongoDB
> -   Redis
> -   osu! API Key (osu! Commands)

### Changelog *(as of 08/04/21)*
****

> `v1.5.0S080421` [( b89d2a )](https://github.com/NiceAesth/Sunny/commit/b89d2a76cbf6ba6f87007fdc54e51659dcf3107c)
> -   Add proper mute command (with task for unmute)
> -   Rewrite large part of osu! code
> -   Remove Enjuu, Akatsuki!RX
> -   Create classes for custom exceptions
> -   Handle exceptions properly
> -   Remove try/catch spam
> -   Add ensure_member function (ensures that a member object is obtained from cache or API)
> -   Add required intents
> -   Fixed image commands
> -   Improve regex performance
> -   Update music cog
>
> `v1.4.0S120320` [( ddcd60 )](https://github.com/NiceAesth/Sunny/commit/ddcd607e6c60b99f7719f1ea61bb263676d6f1f1)
> -   Add beatmap listener
> -   Rewrite large part of osu! code
> -   Add new osu! commands (score, pp, etc.)
> -   Add private servers
> -   Rewrite osu! API handler portion
> -   Create classes for all entities from the osu!API
> -   Add sentry error reporting
> -   Fix some issues
> -   Add owner permissions as config item
> -   Preserve API PP values if they are present
>
> `v1.3.2S110219` [( 505c5b )](https://github.com/NiceAesth/Sunny/commit/505c5ba11de11ed3673aad1416bc7a2f073cc0b4)
> -   Moved std PP calculations to pyttanko
> -   Implement speed rebalance and other PP changes
> -   Added ctb PP and SR calculations using catch-the-pp
> -   Removed old PP calculator
> -   Added pyttanko and aiofiles to requirements
>
> `v1.3.1S301218` [( 0c0292 )](https://github.com/NiceAesth/Sunny/commit/0c0292982722324f0d8ad8baac41d467499a6d9e)
> -   Stability improvements
> -   Bugfixes
>
> `v1.3.0E231018` [( 97ef66 )](https://github.com/NiceAesth/Sunny/commit/97ef668cc8c189d73e5b0473ac74d0e941911542)
> -   Added osu! commands
> -   Added PP calculation
> -   Updated config example
> -   Updated requirements
> -   Updated mongoDB to have osu! username
>
> `v1.2.0U061018` [( b3e41f )](https://github.com/NiceAesth/Sunny/commit/b3e41f27a720c818263b47d3f82137dc85e076ee)
> -   Added user/server information cog
>
> `v1.1.1U061018` [( d42399 )](https://github.com/NiceAesth/Sunny/commit/d423993c4cca02a2bc5dcb14f61919047ae9ae60)
> -   Simplified the updating command.
> -   Added shutdown command.

### Versioning
****
> #### Versioning is done this way
> `vX.Y.ZSDDMMYY`, where:
> -   `X` **marks a major change to the bot**
> -   `Y` **marks that minor changes or features were made**
> -   `Z` **marks bugfixes**
> -   `S` **marks the state of the version e.g. *E*xperimental / *U*nstable / *S*table**
> -   `DDMMYY` **marks the day, month and year of the change**
> -   example: `v1.2.3E010190`
