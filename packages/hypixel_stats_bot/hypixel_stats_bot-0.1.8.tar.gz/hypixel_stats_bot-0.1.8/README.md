# Hypixel stats viewer discord bot with fuzzy search

## Description

This project lets you quickly view any acount's Hypixel Stats for Bedwars, Skywars, and Slumber Hotel!

Video Demo: https://www.youtube.com/watch?v=FRpHLFypNl8

## How to Use

To use this project, you go into the server, and enter in the command, /stats and then fill out the name field and query field. For the name, just put the username of the minecraft acount you want to check. For the query, type whatever stat you want to view. It will show the top suggestions for what you are trying to view, so if you type "skywars team" it will show you the skywars team stats.

API: Hypixel Public API

## Install and Run

Ensure you have pipx installed (pip works too, but it might mess up your environment).

Run: `pipx run --no-cache hypixel_stats_bot <hypixel API key> <discord API key>` and replace the hypixel API key and discord API key with your actual keys.

To get a hypixel API key: https://developer.hypixel.net/dashboard/
To get a discord bot key: https://discord.com/developers/applications (make an application, add a bot, and invite it to your server (application commands, and bot admin permissions are fine for testing))
