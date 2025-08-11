from configparser import ConfigParser
import os
import time
import questionary


def getconfig(action, account: str | None = None):
    if action == "account":
        account_maker()
    if action == "config":
        if account is not None:
            config_maker_barons(account)
        else:
            print("Error: account name must be provided for config action.")


def account_maker():
    config_dir = os.path.join('.', 'configs')
    os.makedirs(config_dir, exist_ok=True)
    accountlist_path = os.path.join(config_dir, 'accountlist.ini')

    config = ConfigParser()
    if os.path.exists(accountlist_path):
        config.read(accountlist_path)

    account_name = questionary.text("Enter account name:").ask()
    if not account_name:
        print("Account name cannot be empty.")
        return

    if config.has_section(account_name):
        overwrite = questionary.confirm(
            f"Account '{account_name}' already exists. Overwrite?"
        ).ask()
        if not overwrite:
            print("Aborted.")
            return
        config.remove_section(account_name)

    username = questionary.text("Enter nickname:").ask()
    password = questionary.password("Enter password:").ask()
    server = questionary.text("Enter server:").ask()

    config.add_section(account_name)
    config.set(account_name, 'username', username)
    config.set(account_name, 'password', password)
    config.set(account_name, 'server', server)

    with open(accountlist_path, 'w') as f:
        config.write(f)

    print(f"Account '{account_name}' saved to {accountlist_path}. Exiting...")
    time.sleep(1)
    exit()


def config_maker_barons(filename: str):
    config_dir = os.path.join('.', 'configs')
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, f"{filename}_config.ini")
    config = ConfigParser()

    unit_options = {
        "1": ("Distance Veteran Demon", '10'),
        "2": ("Distance Mead lvl 10", '216'),
        "3": ("Meelee   Mead lvl 10", '215'),
    }

    flank_tool_options = {
        "1": ("5%   ladders", '614'),
        "2": ("5%   wooden shields", '651'),
        "3": ("--   None", '-1')
    }

    front_tool_options_1 = {
        "1": ("5%   ladders", '614'),
        "2": ("5%   wooden walls (anti distance)", '651'),
        "3": ("--   None", '-1')
    }

    front_tool_options_2 = {
        "1": ("20%  ram", '648'),
        "2": ("5%   ram", '611'),
        "3": ("--   None", '-1')
    }

    if os.path.exists(config_path):
        config.read(config_path)

    print(f"Saves: {config.sections()}")
    save_name = questionary.text(
        "Enter the desired config name (e.g. pluto_ice):"
    ).ask()

    if not save_name:
        print("No name entered, exiting.")
        exit()

    if config.has_section(save_name):
        overwrite = questionary.confirm(
            f"Save '{save_name}' already exists. Overwrite?"
        ).ask()
        if not overwrite:
            print("Exiting.")
            exit()
        config.remove_section(save_name)

    config.add_section(save_name)

    def input_int_list(prompt):
        while True:
            raw = questionary.text(prompt).ask()
            try:
                values = [int(item.strip()) for item in raw.split(",") if item.strip()]
                return ",".join(str(val) for val in values)
            except ValueError:
                print("Please enter valid comma separated integers (e.g. 2,29,30).")

    def input_int(prompt):
        while True:
            raw = questionary.text(prompt).ask()
            try:
                return str(int(raw))
            except ValueError:
                print("Please enter a valid integer.")

    kid = questionary.select(
        "Select Kingdom:",
        choices=["Green", "Fire", "Sands", "Ice"]
    ).ask()
    config.set(save_name, "kid", kid)

    excluded_commanders = input_int_list(
        "Enter excluded commanders (comma separated integers, -1 if none):"
    )
    config.set(save_name, "excluded_commanders", excluded_commanders)

    distance = input_int("Distance for attacks (not precise):")
    config.set(save_name, "distance", distance)

    horse_choice = questionary.select(
        "Type of horse:",
        choices=["Coin", "Feather"]
    ).ask()

    horse_map = {
        "Coin": "1007",
        "Feather": "-1"
    }
    config.set(save_name, "horse", horse_map[horse_choice])

    print("The script will use 4 waves, same setup each wave.")

    max_flank = input_int("Enter number of units on a flank (0 if none):")
    config.set(save_name, "max_flank", max_flank)

    max_front = input_int("Enter number of units on the front (0 if none):")
    config.set(save_name, "max_front", max_front)

    unit_choice = questionary.select(
        "Pick units to send in the attack:",
        choices=[f"{k} - {v[0]}" for k, v in unit_options.items()]
    ).ask().split(" - ")[0]
    config.set(save_name, "unit_id", unit_options[unit_choice][1])

    flank_choice = questionary.select(
        "Pick tool for the flanks:",
        choices=[f"{k} - {v[0]}" for k, v in flank_tool_options.items()]
    ).ask().split(" - ")[0]
    config.set(save_name, "flank_id", flank_tool_options[flank_choice][1])

    if flank_tool_options[flank_choice][0] != "--   None":
        flank_amt = input_int("Enter amount of those tools per flank:")
        config.set(save_name, "flank_tool_ammount", flank_amt)
    else:
        config.set(save_name, "flank_tool_ammount", "0")

    front_choice1 = questionary.select(
        "Pick first tool for the front:",
        choices=[f"{k} - {v[0]}" for k, v in front_tool_options_1.items()]
    ).ask().split(" - ")[0]
    config.set(save_name, "front_id_1", front_tool_options_1[front_choice1][1])

    if front_tool_options_1[front_choice1][0] != "--   None":
        front_amt1 = input_int("Enter amount of those tools per front:")
        config.set(save_name, "front_tool_ammount1", front_amt1)
    else:
        config.set(save_name, "front_tool_ammount1", "0")

    front_choice2 = questionary.select(
        "Pick second tool for the front:",
        choices=[f"{k} - {v[0]}" for k, v in front_tool_options_2.items()]
    ).ask().split(" - ")[0]
    config.set(save_name, "front_id_2", front_tool_options_2[front_choice2][1])

    if front_tool_options_2[front_choice2][0] != "--   None":
        front_amt2 = input_int("Enter amount of those tools per front:")
        config.set(save_name, "front_tool_ammount2", front_amt2)
    else:
        config.set(save_name, "front_tool_ammount2", "0")

    with open(config_path, "w") as f:
        config.write(f)

    print(f"Configuration saved to {config_path}.")
    exit()
