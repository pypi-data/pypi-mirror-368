# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-3.0-or-later
import argparse
import logging
import os
import requests
import toml

AVAILABLE_EXECUTORS = {
    'clever-docker': "Clever Cloud Docker",
    'local-docker': "Local Docker for testing purposes only",
    'service-docker': "Fixed PAAS Resource helper service for testing only",
}

logger = logging.getLogger(__name__)


def register(conf_path, runner_name, coordinator_url, token, executor):
    """Use token to register runner with given executor and write to conf_path.
    """
    resp = requests.post(coordinator_url.rstrip('/') + '/api/v4/runners',
                         json=dict(info=dict(name=runner_name),
                                   description=runner_name,
                                   active=False,
                                   token=token,
                                   ))

    if resp.status_code >= 400:
        raise RuntimeError(resp.status_code, resp.text)

    runner_token = resp.json()['token']

    runner = dict(
        name=runner_name,
        url=coordinator_url,
        token=runner_token,
        executor=executor)

    with open(conf_path, 'a') as conf_file:
        conf_file.write('\n')
        conf_file.write(toml.dumps(dict(runners=[runner])))


def positive_int(s):
    i = int(s)
    if i <= 0:
        raise TypeError("Not a positive integer: %r" % s)
    return i


def non_empty_string(s):
    if not s or not isinstance(s, str):
        raise TypeError("Empty string (or not a string) "
                        "is not allowed: %r" % s)
    return s


def create_conf_file(path, state_file_path, concurrency):
    with open(path, 'w') as conf_file:
        toml.dump(dict(state_file=state_file_path,
                       concurrent=concurrency),
                  conf_file)


def valid_input(value, prompt="", initial_message=None,
                converter=non_empty_string):
    """Repeatedly ask user for input and convert it until valid.

    :param value: can be ``None``, which is expected to always be invalid
       (argparse default), without user feedback about it. In other invalid
       cases (actual value provided or wrong input), a warning log is issued.
    """
    converted = None
    first = True

    if prompt:
        prompt = prompt.strip() + ': '

    while converted is None:
        try:
            converted = converter(value)
        except (TypeError, ValueError) as exc:
            if value is not None:
                logger.warning(str(exc))

            if first and initial_message:
                print(initial_message)
                first = False

            value = input(prompt).strip()

    return converted


def valid_executor(exe):
    if exe not in AVAILABLE_EXECUTORS:
        raise ValueError("Not an available executor: %r" % exe)
    return exe


def main(raw_args=None):
    """Console script entry point.
    """
    parser = argparse.ArgumentParser(
        description="Initiate a Runner configuration by performing the "
        "GitLab registration",
        epilog="The configuration file will be created if needed "
        "and the new Runner configuration appended to it."
    )
    parser.add_argument("config", help="Path to Heptapod Runner "
                        "configuration file to write into")
    parser.add_argument("--name", help="Runner name")
    parser.add_argument('-c', "--coordinator-url",
                        help="Base URL of the GitLab / Heptapod instance to "
                        "run for")
    parser.add_argument('-t', "--registration-token",
                        help="Registration token, as found in Application "
                        "Group or Project settings")
    parser.add_argument('-e', "--executor",
                        choices=AVAILABLE_EXECUTORS.keys())
    init_conf_grp = parser.add_argument_group(
        title="Configuration creation options",
        description="Options if configuration file does not already exist")
    init_conf_grp.add_argument('--max-concurrency', type=int,
                               help="Maximum number of concurrent jobs across "
                               "all runners")
    init_conf_grp.add_argument('--state-file-path',
                               help="File to keep Runner "
                               "state across restarts")

    parser.add_argument("-l", "--logging-level", default='INFO')

    cl_args = parser.parse_args(raw_args)
    logging.basicConfig(level=getattr(logging, cl_args.logging_level.upper()))

    conf_path = cl_args.config
    if not os.path.exists(conf_path):
        print("This is a brand new configuration file!\n")
        state_path = valid_input(
            value=cl_args.state_file_path,
            prompt="State file path",
            initial_message="Please enter state file path "
            "(used to maintain state across restarts, must be writable)")
        concurrency = valid_input(
            value=cl_args.max_concurrency,
            prompt="Concurrency",
            initial_message="Please choose maximum concurrency "
            "(across all runners to be defined in %s" % conf_path,
            converter=positive_int)
        create_conf_file(path=conf_path,
                         state_file_path=state_path,
                         concurrency=concurrency)

    coord_url = valid_input(value=cl_args.coordinator_url,
                            prompt="URL",
                            initial_message="Please enter base URL of the "
                            "GitLab / Heptapod instance to run for")
    runner_name = valid_input(value=cl_args.name,
                              prompt="Please enter runner name")
    reg_token = valid_input(value=cl_args.registration_token,
                            prompt="Please enter registration token")
    available_executors_str = "\n".join(
        "  %s (%s)" % (exe, label)
        for exe, label in AVAILABLE_EXECUTORS.items()
    )
    executor = valid_input(
        value=cl_args.executor,
        converter=valid_executor,
        prompt="Executor",
        initial_message="Please choose an executor. "
        "Available choices are:\n" + available_executors_str)

    try:
        register(conf_path=conf_path,
                 coordinator_url=coord_url,
                 runner_name=runner_name,
                 token=reg_token,
                 executor=executor)
    except RuntimeError as exc:
        logger.error("Failed to register runner: HTTP status code %d, "
                     "Body: %r", *exc.args)
        return 1
    return 0
