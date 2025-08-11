from typing import Type

from robotooter import RoboTooter
from robotooter.cli.util import get_yes


def get_options(text:str, options: dict[str, Type], required: bool = False, only_one: bool = False)-> list[str]:
    print(text)
    keys = sorted(options.keys())

    for i, key in enumerate(keys):
        print(f"{i+1}. {key}")

    choices = input("Select an option: ")
    parts = choices.split(",")
    chosen_keys = [keys[int(x.strip()) - 1] for x in parts if x.strip()]
    if not chosen_keys:
        if required:
            print("\nsorry, you must choose at least one option\n")
            return get_options(text, options, required=required, only_one=only_one)
    if only_one and len(chosen_keys) > 1:
        print("\nsorry, you must choose ONLY one option\n")
        return get_options(text, options, required=required, only_one=only_one)

    return chosen_keys


def run_create_bot(rt: RoboTooter) -> None:
    bot_name = ''
    bot_class = ''
    filter_names: list[str] = []

    all_set = False
    while not all_set:
        print("Let's get your bot's information.")
        bot_name = input("Enter the bot name: ")
        bot_class = get_options("Select a bot class", rt._bots, True, True)[0]
        filter_names = get_options("Select filters", rt._filters)

        print("\nHere's what we have:")
        print("bot_name:", bot_name)
        print("bot_class:", bot_class)
        print("filter_names:", filter_names)
        print("")
        all_set = get_yes("Is this correct?")

    rt.create_new_bot(
        bot_name=bot_name,
        bot_class=bot_class,
        filter_names=filter_names,
    )
    print("Bot created successfully")
    bot = rt._bots[bot_class]
    if bot.new_bot_info():
        print(bot.new_bot_info())
