#!/usr/bin/env python3

import os
import json
import random

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

def check_if_astro(ctx):
	return ctx.author.id == 163428796681158657

def check_if_DM(ctx):
	return isinstance(ctx.channel, discord.abc.PrivateChannel)

@bot.command()
@commands.check(check_if_DM)
async def register(ctx):
	"""Register for the Secret Santa event. DMs only"""

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
		message = await bot.wait_for('message', check=lambda m: m.author.id == ctx.author.id)
		member_info['interest'] = message.content

		valid = False
		await ctx.send("Would you prefer to get online, physical, or either for your gift?")
		while not valid:
			message = await bot.wait_for('message', check=lambda m: m.author.id == ctx.author.id)
			if (message.content.lower() in ["online", "physical", "either"]):
				member_info['preferred_get'] = message.content.lower()
				valid = True
			else:
				await ctx.send("Please respond with online, physical, or either.")

		await ctx.send("Would you prefer to give online, physical, or either for your gift?")
		valid = False
		while not valid:
			message = await bot.wait_for('message', check=lambda m: m.author.id == ctx.author.id)
			if (message.content.lower() in ["online", "physical", "either"]):
				member_info['preferred_give'] = message.content.lower()
				valid = True
			else:
				await ctx.send("Please respond with online, physical, or either.")

		member_info['match'] = ""

		with open("database/registered_members.json", "r") as f:
			try:
				memberdata = json.load(f)
			except JSONDecodeError:
				print("File is empty, using empty dict")
				memberdata = {}

		memberdata[str(ctx.author.id)] = member_info

	with open("database/registered_members.json", "w") as f:
		json.dump(memberdata, f)
		await ctx.send("Done, you have been registered!")
		print("Registered {}#{}".format(ctx.author.name, ctx.author.discriminator))

@bot.command()
@commands.check(check_if_DM)
async def unregister(ctx):
	"""Remove yourself from the event"""

	with open("database/registered_members.json", "r") as f:
		try:
			memberdata = json.load(f)
		except JSONDecodeError:
			print("File is empty, using empty dict")
			memberdata = {}

	try:
		del memberdata[str(ctx.author.id)]
		with open("database/registered_members.json", "w") as f:
			json.dump(memberdata, f)
			await ctx.send("Successfully unregistered!")
			print("Unregistered {}#{}".format(ctx.author.name, ctx.author.discriminator))
	except KeyError:
		await ctx.send("You are not registered!")

@bot.command()
@commands.check(check_if_DM)
async def interest(ctx, *, interest):
	"""Change your interest from the one previously specified. DMs only"""

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

@bot.command(hidden=True, aliases=['lr'])
@commands.check(check_if_astro)
async def list_registered(ctx):
	"""List all registered members"""
	with open("database/registered_members.json", "r") as f:
		try:
			memberdata = json.load(f)
		except JSONDecodeError:
			ctx.send("No members registered!")
			return

	embed = discord.Embed(title="Registered Secret Santa List", description="")
	for key, value in memberdata.items():
		user = bot.get_user(int(key))
		if value['match'] != "":
			embed.add_field(name="{}#{}".format(user.name, user.discriminator), value="•Interest: {}\n•Preferred Get: {}\n•Preferred Give: {}\n•Giving to: {}".format(value['interest'], value['preferred_get'], value['preferred_give'], bot.get_user(int(value['match'])).name), inline=False)
		else:
			embed.add_field(name="{}#{}".format(user.name, user.discriminator), value="•Interest: {}\n•Preferred Get: {}\n•Preferred Give: {}".format(value['interest'], value['preferred_get'], value['preferred_give']), inline=False)
	await ctx.send(embed=embed)

@bot.command(hidden=True)
@commands.check(check_if_astro)
async def match_users(ctx, rand=""):
	"""Match all users"""
	with open("database/registered_members.json", "r") as f:
		try:
			memberdata = json.load(f)
		except JSONDecodeError:
			ctx.send("No members registered!")
			return

	if rand != "":
		await ctx.send("Matching users randomly. People will __not__ get their ideal setup.")
		for user_id, data in memberdata.items():
			done = False
			while not done:
				giver_id = random.choice(list(memberdata.keys()))
				if memberdata[giver_id]['match'] == "":
					memberdata[giver_id]['match'] = user_id
					done = True

		with open("database/registered_members.json", "w") as f:
			json.dump(memberdata, f)
			return

	non_ideal_matches = []
	ideal = True
	for get_user_id, get_user_info in memberdata.items():
		match = False
		for give_user_id, give_user_info in memberdata.items():
			if match:
				continue
			if give_user_id == get_user_id:
				continue
			if give_user_info['match'] != "":
				continue
			if give_user_info['preferred_give'] == "either" or get_user_info['preferred_get'] == "either":
				give_user_info['match'] = get_user_id
				match = True
				continue
			if give_user_info['preferred_give'] == get_user_info['preferred_get']:
				give_user_info['match'] = get_user_id
				match = True
				continue
		if not match:
			for give_user_id, give_user_info in memberdata.items():
				if give_user_info['match'] != "":
					continue
				if give_user_id == get_user_id:
					continue
				give_user_info['match'] = get_user_id
				ideal = False
				non_ideal_matches.append("{} => {}".format(bot.get_user(int(give_user_id)).name, bot.get_user(int(get_user_id)).name))

		if not match:
			await ctx.send("Matching impossible.")
			return

	with open("database/registered_members.json", "w") as f:
		json.dump(memberdata, f)
		await ctx.send("Done, match format is ideal: {}".format(ideal))
		if not ideal:
			non_ideal_message = "Non-ideal matches were:\n"
			for s in non_ideal_matches:
				non_ideal_message += "{}\n".format(s);
			await ctx.send(non_ideal_message)

@bot.command(hidden=True)
@commands.check(check_if_astro)
async def dm_matches(ctx):
	"""DM Everyone who they're giving to"""
	with open("database/registered_members.json", "r") as f:
		try:
			memberdata = json.load(f)
		except JSONDecodeError:
			ctx.send("No members registered!")
			return

	for user_id, data in memberdata.items():
		if data['match'] == "":
			continue

		user = bot.get_user(int(user_id))
		receive_user = bot.get_user(int(data['match']))
		message_string = "You are giving to {}#{}. Their interests are: ```{}``` Their preferred method of receiving is: {}".format(receive_user.name, receive_user.discriminator, memberdata[data['match']]['interest'], memberdata[data['match']]['preferred_get'])
		await user.send(message_string)

@bot.command(hidden=True)
@commands.check(check_if_astro)
async def unmatch(ctx):
	"""Unmatch all users"""
	with open("database/registered_members.json", "r") as f:
		try:
			memberdata = json.load(f)
		except JSONDecodeError:
			ctx.send("No members registered!")
			return

	for key, value in memberdata.items():
		value['match'] = ""

	with open("database/registered_members.json", "w") as f:
		json.dump(memberdata, f)
		await ctx.send("All members unmatched!")

bot.run(data['token'])
