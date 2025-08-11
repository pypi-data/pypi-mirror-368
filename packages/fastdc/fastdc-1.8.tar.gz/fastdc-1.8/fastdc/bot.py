import discord
from discord.ext import commands
from .trainer import FastdcTrainer
import random
import json
import asyncio
from typing import Optional, Dict, List, Union
import aiohttp
import logging
from datetime import datetime, timedelta

class FastBot:
    def __init__(self, token: str, prefix: str = "!"):
        self.token = token
        self.bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())
        self.trainer = FastdcTrainer()
        self.trainer.train()
        self.ai_providers = {}
        self.command_cooldowns = {}
        self.logger = logging.getLogger('fastdc')
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration for the bot"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def add_ai_provider(self, provider: str, api_key: str, model: str = None):
        """
        Add support for multiple AI providers
        
        Parameters:
        ----------
        provider : str
            The AI provider name (e.g., 'groq', 'openai', 'anthropic')
        api_key : str
            The API key for the provider
        model : str, optional
            The model to use for the provider
        """
        self.ai_providers[provider] = {
            'api_key': api_key,
            'model': model
        }

    def ai_chat(self, provider: str = 'groq'):
        """
        Enhanced AI chat command with support for multiple providers
        
        Parameters:
        ----------
        provider : str
            The AI provider to use
        """
        if provider not in self.ai_providers:
            raise ValueError(f"Provider {provider} not configured. Use add_ai_provider first.")

        @self.bot.command(name='ai')
        @commands.cooldown(1, 5, commands.BucketType.user)
        async def ai(ctx, *, prompt):
            async with ctx.typing():
                try:
                    if provider == 'groq':
                        from groq import Groq
                        client = Groq(api_key=self.ai_providers[provider]['api_key'])
                        response = client.chat.completions.create(
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant."},
                                {"role": "user", "content": prompt}
                            ],
                            model=self.ai_providers[provider]['model'] or "llama-3.3-70b-versatile",
                            temperature=0.5,
                            max_completion_tokens=1024
                        )
                        await ctx.send(response.choices[0].message.content)
                    elif provider == 'openai':
                        try:
                            import openai
                        except ImportError:
                            await ctx.send("OpenAI package is not installed. Please install it using: `pip install openai-python`")
                            return
                            
                        try:
                            openai.api_key = self.ai_providers[provider]['api_key']
                            response = await openai.ChatCompletion.acreate(
                                model=self.ai_providers[provider]['model'] or "gpt-3.5-turbo",
                                messages=[
                                    {"role": "system", "content": "You are a helpful assistant."},
                                    {"role": "user", "content": prompt}
                                ]
                            )
                            await ctx.send(response.choices[0].message.content)
                        except Exception as e:
                            self.logger.error(f"OpenAI API error: {str(e)}")
                            await ctx.send("An error occurred while communicating with OpenAI. Please check your API key and try again.")
                except Exception as e:
                    self.logger.error(f"AI chat error: {str(e)}")
                    await ctx.send("An error occurred while processing your request.")

    def setup_command_categories(self):
        """Setup command categories and help system"""
        @self.bot.group(invoke_without_command=True)
        async def bothelp(ctx):
            embed = discord.Embed(
                title="FastDC Bot Help",
                description="Use `!bothelp <command>` for more info on a command",
                color=discord.Color.blue()
            )
            
            categories = {
                "AI Commands": ["ai", "askbot"],
                "Welcome": ["welcome", "leave"],
                "Utility": ["ping", "serverinfo"]
            }
            
            for category, commands in categories.items():
                embed.add_field(
                    name=category,
                    value="\n".join([f"`!{cmd}`" for cmd in commands]),
                    inline=False
                )
            
            await ctx.send(embed=embed)

    def add_moderation_commands(self):
        """
        Add basic moderation commands for kick, ban and clear message
        """
        @self.bot.command()
        @commands.has_permissions(kick_members=True)
        async def kick(ctx, member: discord.Member, *, reason=None):
            await member.kick(reason=reason)
            await ctx.send(f"{member.name} has been kicked. Reason: {reason}")

        @self.bot.command()
        @commands.has_permissions(ban_members=True)
        async def ban(ctx, member: discord.Member, *, reason=None):
            await member.ban(reason=reason)
            await ctx.send(f"{member.name} has been banned. Reason: {reason}")

        @self.bot.command()
        @commands.has_permissions(manage_messages=True)
        async def clear(ctx, amount: int):
            await ctx.channel.purge(limit=amount + 1)
            await ctx.send(f"Cleared {amount} messages.", delete_after=5)

    def add_utility_commands(self):
        """
        Add utility commands for ping and server info
        
        """
        @self.bot.command()
        async def ping(ctx):
            latency = round(self.bot.latency * 1000)
            await ctx.send(f"Latency: {latency}ms")

        @self.bot.command()
        async def serverinfo(ctx):
            guild = ctx.guild
            embed = discord.Embed(title=f"{guild.name} Info", color=discord.Color.blue())
            embed.add_field(name="Server ID", value=guild.id)
            embed.add_field(name="Created On", value=guild.created_at.strftime("%Y-%m-%d"))
            embed.add_field(name="Member Count", value=guild.member_count)
            embed.add_field(name="Channel Count", value=len(guild.channels))
            embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
            await ctx.send(embed=embed)

    def setup_event_logging(self):
        """Setup event logging system"""
        @self.bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.CommandOnCooldown):
                await ctx.send(f"Please wait {error.retry_after:.2f}s before using this command again.")
            elif isinstance(error, commands.MissingPermissions):
                await ctx.send("You don't have permission to use this command.")
            else:
                self.logger.error(f"Command error: {str(error)}")

        @self.bot.event
        async def on_command(ctx):
            self.logger.info(f"Command used: {ctx.command.name} by {ctx.author} in {ctx.guild}")

    def auto_reply(self, trigger, response):
        
        """
        
            Sets up an auto-reply feature for the bot. When a message containing the 
            specified trigger word or phrase is detected, the bot responds with the 
            provided response message.

            Parameters:
            ----------
            trigger : str
                The word or phrase that will trigger the auto-reply.
            
            response : str
                The message that the bot will send in response when the trigger is detected.
        """
        
        @self.bot.event
        async def on_message(message):
            if message.author.bot:
                return 
            if trigger.lower() in message.content.lower():
                await message.channel.send(response)
            await self.bot.process_commands(message)
            
    def welcome_member(self, message : str = "Hello {member}, welcome to Server!"):
        
        """
            Sends a welcome message to new members who join the Discord server.
            The message is sent in the server's system channel if it exists.
            
            Parameters:
            ----------
            message : str
                Format messagee for member join the channel
            
        """
        
        @self.bot.event
        async def on_member_join(member):
            channel = member.guild.system_channel
            
            if not channel:
                for ch in member.guild.text_channels:
                    if ch.permissions_for(member.guild.me).send_messages:
                        channel = ch
                        break
                    
            if "{member}" not in message:
                message_to_send = "Hello {member}, welcome to Server!"   
            else:
                message_to_send = message 
                
            message_welcome = message_to_send.replace("{member}", member.name)
            
            
            if channel:
                await channel.send(f"{message_welcome}")
                
    def leave_member(self, message : str = "{member} has left the server"):
        
        """
            Sends a leave message to the system channel
            when a member leaves the server.
            
            Parameters:
            ----------
            message : str
                Format messagee for member leaving the channel
            
        """
        
        @self.bot.event
        async def on_member_remove(member):
            channel = member.guild.system_channel
            
            if not channel:
                for ch in member.guild.text_channels:
                    if ch.permissions_for(member.guild.me).send_messages:
                        channel = ch
                        break
                    
            if "{member}" not in message:
                message_to_send = "{member} has left the server"   
            else:
                message_to_send = message 
                
            message_leave = message_to_send.replace("{member}", member.name)
            
            if channel:
                await channel.send(f"{message_leave}")
            
    def train_bot(self):
        
        """
            Sets up a command to interact with a pre-trained conversational model 
            using the ChatterBot library.
        """
        @self.bot.command()
        async def askbot(ctx, *, message):
            response = self.trainer.get_response(message)
            await ctx.send(response)
            
    def custom_info_command(self, provider='groq', data_path='data.txt'):
        """
        AI command that answers based on specific information from data.txt.

        This command allows the bot to answer user questions using custom knowledge
        stored in a text file (data.txt). The bot will search for the most relevant
        information in the file and use it as context for the AI (OpenAI or Groq)
        to generate a more accurate and specific response.
        """
        import os
        from difflib import get_close_matches

        def load_knowledge(filename):
            """
            Reads the knowledge base from a text file and splits it into entries.

            Each entry is separated by two newlines (\n\n) and can be a paragraph,
            list, or any custom information.

            Returns:
                List[str]: A list of knowledge entries.
            """
            if not os.path.exists(filename):
                return []
            with open(filename, 'r', encoding='utf-8') as f:
                entries = f.read().split('\n\n')
            return entries

        def find_relevant_info(question, entries):
            """
            Finds the most relevant knowledge entries for the user's question.

            Uses fuzzy matching to select up to 2 entries that are most similar
            to the user's question.

            Returns:
                str: The most relevant knowledge entries joined as a single string,
                     or an empty string if no match is found.
            """
            matches = get_close_matches(question, entries, n=2, cutoff=0.2)
            return '\n'.join(matches) if matches else ''

        @self.bot.command(name='infospesifik')
        async def infospesifik(ctx, *, question):
            """
            Discord command: !infospesifik <question>
            Answers the user's question using custom knowledge from data.txt,
            with the help of OpenAI or Groq for natural language generation.
            """
            entries = load_knowledge(data_path)
            context = find_relevant_info(question, entries)
            if context:
                prompt = (
                    f"Use the following information to answer the user's question:\n"
                    f"{context}\n\n"
                    f"Question: {question}\n"
                    f"Answer clearly and specifically."
                )
            else:
                prompt = (
                    f"Question: {question}\n"
                    f"Answer clearly and specifically."
                )

            if provider == 'openai':
                try:
                    import openai
                    openai.api_key = self.ai_providers[provider]['api_key']
                    response = await openai.ChatCompletion.acreate(
                        model=self.ai_providers[provider]['model'] or 'gpt-3.5-turbo',
                        messages=[
                            {"role": "system", "content": "You are a friendly and informative Discord assistant."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    await ctx.send(response.choices[0].message.content)
                except Exception as e:
                    await ctx.send(f"An error occurred with OpenAI: {e}")
            elif provider == 'groq':
                try:
                    from groq import Groq
                    client = Groq(api_key=self.ai_providers[provider]['api_key'])
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "You are a friendly and informative Discord assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        model=self.ai_providers[provider]['model'] or "llama-3.3-70b-versatile",
                        temperature=0.5,
                        max_completion_tokens=1024
                    )
                    await ctx.send(chat_completion.choices[0].message.content)
                except Exception as e:
                    await ctx.send(f"An error occurred with Groq: {e}")
            else:
                await ctx.send("AI provider not supported. Use 'openai' or 'groq'.")

    def run(self, message_run):
        """
            Starts the Discord bot using the provided token.
        """
        
        @self.bot.event
        async def on_ready():
            
            
            name_of_bot = str(self.bot.user)
            
            if "{bot}" in message_run:
                res = message_run.replace("{bot}", name_of_bot)
            else:
                res = f"{name_of_bot} Ready to Use!"
                
            print(res)
            
            

        self.bot.run(self.token)
                    
