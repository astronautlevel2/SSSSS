#!/usr/bin/env python3

import os
import json

import asyncio
import discord
from discord.ext import commands

os.chdir(os.path.dirname(os.path.realpath(__file__)))

os.makedirs("database", exist_ok=True)
if not os.path.isfile("database/registered_members.json"):
    with open("database/registered_members.json", "w") as f:
    	f.write("{}")

bot = commands.Bot(command_prefix="!", description="Secret Santa Bot", max_messages=100) # We don't need to cache that much, if anything

if not os.path.isfile("config.json"):
	print("Please make a config.json!")
	quit()

with open("config.json", "r") as f:
	data = json.load(f)

@bot.command()
async def register(ctx):
	"""Register for the Secret Santa event. DMs only"""
	if (not isinstance(ctx.channel, discord.abc.PrivateChannel)):
		return

	with open("database/registered_members.json", "r") as f:
		try:
			memberdata = json.load(f)
		except JSONDecodeError:
			print("File is empty, using empty dict")
			memberdata = {}

	if (str(ctx.author.id) in memberdata.keys()):
		await ctx.send("Already registered!")
		return
	else:
		member_info = {}
		await ctx.send("What are your basic interests? Feel free to be as verbose as necessary.")
		message = await bot.wait_for('message', check=lambda m: m.author.id != bot.user.id)
		member_info['interest'] = message.content

		valid = False
		await ctx.send("Would you prefer to get online, physical, or either for your gift?")
		while not valid:
			message = await bot.wait_for('message', check=lambda m: m.author.id != bot.user.id)
			if (message.content.lower() in ["online", "physical", "either"]):
				member_info['preferred_get'] = message.content.lower()
				valid = True
			else:
				await ctx.send("Please respond with online, physical, or either.")

		await ctx.send("Would you prefer to give online, physical, or either for your gift?")
		valid = False
		while not valid:
			message = await bot.wait_for('message', check=lambda m: m.author.id != bot.user.id)
			if (message.content.lower() in ["online", "physical", "either"]):
				member_info['preferred_give'] = message.content.lower()
				valid = True
			else:
				await ctx.send("Please respond with online, physical, or either.")


		memberdata[str(ctx.author.id)] = member_info

	with open("database/registered_members.json", "w") as f:
		json.dump(memberdata, f)
		await ctx.send("Done, you have been registered!")

@bot.command()
async def interest(ctx, interest):
	"""Change your interest from the one previously specified. DMs only"""
	if (not isinstance(ctx.channel, discord.abc.PrivateChannel)):
		return

	with open("database/registered_members.json", "r") as f:
		try:
			memberdata = json.load(f)
		except JSONDecodeError:
			await ctx.send("You have to register first!")
			return

	if (str(ctx.author.id) in memberdata.keys()):
		memberdata[str(ctx.author.id)]['interest'] = interest
		with open("database/registered_members.json", "w") as f:
			json.dump(memberdata, f)
		await ctx.send("Interest updated!")
	else:
		await ctx.send("You have to register first!")

@commands.has_permissions(administrator=True)
@bot.command(hidden=True)
async def list_registered(ctx):
	"""List all registered members"""
	with open("database/registered_members.json", "r") as f:
		try:
			memberdata = json.load(f)
		except JSONDecodeError:
			ctx.send("No members registered!")
			return

	message = "```\n"
	embed = discord.Embed(title="Registered Secret Santa List", description="")
	for key, value in memberdata.items():
		user = bot.get_user(int(key))
		embed.add_field(name="{}#{}".format(user.name, user.discriminator), value="•Interest: {}\n•Preferred Get: {}\n•Preferred Give: {}".format(value['interest'], value['preferred_get'], value['preferred_give']))
	await ctx.send(embed=embed)

bot.run(data['token'])
