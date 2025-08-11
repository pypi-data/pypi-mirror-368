import os

from robotooter.bots.base_bot import BaseBot
from robotooter.cli.util import get_yes


def run_authorize(bot: BaseBot, force: bool) -> None:
    if bot.mastodon_manager.access_token_exists:
        if force or get_yes("Mastodon authentication file already exists. Do you want to replace it?"):
            if bot.mastodon_manager.access_token:
                os.remove(bot.mastodon_manager.access_token)
        else:
            print("Keeping current authentication settings.")
            return

    all_set = False
    client_key = ''
    client_secret = ''
    api_base_url = ''
    while not all_set:
        print("Let's get your information.")
        client_key = input("Enter your client key: ")
        client_secret = input("Enter your client secret: ")
        api_base_url = input("Enter your API base URL (for example, https://mastodon.social): ")

        print("\nHere's what we have:")
        print("client_key:", client_key)
        print("client_secret:", client_secret)
        print("api_base_url:", api_base_url)
        print("")
        all_set = get_yes("Is this correct? Enter 'y' to continue, otherwise we'll try again.")

    print("\nGreat! Now we will request an authorization URL.")
    auth_url = bot.get_auth_url(
        client_key=client_key, client_secret=client_secret, api_base_url=api_base_url
    )
    print("Here's your authorization URL:")
    print(auth_url)

    print("\nYou need to open that in a browser, make sure you're logged into Mastodon, and authorize")
    print("the application to user the account. It will give you a code, which you will enter here.")
    code = input("Enter authorization code: ")

    bot.log_in(code=code)

    print(f"Success! {bot.config.bot_name} should be set to toot up a storm.")
