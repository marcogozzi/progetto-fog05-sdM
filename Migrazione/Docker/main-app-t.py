import argparse
import json
import os

from time import sleep
from datetime import datetime

state = {}


def load_settings(args):
    settings = {}
    global state
    # os.environ['load_state'] = "a" # for testing purpose
    # Load state from filesystem is load_state is set in environment
    if 'load_state' in os.environ:
        print('found state')
        # Empty dictionaries evaluate to False in Python
        while not state:
            try:
                with open("/tmp/fos/" + datetime.now().strftime("%H:%M:%S"), "w") as wait_file:
                    wait_file.write("state is " + str(state))
            except Exception as e:
                print("Wait file error _" + str(e))
            try:
                with open("/tmp/fos/state.json", "r") as json_file:
                    state = json.load(json_file)
            except Exception as e:
                print("Waiting for state.json to be present in /tmp/fos/")
                with open("/tmp/fos/error", "w") as error_file:
                    error_file.write("error is " + str(e))
                sleep(5)
    state['version'] = '20201019-1145'
    with open('/tmp/fos/after_state', "w") as output:
        output.write(str(state))

    # if configuration is set by config file, an environment variable called is_config is set
    if 'is_config' in os.environ:
        with open(args.config) as json_file:
            settings = json.load(json_file)
            #			data = json.load(json_file)
            #			try:
            #				settings["sleep_period"] = int(data["sleep_period"])
            #			except:
            #				settings["sleep_period"] = 5
            #			try:
            #				settings["iterations"] = int(data["iterations"])
            #			except:
            #				settings["iterations"] = 10
            #			try:
            #				settings["env_output"] = data["env_output"]
            #			except:
            #				settings["env_output"] = "none"
            state["init"] = "config_file"
    # else get values from environment variables
    else:
        try:
            settings["sleep_period"] = int(os.environ["sleep_period"])
        except:
            settings["sleep_period"] = 5
        try:
            settings["iterations"] = int(os.environ["iterations"])
        except:
            settings["iterations"] = 10
        try:
            settings["env_output"] = os.environ["env_output"]
        except:
            settings["env_output"] = "error_env"
        state["init"] = "environment"
    with open("/tmp/fos/end_load_settings", "w") as output:
        output.write("0")
    return settings


def business_logic(settings):
    global state

    with open("/tmp/fos/settings.json", "w") as output:
        json.dump(settings, output)
    with open("/tmp/fos/init_state.json", "w") as output:
        json.dump(state, output)
    if "iteration" not in state:
        state["iteration"] = 0
    print(state)
    for iteration in range(state["iteration"], settings["iterations"]):
        new_file = "test-output-" + str(iteration) + ".txt"
        state["iteration"] = iteration
        with open("/tmp/fos/" + new_file, "w") as output:
            output.write(str(datetime.now()) + "with env out " + settings["env_output"])
        with open("/tmp/fos/state.json", "w") as state_file:
            json.dump(state, state_file)
        sleep(settings["sleep_period"])


def main():
    with open("/tmp/fos/main.txt", "w") as output:
        output.write("start")

    parser = argparse.ArgumentParser(
        prog='main-app',
        description='fog05 containerd demo application',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s V1',
        help='show version information and exit'
    )
    parser.add_argument(
        '--config', '-c',
        dest='config', type=str, metavar='C',
        default=os.getcwd() + '/config/config.json',
        help='relative path to configuration file'
    )

    args = parser.parse_args()
    settings = load_settings(args)
    with open("/tmp/fos/post_settings.txt", "w") as output:
        output.write("start")
    business_logic(settings)
    with open("/tmp/fos/post_bs.txt", "w") as output:
        output.write("start")
    print("Sleep after work")
    sleep(60)


if __name__ == '__main__':
    main()
