# -*- coding: utf-8 -*-
import argparse

from vpnflow import __author__

console_art_short = """
__     __ ____   _   _  _____  _       ___  __        __
\ \   / /|  _ \ | \ | ||  ___|| |     / _ \ \ \      / /
 \ \ / / | |_) ||  \| || |_   | |    | | | | \ \ /\ / / 
  \ V /  |  __/ | |\  ||  _|  | |___ | |_| |  \ V  V /  
   \_/   |_|    |_| \_||_|    |_____| \___/    \_/\_/   

"""
console_art = """
__     __ ____   _   _  _____  _       ___  __        __
\ \   / /|  _ \ | \ | ||  ___|| |     / _ \ \ \      / /
 \ \ / / | |_) ||  \| || |_   | |    | | | | \ \ /\ / / 
  \ V /  |  __/ | |\  ||  _|  | |___ | |_| |  \ V  V /  
   \_/   |_|    |_| \_||_|    |_____| \___/    \_/\_/   

                | |__   _   _ 
                | '_ \ | | | |
                | |_) || |_| |
                |_.__/  \__, |
                        |___/ 
    ___     ____   ____     ____    ____ __  __
   /   |   /  _/  / __ \   / __ )  / __ \\ \/ /
  / /| |   / /   / / / /  / __  | / / / / \  / 
 / ___ | _/ /   / /_/ /  / /_/ / / /_/ /  / /  
/_/  |_|/___/   \____/  /_____/  \____/  /_/   

"""


def create_parser():
    """⭐"""
    parser = argparse.ArgumentParser(
        usage='%(prog)s', description=console_art_short,
        epilog=f"vpnflow. Copyright © 2025 {__author__}",
        formatter_class=argparse.RawDescriptionHelpFormatter, add_help=True
        )
    parser.add_argument("--log-conf-file", action="store", type=str, help=".yaml file path")
    parser.add_argument("--run-scheduled-tasks", action="store_true")

    subparsers = parser.add_subparsers(dest="command")

    parser_db = subparsers.add_parser("db")
    parser_db.add_argument("--drop", action="store_true")
    parser_db.add_argument("--create", action="store_true")
    parser_db.add_argument("--insert", action="store", help=".yaml file path")
    return parser


def show_art():
    """⭐"""
    print(console_art)
