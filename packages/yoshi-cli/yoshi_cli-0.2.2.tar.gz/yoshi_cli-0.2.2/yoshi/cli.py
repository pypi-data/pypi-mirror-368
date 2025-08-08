"""
This script uses argparse to parse command line arguments.

It imports the required modules and sets up a parser with basic options for demonstration purposes.
"""

import argparse
from yoshi import crypto, database, process


def yoshi():
    """
    CLI entry point logic, used to parse user inputs.
    """
    parser = argparse.ArgumentParser(
        description="Manage your username and passwords via a convenient CLI vault."
    )

    # Top-level arguments
    group_one = parser.add_mutually_exclusive_group()
    group_one.add_argument(
        "-n", "--new", help="Create a new account.", action="store_true"
    )
    group_one.add_argument(
        "-l", "--list", help="List all saved accounts.", action="store_true"
    )
    group_one.add_argument(
        "-e", "--edit", help="Edit a saved account.", action="store_true"
    )
    group_one.add_argument(
        "-d", "--delete", help="Delete a saved account.", action="store_true"
    )
    group_one.add_argument(
        "--purge",
        help=(
            "Purge all accounts and delete the vault. "
            "(Caution: this will irreversibly destroy your data.)"
        ),
        action="store_true",
    )
    group_one.add_argument("--encrypt", help="Encrypt the vault.", action="store_true")
    group_one.add_argument("--decrypt", help="Decrypt the vault.", action="store_true")

    # Encryption flags
    group_two = parser.add_mutually_exclusive_group()
    group_two.add_argument(
        "-g",
        "--generate",
        help=("When using the --encrypt option, generate a new encryption key."),
        action="store_true",
    )
    group_two.add_argument(
        "-k",
        "--keyfile",
        help="Path to existing key file.",
        action="store",
        nargs=1,
        type=str,
    )

    # Edit flags
    group_three = parser.add_argument_group()
    group_three.add_argument(
        "-u",
        "--uuid",
        help=("When using the --edit or --delete options, provide the account UUID."),
        action="store",
        nargs=1,
        type=str,
    )
    group_three.add_argument(
        "-f",
        "--field",
        help=(
            "When using the --edit option, specify the field to edit (integer index)."
        ),
        action="store",
        nargs=1,
        type=int,
    )

    args = parser.parse_args()

    if args.decrypt:
        if args.keyfile:
            key = crypto.load_key(args.keyfile[0])
        else:
            key = input("Please enter your decryption key: ")
        crypto.decrypt(key)
    elif args.encrypt:
        if args.generate:
            key = crypto.generate_key()
            print(
                "WRITE THIS KEY DOWN SOMEWHERE SAFE. YOU WILL NOT BE ABLE TO DECRYPT "
                "YOUR DATA WITHOUT IT!"
            )
            print(key.decode())
            print("\n")
        else:
            if args.keyfile:
                key = crypto.load_key(args.keyfile[0])
            else:
                key = input("Please enter your encryption key: ")
        crypto.encrypt(key)
    elif database.check_table():
        if args.new:
            process.create_account()
        elif args.list:
            process.list_accounts()
        elif args.edit:
            process.edit_account(args.uuid[0], args.field[0])
        elif args.delete:
            process.delete_account(args.uuid[0])
        elif args.purge:
            process.purge_accounts()
        else:
            raise TypeError(
                "Please specify a command or use the --help flag for more information."
            )


if __name__ == "__main__":
    yoshi()
