import json
import sys
import csv
import re
from functools import wraps

import click
from dotted.collection import DottedDict
from requests.exceptions import HTTPError as RequestsHTTPError

from .api import load_config, save_config, get_manager, filter_users
from .okta import REST
from .exceptions import ExitException


VERSION = "2.3.1"

okta_manager = None
config = None

FILTER_PATTERN = '(eq|sw|gt|ge|lt|le) ([^ )"]+)'
FILTER_MATCHER = re.compile(FILTER_PATTERN)

# https://is.gd/T1enMM
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def _command_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global okta_manager
        global config
        try:
            okta_manager = get_manager()
            rv = func(*args, **kwargs)
            if not isinstance(rv, str):
                print(json.dumps(rv, indent=2, sort_keys=True))
            else:
                print(rv)
        except ExitException as e:
            print("ERROR: {}".format(str(e)))
            sys.exit(-1)
    return wrapper


def _dict_flat_to_nested(flat_dict, defaults=None):
    """
    Takes a "flat" dictionary, whose keys are of the form "one.two.three".
    It will return a nested dictionary with this content:
    {one: {two: {three: value}}}.

    :param flat_dict: The dictionary to convert to a nested one
    :param defaults: Default values to use if flat_dict does not provide them
    :return: A nested python dictionary
    """
    tmp = DottedDict()
    if defaults is None:
        defaults = {}
    # values from flat_dict have precedence over default values
    for key, val in defaults.items():
        tmp[key] = val
    for key, val in flat_dict.items():
        # key can be "one.two", so keys with a dot in their name are not
        # permitted, cause they are interpreted ...
        tmp[key] = val
    return tmp.to_python()


def _prepare_okta_filter_string(filter_string):
    return re.sub(FILTER_MATCHER, '\g<1> "\g<2>"', filter_string)


def _okta_get_groups_by_name(name, unique=False):
    groups = okta_manager.list_groups()
    groups = list(filter(
            lambda x: x["profile"]["name"].lower().find(name.lower()) != -1,
            groups))
    if unique and len(groups) != 1:
        raise ExitException("Group name must be unique. "
                            f"(found '{len(groups)}' matching groups).")
    return groups


@click.group(name="config")
def cli_config():
    """Manage okta-cli configuration"""
    pass


@cli_config.command(name="new", context_settings=CONTEXT_SETTINGS)
@click.option("-n", "--name", required=True, prompt=True,
              help="Name of the configuration to add.")
@click.option("-u", "--url", required=True, prompt=True,
              help="The base URL of Okta, e.g. 'https://my.okta.com'.")
@click.option("-t", "--token", required=True, prompt=True,
              help="The API token to use")
def config_new(name, url, token):
    global config
    try:
        config = load_config()
    except ExitException:
        config = dict(
                profiles={}
        )
    config["profiles"][name] = dict(
            url=url,
            token=token,
    )
    save_config(config)
    print("Profile '{}' added.".format(name))


@cli_config.command(name="list", context_settings=CONTEXT_SETTINGS)
def config_list():
    global config
    config = load_config()
    for name, conf in config["profiles"].items():
        print("{}  {}  {}".format(name, conf["url"], "*"*3+conf["token"][38:]))


@cli_config.command(name="use-context", context_settings=CONTEXT_SETTINGS)
@click.argument("profile-name")
@_command_wrapper
def config_use_context(profile_name):
    global config
    config = load_config()
    if profile_name not in config["profiles"]:
        raise ExitException("Unknown profile name: '{}'.".format(profile_name))
    config["default"] = profile_name
    save_config(config)
    return "Default profile set to '{}'.".format(profile_name)


@cli_config.command(name="current-context", context_settings=CONTEXT_SETTINGS)
@_command_wrapper
def config_current_context():
    global config
    config = load_config()
    if "default" not in config:
        return "No profile set."
    return "Current profile set to '{}'.".format(config["default"])


@click.group(name="pw")
def cli_pw():
    """Manage passwords"""
    pass


@cli_pw.command(name="reset", context_settings=CONTEXT_SETTINGS)
@click.argument("login-or-id")
@click.option("-n", "--no-email", is_flag=True)
@_command_wrapper
def pw_reset(login_or_id, no_email):
    """Reset the password of a user"""
    return okta_manager.reset_password(login_or_id, send_email=not no_email)


@cli_pw.command(name="expire", context_settings=CONTEXT_SETTINGS)
@click.argument("login-or-id")
@click.option("-t", "--temp-password", is_flag=True)
@_command_wrapper
def pw_expire(login_or_id, temp_password):
    """Expire the password of a user"""
    return okta_manager.expire_password(login_or_id,
                                        temp_password=temp_password)


@click.group(name="groups")
def cli_groups():
    """Group operations"""
    pass


@cli_groups.command(name="list", context_settings=CONTEXT_SETTINGS)
@click.option("-f", "--filter", 'api_filter', default="")
@click.option("-q", "--query", 'api_query', default="")
@_command_wrapper
def groups_list(api_filter, api_query):
    """List all defined groups"""
    return okta_manager.list_groups(filter=api_filter, query=api_query)


@cli_groups.command(name="users", context_settings=CONTEXT_SETTINGS)
@click.argument("name-or-id")
@click.option("-i", "--id", 'use_id', is_flag=True, default=False,
              help="Use Okta group ID instead of the group name")
@_command_wrapper
def groups_list_users(name_or_id, use_id):
    """List all users in a group"""
    if not use_id:
        name_or_id = _okta_get_groups_by_name(name_or_id, unique=True)[0]["id"]
    return okta_manager.call_okta(f"/groups/{name_or_id}/users", REST.get)


@cli_groups.command(name="clear", context_settings=CONTEXT_SETTINGS)
@click.argument("name-or-id")
@click.option("-i", "--id", 'use_id', is_flag=True, default=False,
              help="Use Okta group ID instead of the group name")
@_command_wrapper
def groups_clear(name_or_id, use_id):
    """Remove all users from a group.

    This can take a while if the group is big."""
    if not use_id:
        name_or_id = _okta_get_groups_by_name(name_or_id, unique=True)[0]["id"]
    users = okta_manager.call_okta(f"/groups/{name_or_id}/users", REST.get)
    for user in users:
        user_id = user['id']
        user_login = user['profile']['login']
        print(f"Removing user {user_login} ... ", file=sys.stderr, end="")
        path = f"/groups/{name_or_id}/users/{user_id}"
        okta_manager.call_okta_raw(path, REST.delete)
        print("ok", file=sys.stderr)
    return "All users removed"


@click.group(name="apps")
def cli_apps():
    """Application operations"""
    pass


@cli_apps.command(name="list", context_settings=CONTEXT_SETTINGS)
@click.argument("partial_name", required=False, default=None)
@click.option("-f", "--filter", 'api_filter', default="")
@_command_wrapper
def apps_list(api_filter, partial_name):
    """List all defined applications. If you give an optional command line
    argument, the apps are filtered by name using this string."""
    params = {}
    if api_filter:
        params = {"filter": api_filter}
    rv = okta_manager.call_okta("/apps", REST.get, params=params)
    # now filter by name, if given
    if partial_name:
        matcher = re.compile(partial_name)
        rv = list(filter(lambda x: matcher.search(x["name"]), rv))
    return rv


@cli_apps.command(name="users", context_settings=CONTEXT_SETTINGS)
@click.argument("app_id")
@click.option("-n", "--use-name", is_flag=True,
              help="Look for app by name instead of Okta app ID")
@_command_wrapper
def apps_users(app_id, use_name):
    """List all users for an application"""
    if use_name:
        apps = okta_manager.call_okta("/apps", REST.get)
        matcher = re.compile(app_id.lower())
        apps = list(filter(lambda x: matcher.search(x["name"].lower()), apps))
        if len(apps) != 1:
            raise ExitException(f"Found {len(apps)} matching apps. Must be 1!")
        use_app_id = apps[0]["id"]
    else:
        use_app_id = app_id
    return okta_manager.call_okta(f"/apps/{use_app_id}/users", REST.get)


@click.group(name="users")
def cli_users():
    """Add, update (etc.) users"""
    pass


@cli_users.command(name="list", context_settings=CONTEXT_SETTINGS)
@click.option("-m", "--match", 'matches', multiple=True)
@click.option("-p", "--partial", is_flag=True,
              help="Accept partial matches for match queries.")
@click.option("-f", "--filter", 'api_filter', default="")
@click.option("-s", "--search", 'api_search', default="")
@_command_wrapper
def users_list(matches, partial, api_filter, api_search):
    """Lists users (all or using various filters)"""
    users = okta_manager.list_users(
            filter_query=_prepare_okta_filter_string(api_filter),
            search_query=_prepare_okta_filter_string(api_search))
    filters_dict = {k: v for k, v in map(lambda x: x.split("="), matches)}
    return list(filter_users(users, filters=filters_dict, partial=partial))


@cli_users.command(name="get", context_settings=CONTEXT_SETTINGS)
@click.argument('login_or_id')
@click.option("-i", "--use-id", 'use_id', is_flag=True,
              help="Search by Okta ID instead of login field")
@_command_wrapper
def users_get(login_or_id, use_id):
    """List ONE user by login or Okta ID"""
    if use_id:
        rv = okta_manager.call_okta(f"/users/{login_or_id}", REST.get)
    else:
        query = f'profile.login eq "{login_or_id}"'
        rv = okta_manager.list_users(filter_query=query)
    return rv


@cli_users.command(name="deactivate", context_settings=CONTEXT_SETTINGS)
@click.argument('login_or_id')
@click.option("-e", "--send-email", is_flag=True,
              help="Send email to admins if set")
@click.option("--no-confirmation", is_flag=True,
              help="Don't ask - DANGER!!")
@_command_wrapper
def users_deactivate(login_or_id, send_email, no_confirmation):
    """Deactivate a user (DESTRUCTIVE OPERATION)"""
    params = {}
    if send_email:
        params["sendEmail"] = "TRUE"
    if not no_confirmation:
        check = input("DANGER!! Do you REALLY want to do this "
                      "(maybe use 'suspend' instead)?\n"
                      f"Then enter '{login_or_id}': ")
        if check != login_or_id:
            raise ExitException("Aborted.")
    okta_manager.call_okta(
        f"/users/{login_or_id}/lifecycle/deactivate", REST.post,
        params=params)
    return f"User '{login_or_id}' deactivated."


@cli_users.command(name="delete", context_settings=CONTEXT_SETTINGS)
@click.argument('login_or_id')
@click.option("-e", "--send-email", is_flag=True,
              help="Send email to admins if set")
@click.option("--no-confirmation", is_flag=True,
              help="Don't ask - DANGER!!")
@_command_wrapper
def users_delete(login_or_id, send_email, no_confirmation):
    """Delete a user (DESTRUCTIVE OPERATION)"""
    params = {}
    if send_email:
        params["sendEmail"] = "TRUE"
    if not no_confirmation:
        check = input("DANGER!! Do you REALLY want to do this?\n"
                      f"Then enter '{login_or_id}': ")
        if check != login_or_id:
            raise ExitException("Aborted.")
    okta_manager.call_okta_raw(
        f"/users/{login_or_id}", REST.delete,
        params=params)
    return f"User '{login_or_id}' deleted."


@cli_users.command(name="suspend", context_settings=CONTEXT_SETTINGS)
@click.argument('login_or_id')
@_command_wrapper
def users_suspend(login_or_id):
    """Suspend a user"""
    path = f"/users/{login_or_id}/lifecycle/suspend"
    rv = okta_manager.call_okta(path, REST.post)
    return rv


@cli_users.command(name="update", context_settings=CONTEXT_SETTINGS)
@click.argument('user_id')
@click.option('-s', '--set', 'set_fields', multiple=True)
@click.option('-c', '--context', default=None,
              help="Set a context (profile, credentials) to save typing")
@_command_wrapper
def users_update(user_id, set_fields, context):
    """Update a user object. see https://is.gd/DWHEvA for details.

    This is equivalent:

    \b
    okta-cli users update 012345 -s profile.lastName=Doe
    okta-cli users update 012345         -s lastName=Doe -c profile

    EXAMPLE: Update a profile field:

    \b
    okta-cli users update 012345 \\
       -s profile.email=me@myself.com

    EXAMPLE: Set a new password:

    \b
    okta-cli users update 012345 \\
       -s credentials.password.value="SoopaS3cret!"

    EXAMPLE: Update a recovery question:

    \b
    okta-cli users update 012345 \\
       -p credentials.recovery_question \\
       -s question="Who let the dogs out?" \\
       -s answer="Me."
    """
    fields_dict = {k: v for k, v in map(lambda x: x.split("="), set_fields)}
    if context:
        fields_dict = {context + "." + k: v for k, v in fields_dict.items()}
    nested_dict = _dict_flat_to_nested(fields_dict)
    return okta_manager.update_user(user_id, nested_dict)


@cli_users.command(name="update-csv", context_settings=CONTEXT_SETTINGS)
@click.argument('csv-file')
@click.option('-s', '--set', 'set_fields', multiple=True,
              help="Set default field values for updates")
@click.option('-i', '--jump-to-index', metavar="IDX",
              default=0,
              help="Start with index IDX (0-based) and skip previous entries")
@click.option('-u', '--jump-to-user', metavar="USER_ID",
              default=None,
              help="Same as --jump-to-index, but starts from a specific user "
                   "ID instead of an index")
@click.option('-l', '--limit', metavar="NUM",
              default=0,
              help="Stop after NUM updates")
@_command_wrapper
def users_bulk_update(csv_file, set_fields, jump_to_index, jump_to_user, limit):
    """Bulk-update users from a CSV file"""
    fields_dict = {k: v for k, v in map(lambda x: x.split("="), set_fields)}
    rv = []
    errors = []
    counter = 0
    with open(csv_file, "r", encoding="utf-8") as infile:
        dialect = csv.Sniffer().sniff(infile.read(4096))
        infile.seek(0)
        dr = csv.DictReader(infile, dialect=dialect)
        for _ in range(jump_to_index):
            next(dr)
        print("0..", file=sys.stderr, end="")
        for row in dr:
            if counter and counter % 50 == 0:
                print(f"..{counter}", file=sys.stderr, flush=True, end="")
            if limit and counter > limit:
                break
            if jump_to_user:
                if row["profile.login"] != jump_to_user:
                    continue
                else:
                    jump_to_user = None
            user_id = row.pop("profile.login")
            final_dict = _dict_flat_to_nested(row, defaults=fields_dict)
            try:
                rv.append(okta_manager.update_user(user_id, final_dict))
            except RequestsHTTPError as e:
                errors.append((counter + jump_to_index, final_dict, str(e)))
            counter += 1
    print("", file=sys.stderr)
    return {"done": rv, "errors": errors}


@cli_users.command(name="add", context_settings=CONTEXT_SETTINGS)
@click.option('-s', '--set', 'set_fields', multiple=True)
@click.option('-r', '--read-csv', help="Read from CSV file", default=None)
@click.option('-a', '--activate/--no-activate',
              help="Set 'activation' flag, see Okta API docs")
@click.option('-p', '--provider/--no-provider',
              help="Set 'provider' flag, see Okta API docs")
@click.option('-n', '--nextlogin/--no-nextlogin',
              help="Set 'nextLogin' to 'changePassword', see Okta API docs")
@_command_wrapper
def users_add(set_fields, read_csv, activate, provider, nextlogin):
    """Add a user to Okta"""
    # first use and clean the fields dict from the command line
    fields_dict = {k: v for k, v in map(lambda x: x.split("="), set_fields)}
    # query parameters
    params = {}
    # set the flags
    if activate:
        params['activate'] = str(activate).upper()
    if provider:
        params['provider'] = str(provider).upper()
    if nextlogin:
        params['nextlogin'] = "changePassword"
    # when reading from csv, we iterate
    if read_csv:
        added = []
        with open(read_csv, "r", encoding="utf-8") as infile:
            dialect = csv.Sniffer().sniff(infile.read(4096))
            infile.seek(0)
            dr = csv.DictReader(infile, dialect=dialect)
            for row in dr:
                final_dict = _dict_flat_to_nested(
                    row, defaults=fields_dict)
                added.append(okta_manager.add_user(params, final_dict))
        return added
    # when creating directly, we don't :)
    else:
        final_dict = _dict_flat_to_nested(fields_dict)
        return okta_manager.add_user(params, final_dict)


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """
    Okta CLI helper.

    See subcommands for help: "okta-cli users --help" etc.

    If in doubt start with: "okta-cli config new --help"
    """
    pass


@cli.command(name="version", context_settings=CONTEXT_SETTINGS)
def cli_version():
    """Prints version number and exit"""
    print(VERSION)


cli.add_command(cli_config)
cli.add_command(cli_users)
cli.add_command(cli_pw)
cli.add_command(cli_groups)
cli.add_command(cli_apps)
