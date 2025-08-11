# Copyright (C) 2024 Bryan L. Fordham
# 
# This file is part of RoboTooter.
#
# RoboTooter is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RoboTooter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with RoboTooter. If not, see <https://www.gnu.org/licenses/>.

import argparse

from robotooter import RoboTooter
from robotooter.bots.base_bot import BaseBot
from robotooter.rt import load_robo_tooter

parser = argparse.ArgumentParser(
    prog='robotooter',
    description='Simplifying Mastodon Bots',
    epilog='Licensed under AGPL-3.0. See LICENSE file for details.'
)

parser.add_argument('-b', '--bot', help='Speficy which bot to use')

subparsers = parser.add_subparsers(help='subcommand help', dest='command')

parser_info = subparsers.add_parser('info', help='Display info about the local setup, then exit')

parser_configure = subparsers.add_parser('configure', help='Initialize configuration.')

parser_speak = subparsers.add_parser('speak', help='Output a sentence. Ignores quiet.')
parser_speak.add_argument('-c', '--count', default=1, type=int, help='Number of sentences to output')

parser_toot = subparsers.add_parser('toot', help='Create a sentence and toot it. Prints the sentence unless quiet.')

parser_create = subparsers.add_parser('create-bot', help='Create a new bot.')
parser_setup = subparsers.add_parser('setup', help='Run data setup for a bit.')
parser_authorize = subparsers.add_parser('authorize', help='Authorize a bot.')
parser_authorize.add_argument('-f', '--force', action='store_true', help='Force removal of existing files.')

def require_bot(robo: RoboTooter, args: argparse.Namespace) -> BaseBot:
    if not args.bot:
        raise Exception("Must specify a bot to use with --bot")
    return robo.load_bot(args.bot)

def main() -> None:
    args = parser.parse_args()
    rt = load_robo_tooter()

    match args.command:
        case 'info':
            from robotooter.cli.info import run_info
            run_info(rt)

        case 'configure':
            from robotooter.cli.configure import run_configure
            run_configure(rt)

        case 'create-bot':
            from robotooter.cli.create_bot import run_create_bot
            run_create_bot(rt)

        case 'speak':
            bot = require_bot(rt, args)
            for _ in range(args.count):
                for line in bot.generate_content():
                    print(line)

        case 'toot':
            bot = require_bot(rt, args)
            bot.toot()
        case 'setup':
            bot = require_bot(rt, args)
            print(f"Running setup for {args.bot}")
            bot.setup_data()
        case 'authorize':
            bot = require_bot(rt, args)
            from robotooter.cli.authorize import run_authorize
            run_authorize(bot, args.force)
        case _:
            parser.print_help()

if __name__ == '__main__':
    main()
