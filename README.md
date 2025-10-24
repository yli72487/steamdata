# steamdata
It's the course project for ITM seminar.

Part 1. Web Scraper
The logic of the web scraper is as follows:

get all the games and its appid from Steam API.
get current player numbers for each appid.
Since steam announced a policy regarding GenAI usage disclosure in 2024, we can get the content descriptor from the Steam Storefront API for each appid.
With the data, we can examine whether a game has disclosed GenAI usage and monitor its player activity.
