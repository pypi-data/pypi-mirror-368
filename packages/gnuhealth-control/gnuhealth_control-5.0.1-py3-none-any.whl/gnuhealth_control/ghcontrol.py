# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>      #
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org> #
#                                                                           #
# SPDX-License-Identifier: GPL-3.0-or-later                                 #
#############################################################################
#   Hospital Management Information System (HMIS) component of the          #
#                       GNU Health project                                  #
#                   https://www.gnuhealth.org                               #
#############################################################################
#                               ghcontrol.py                                #
#############################################################################

from datetime import datetime
from curses import wrapper, panel
from venv import EnvBuilder
from shutil import copy
from importlib.metadata import distributions

import argparse
import curses
import os
import re
import subprocess
import psutil
import string
import random

# ghcontrol version shares release major and minor numbers with GH HIS.
VERSION = "5.0.1"  # gnuheath-control version
MIN_VER = '>=5.0.0a1,<5.1'  # Initial gnuhealth server package version
TRYTON_PINNING = '>=7.0,<7.1'   # Pin the tryton packages to this range

""" GNU Health control limits the health packages to the official ones
    for a particular release
"""

HEALTH_PACKAGES = [
    "archives", "caldav", "calendar", "contact-tracing", "crypto",
    "crypto-lab", "dentistry", "disability", "ems", "federation", "genetics",
    "genetics-uniprot", "gyneco", "history", "icd10", "icd10pcs", "icd11",
    "icd9procs", "icpm", "icu", "imaging", "imaging-worklist", "inpatient",
    "inpatient-calendar", "insurance", "iss", "lab", "lifestyle", "mdg6",
    "ntd", "ntd-chagas", "ntd-dengue", "nursing", "ophthalmology", "orthanc",
    "pediatrics", "pediatrics-growth-charts", "pediatrics-growth-charts-who",
    "qrcodes", "reporting", "services", "services-imaging", "services-lab",
    "socioeconomics", "stock", "stock-inpatient", "stock-nursing",
    "stock-surgery", "surgery", "surgery-protocols", "webdav3-server",
    "who-essential-medicines"]


def log_window():
    winlen = 45
    x = int(curses.COLS/2 - winlen/2)
    logwin = curses.newwin(10, winlen, 2, x)
    logwin.box()
    curses.echo()
    return logwin


def show_logs(win, row, col, data, attr=None):
    win.addstr(row, col, data, attr)
    win.refresh()


def task_engine(task, window, row):
    task_name = task[0][0]
    args = task[0][1]
    tsk = task[1]

    task_str = f"Running {task_name} ..."
    show_logs(win=window, row=row, col=1, data=task_str, attr=0)
    window.refresh()

    rc = tsk(args)
    if rc == 0:
        attr = curses.color_pair(1) | curses.A_BOLD
        result = "[OK]"
    else:
        attr = curses.color_pair(2) | curses.A_BOLD
        result = "[ERROR]"
    col = 35
    show_logs(win=window, row=row, col=col, data=result, attr=attr)
    window.refresh()
    return rc


def get_timestamp():
    return datetime.now().strftime("%Y%m%d%H%M%S")


class Server:

    arguments = None

    def __init__(self, stdscr, arguments):
        self.arguments = arguments
        self.stdscr = stdscr

    def get_base_dir(self):
        basedir = self.arguments.basedir
        return basedir

    def get_his_dir(self):
        basedir = self.get_base_dir()
        major_minor = re.match(r'(^[0-9]+)\.([0-9]+)\.(.+$)', VERSION)
        rel = f"{major_minor[1]}{major_minor[2]}"
        release = self.arguments.release or rel
        his_dir = f"{basedir}/his-{release}"
        return his_dir

    def get_pip_cache_dir(self):
        basedir = self.get_base_dir()
        pip_cache_dir = f"{basedir}/cache/pip"
        return pip_cache_dir

    def setup_dirs(self):
        """ Creates the basic directory structure to hold GH HIS
            components
        """

        basedir = self.get_base_dir()
        his_dir = self.get_his_dir()
        pip_cache_dir = self.get_pip_cache_dir()

        try:
            # Create root directory
            os.makedirs(basedir)

            # Create pip cache directory
            os.makedirs(pip_cache_dir, exist_ok=True)

        except FileExistsError:  # Allow the basedir to exist
            pass

        try:
            # Create his directory
            os.mkdir(his_dir)

        except BaseException:
            return -1

        for subdir in ["etc", "log", "local", "attach", "backup"]:
            try:
                # Create subdirs
                os.mkdir(f"{his_dir}/{subdir}")
            except BaseException:
                return -1

        return 0

    def setup_virtualenv(self):
        """ Create the virtual environment
        """
        his_dir = self.get_his_dir()
        venvdir = f"{his_dir}/venv"
        ghvenv = EnvBuilder(system_site_packages=False, with_pip=True)

        try:
            ghvenv.create(env_dir=venvdir)
        except BaseException:
            return -1

        return 0

    def install_core(self):
        """ Install the core package ("gnuhealth")
            in the newly created virtual environment
        """
        his_dir = self.get_his_dir()
        pip_cache_dir = self.get_pip_cache_dir()
        npython = f"{his_dir}/venv/bin/python"

        """ The following vars will only be used in development
        """
        pre = self.arguments.pre
        test_repo = "https://test.pypi.org/simple/"
        extra_index = "https://pypi.org/simple/"
        deplog = f"{his_dir}/log/install_deps.log"
        with open(deplog, "w") as logfile:
            if (self.arguments.test):
                process = [
                    npython, '-m', 'pip', 'install', '-i', test_repo,
                    '--extra-index-url', extra_index,
                    '--cache-dir', pip_cache_dir,
                    '--upgrade', f"gnuhealth{MIN_VER}"]
            else:
                process = [
                  npython, '-m', 'pip', 'install', '--cache-dir',
                  pip_cache_dir, '--upgrade',
                  f"gnuhealth{MIN_VER}"]

            if pre:
                process.append('--pre')  # Append pip pre-release argument

            try:
                subprocess.run(process, stdout=logfile, stderr=logfile)

            except BaseException:
                return -1

        return 0

    def check_config_dir(self):
        his_dir = self.get_his_dir()
        etc_dir = f"{his_dir}/etc"

        if os.path.exists(etc_dir) and os.path.isdir(etc_dir):
            return 0
        else:
            return -1

    def gnuhealthrc(self):
        """ Generate the gnuhealthrc profile.
            We explicitly set the virtual environment (VIRTUAL_ENV)
            and path so no need to source 'activate' script
            Set aliases and editor for interactive sessions
            For non-interactive sessions there are also the following
            scripts:
            * start_gnuhealth
            * editconf
            * ghis_env
        """
        his_dir = self.get_his_dir()
        venvdir = f"{his_dir}/venv"
        trytond_cfg = f"{his_dir}/etc/trytond.conf"
        trytond_log_conf = f"{his_dir}/etc/server_log.conf"

        ghrc = f'{his_dir}/etc/gnuhealthrc'
        self.create_bash_wrap(
            file_name="etc/gnuhealthrc",
            executable=False,
            need_backup=True,
            file_content=f"""\
export VIRTUAL_ENV={venvdir}
export PATH={his_dir}:{venvdir}/bin:$PATH
export TRYTOND_CONFIG={trytond_cfg}
export TRYTOND_LOGGING_CONFIG={trytond_log_conf}
export GNUHEALTH_HIS_BASE={his_dir}

alias cdlogs='cd {his_dir}/log'
alias cdbase='cd {his_dir}'

# Avoid accidental execution of rm, mv or cp
alias | grep rm= &> /dev/null || alias rm='rm -i'
alias | grep mv= &> /dev/null || alias mv='mv -i'
alias | grep cp= &> /dev/null || alias cp='cp -i'
""")

        ghenv = f'{his_dir}/ghis_env'
        self.create_bash_wrap("ghis_env", f"""\
#!/usr/bin/env bash

[[ -f {venvdir}/bin/activate ]] && source {venvdir}/bin/activate
[[ -f {ghrc} ]] && source {ghrc}

export GNUHEALTH_ENV=1

exec \"$@\"
""")
        self.create_bash_wrap("start_gnuhealth", f"""\
#!/usr/bin/env bash

{ghenv} trytond \"$@\"
""")

        self.create_bash_wrap("editconf", f"""\
#!/usr/bin/env bash

if command -v nano &> /dev/null; then
    export EDITOR=nano
else
    export EDITOR=vi
fi

$EDITOR {trytond_cfg} \"$@\"
""")

        self.modify_bashrc(ghrc)

        return 0

    def create_bash_wrap(self, file_name, file_content,
                         executable=True,
                         need_backup=False):
        his_dir = self.get_his_dir()
        file_path = f'{his_dir}/{file_name}'
        timestamp = self.get_timestamp()

        if need_backup:
            file_backup = f"{file_path}.back-{timestamp}"
            if os.path.isfile(file_path):
                copy(file_path, file_backup)

        with open(file_path, "w") as f:
            file_content = file_content
            f.write(file_content)
            if executable:
                os.chmod(file_path, 0o755)

    def get_timestamp(self):
        return datetime.now().strftime("%Y%m%d%H%M%S")

    def modify_bashrc(self, ghrc):
        home = os.environ['HOME']
        bashrc = f"{home}/.bashrc"
        timestamp = self.get_timestamp()
        bashrc_back = f"{home}/.bashrc.back-{timestamp}"

        if not self.arguments.ignore_bashrc:
            if os.path.isfile(bashrc):
                copy(bashrc, bashrc_back)  # Make a backup of bashrc
            self.modify_bashrc_gnuhealth_section(
                bashrc, f"[[ -f {ghrc} ]] && source {ghrc}")

        # --update-config will also update $HOME/.bashrc
        if (self.arguments.update_config
                and self.arguments.ignore_bashrc):
            if os.path.isfile(bashrc):
                copy(bashrc, bashrc_back)  # Make a backup of bashrc
            self.modify_bashrc_gnuhealth_section(bashrc, "")

    def modify_bashrc_gnuhealth_section(self, file_path, content):

        start_marker = "### GNUHEALTH_BEGIN_SETTING ###"
        end_marker = "### GNUHEALTH_END_SETTING ###"

        start_index = -1
        end_index = -1

        if os.path.isfile(file_path):  # Check for existance of the file
            with open(file_path, 'r') as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                if start_marker in line:
                    start_index = i
                if end_marker in line:
                    end_index = i

        if start_index == -1 or end_index == -1:
            with open(file_path, "a") as f:
                f.write(f'\n{start_marker}\n{content}\n{end_marker}\n')

        else:
            new_lines = lines[:start_index + 1] + \
                [content + "\n"] + lines[end_index:]

            with open(file_path, 'w') as f:
                f.writelines(new_lines)

    def trytond_cfg(self):
        """ Generate trytond.conf
            and server_log.conf
        """
        his_dir = self.get_his_dir()
        timestamp = self.get_timestamp()
        trytond_cfg = f"{his_dir}/etc/trytond.conf"
        trytond_cfg_back = f"{his_dir}/etc/trytond.conf.back-{timestamp}"

        trytond_log_conf = f"{his_dir}/etc/server_log.conf"
        trytond_log_conf_back = \
            f"{his_dir}/etc/server_log.conf.back-{timestamp}"

        if os.path.isfile(trytond_cfg):  # If the profile exists, make a backup
            copy(trytond_cfg, trytond_cfg_back)

        if os.path.isfile(trytond_log_conf):  # If it exists, make a backup
            copy(trytond_log_conf, trytond_log_conf_back)

        with open(trytond_cfg, "w") as trytondconf_file:
            file_content = f"""\
# Generated by gnuhealth-control
[database]
uri = postgresql://
path = {his_dir}/attach

[web]
# Listen to all network interfaces.
listen = 0.0.0.0:8000
"""
            trytondconf_file.write(file_content)

        with open(trytond_log_conf, "w") as logconf_file:
            file_content = f"""\
[formatters]
keys=simple

[handlers]
keys=rotate,console

[loggers]
keys=root

[formatter_simple]
format=[%(asctime)s] %(levelname)s:%(name)s:%(message)s
datefmt=%a %b %d %H:%M:%S %Y

[handler_rotate]
class=handlers.TimedRotatingFileHandler
args=('{his_dir}/log/his_server.log', 'D', 1, 30)
formatter=simple

[handler_console]
class=StreamHandler
formatter=simple
args=(sys.stdout,)

[logger_root]
level=WARNING
handlers=rotate,console
"""

            logconf_file.write(file_content)

        return 0

    def install_finished(self):
        return 0

    def do_task(self, task):
        """ Method to execute each of the tasks
            and get the result code
        """

        tsk = getattr(self, task)
        rc = tsk()
        return (rc)

    def setup(self):
        """ Installs a GNU Health HIS Server
        """
        if self.arguments.update_config:
            TASKS = ["check_config_dir", "gnuhealthrc",
                     "trytond_cfg", "install_finished"]
        else:
            TASKS = ["setup_dirs", "setup_virtualenv", "install_core",
                     "gnuhealthrc", "trytond_cfg", "install_finished"]
        logwin = log_window()
        row = 1

        for task in TASKS:
            if task == 'install_finished':
                task_str = "Installation successful"
                msg = "Please LOGOUT and re-login " \
                      "to activate the new environment"

                attr = curses.color_pair(3) | curses.A_BOLD
                x = int(curses.COLS/2 - len(msg)/2)
                msgwin = curses.newwin(4, len(msg)+1, 13, x)
                msgwin.addstr(2, 1, msg, attr)
                msgwin.refresh()

            else:
                task_str = f"Running {task} ..."
            show_logs(win=logwin, row=row, col=1, data=task_str, attr=0)
            logwin.refresh()
            rc = self.do_task(task)
            if rc == 0:
                attr = curses.color_pair(1) | curses.A_BOLD
                result = "[OK]"
            else:
                attr = curses.color_pair(2) | curses.A_BOLD
                result = "[ERROR]"
            col = 30
            show_logs(
                win=logwin, row=row, col=col, data=result, attr=attr)
            row = row + 1
            logwin.refresh()
            if rc != 0:
                break

    def start(self):
        """ Start the GNU Health HIS Tryton server
        """
        nenv = os.environ.copy()
        try:
            subprocess.Popen(
                ['trytond'], env=nenv, stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT)

        except BaseException:
            return -1

        GHControl.footer_window(self, self.stdscr)  # Refresh footer window
        return 0

    def stop(self):
        """ Stops the GNU Health HIS Tryton server
        """
        for proc in psutil.process_iter():
            # look for combinations that contain both python and trytond in
            # the same command line
            try:
                command_line = proc.cmdline()
            except psutil.ZombieProcess:
                pass

            if any("python" and "trytond" in args for args in command_line):
                proc.terminate()  # Gracefully ask to stop the server
                try:
                    proc.wait(timeout=5)
                except BaseException:  # If timeout, time to kill...
                    proc.kill()
                    proc.wait()

        GHControl.footer_window(self, self.stdscr)  # Refresh footer window
        return 0

    def status(self):
        """ Shows the status of the server
        """

        for proc in psutil.process_iter():
            # True if process contains python & trytond (
            # (eg, python ./trytond // python trytond ..)
            # We can evaluate other combinations, like when using gunicorn
            try:
                command_line = proc.cmdline()

            except psutil.ZombieProcess:
                pass
            except psutil.NoSuchProcess:
                pass

            if any("python" and "trytond" in args for args in command_line):
                return True
        return False

    def update(self):
        """ Updates to the latest compatible version the existing
            gnuhealth and tryton packages in the virtual environment
        """
        pip_cache_dir = self.get_pip_cache_dir()
        his_dir = self.get_his_dir()
        npython = f"{his_dir}/venv/bin/python"
        updatelog = f"{his_dir}/log/update.log"
        logfile = open(updatelog, "w")

        win = curses.newwin(10, 50, 3, 30)
        win.box()
        pkg_ok = True
        status = "System Package(s) Update OK"
        attr = curses.color_pair(1) | curses.A_BOLD

        for package in distributions():
            pkg = package.metadata["Name"]
            win.addstr(1, 2, "Updating....")
            x = 25 - int(len(pkg)/2)
            win.addstr(4, x, f"{pkg}", curses.A_BOLD)

            win.refresh()

            if ("tryton" in pkg or "gnuhealth" in pkg):
                if "tryton" in pkg:
                    pkg = f"{pkg}{TRYTON_PINNING}"
                else:
                    pkg = f"{pkg}{MIN_VER}"  # Get GNU Health packages

                process = [
                  npython, '-m', 'pip', 'install', '--cache-dir',
                  pip_cache_dir, '--upgrade',
                  pkg]

                try:
                    subprocess.check_call(
                        process, stdout=logfile, stderr=logfile)
                except BaseException:
                    pkg_ok = False

            win.refresh()
            win.clear()
            win.box()

        if not pkg_ok:
            attr = curses.color_pair(2) | curses.A_BOLD
            status = "[ERROR] Check logs"

        x = 25 - int(len(status)/2)
        win.addstr(4, x, status, attr)
        win.refresh()

    def add_package(self):
        """ Get the package name (without the gnuhealth prefix)
        """
        his_dir = self.get_his_dir()
        pip_cache_dir = self.get_pip_cache_dir()
        npython = f"{his_dir}/venv/bin/python"
        pkglog = f"{his_dir}/log/packages.log"

        # List the official GNU Health packages
        winwidth = 80
        x = int(curses.COLS/2 - winwidth/2)
        winlist = curses.newwin(12, winwidth, 13, x)
        winlist.box()
        winlist.addstr(1, 2, "Available packages:", curses.color_pair(1))
        row = 3
        col = 2

        for pkg in HEALTH_PACKAGES:
            if HEALTH_PACKAGES[-1] == pkg:
                pkg = f"{pkg}."
            else:
                pkg = f"{pkg}, "

            if col + len(pkg) < 80:
                winlist.addstr(row, col, pkg)
                col = col + len(pkg)
            else:
                col = 2
                row = row + 1
                winlist.addstr(row, col, pkg)
        winlist.refresh()

        win = curses.newwin(10, 50, 3, 30)
        win.box()
        curses.echo()
        curses.curs_set(1)
        win.addstr(2, 1, "Health package:")
        pkg = win.getstr(2, 20).decode()
        win.addstr(4, 1, f"{pkg} selected.")
        win.addstr(6, 1, "Install? (yes/no)")
        confirm = win.getstr(6, 20).decode()
        if (confirm != "yes"):
            return

        win.clear()
        win.refresh()
        win.box()

        if (pkg not in HEALTH_PACKAGES and pkg != "all"):
            win.addstr(4, 3, f"ERROR: {pkg} not in list")
            win.refresh()
            return

        """
            If we answer yes, use pip to install the selected package
        """

        curses.curs_set(0)

        logfile = open(pkglog, "w")

        if pkg == "all":
            packages = HEALTH_PACKAGES
        else:
            packages = [pkg]

        pkg_ok = True
        status = "Package(s) Installation OK"
        attr = curses.color_pair(1) | curses.A_BOLD
        for pkg in packages:
            pkg_pinning = f"{pkg}{MIN_VER}"  # Append version pinning
            win.addstr(1, 2, "Processing....")
            x = 25 - int(len(pkg)/2)
            win.addstr(4, x, f"{pkg}", curses.A_BOLD)

            win.refresh()

            process = [
              npython, '-m', 'pip', 'install', '--cache-dir',
              pip_cache_dir, '--upgrade',
              f"gnuhealth-{pkg_pinning}"]

            try:
                subprocess.check_call(
                    process, stdout=logfile, stderr=logfile)
            except BaseException:
                pkg_ok = False

            win.refresh()
            win.clear()
            win.box()

        if not pkg_ok:
            attr = curses.color_pair(2) | curses.A_BOLD
            status = "[ERROR] Check logs"

        x = 25 - int(len(status)/2)
        win.addstr(4, x, status, attr)
        win.refresh()


class Instance:

    arguments = None

    def __init__(self, stdscr, arguments):
        self.arguments = arguments
        self.his_base = os.environ.get('GNUHEALTH_HIS_BASE')

    def show_logs(self, win, row, col, data, attr=None):
        win.addstr(row, col, data, attr)
        win.refresh()

    def create_db(self, *args):
        """ Create database
        """
        dbname, = args[0]
        dblog = f"{self.his_base}/log/createdb.log"
        with open(dblog, "w") as logfile:
            try:
                subprocess.run(
                    ['createdb', dbname],
                    stdout=logfile, stderr=logfile)

            except BaseException:
                return -1
        return 0

    def create_instance(self, *args):
        """ Create Instance
        """
        dbname = args[0][0]
        email = args[0][1]
        password = args[0][2]
        fname = ''.join(random.choices(string.ascii_lowercase, k=5))
        tryton_pass = f"/tmp/.{fname}"
        with open(tryton_pass, "w") as pwfile:
            try:
                pwfile.write(password)
            except BaseException:
                os.remove(tryton_pass)  # Delete temp file
                return -1

        log = f"{self.his_base}/log/create_instance.log"
        tadmin = f"{self.his_base}/venv/bin/trytond-admin"

        """ Update the environment variables for this session
        """
        nenv = os.environ.copy()
        nenv['TRYTONPASSFILE'] = tryton_pass

        with open(log, "w") as logfile:
            try:
                subprocess.check_call(
                    [tadmin, '--database', dbname,
                     '--email', email, '--all', '-vv'],
                    env=nenv, stdout=logfile, stderr=logfile)
            except BaseException:
                os.remove(tryton_pass)
                return -1

        os.remove(tryton_pass)  # Delete temp file
        return 0

    def refresh_instance(self, *args):
        """ It updates all the modules
            executting trytond-admin --all
        """
        win = curses.newwin(10, 50, 3, 30)
        win.box()
        curses.echo()
        curses.curs_set(1)
        win.addstr(2, 1, "Instance Name:")
        dbname = win.getstr(2, 20).decode()
        curses.curs_set(0)
        win.addstr(4, 1, "Refreshing modules...")
        win.refresh()

        log = f"{self.his_base}/log/refresh_instance.log"
        tadmin = f"{self.his_base}/venv/bin/trytond-admin"

        """ Update the environment variables for this session
        """
        nenv = os.environ.copy()

        with open(log, "w") as logfile:
            try:
                # check_call to get the return code from trytond-admin
                subprocess.check_call(
                    [tadmin, '--database', dbname,
                     '--all', '-vv'],
                    env=nenv, stdout=logfile, stderr=logfile)
            except BaseException:
                attr = curses.color_pair(2) | curses.A_BOLD
                win.addstr(4, 25, "[ERROR]", attr)
                win.refresh()
                return -1

        attr = curses.color_pair(1) | curses.A_BOLD
        win.addstr(4, 25, "[OK]", attr)
        win.refresh()
        return 0

    def install_health_package(self, *args):
        """ Installs the health core package
        """
        dbname = args[0][0]

        log = f"{self.his_base}/log/install_health_package.log"
        tadmin = f"{self.his_base}/venv/bin/trytond-admin"

        """ Retrieve the environment variables for this session
        """
        nenv = os.environ.copy()

        with open(log, "w") as logfile:
            try:
                subprocess.check_call(
                    [tadmin, '--database', dbname,
                     '--update', 'health', '--activate-dependencies', '-vv'],
                    env=nenv, stdout=logfile, stderr=logfile)
            except BaseException:
                return -1

        return 0

    def import_countries(self, *args):
        """ Import countries
        """
        dbname = args[0][0]
        log = f"{self.his_base}/log/import_countries.log"
        imp_countries = f"{self.his_base}/venv/bin/trytond_import_countries"

        """ Load environment variables for this session
        """
        nenv = os.environ.copy()

        with open(log, "w") as logfile:
            try:
                subprocess.check_call(
                    [imp_countries, '--database', dbname],
                    env=nenv, stdout=logfile, stderr=logfile)
            except BaseException:
                return -1
        return 0

    def import_currencies(self, *args):
        """ Import currencies
        """
        dbname = args[0][0]
        log = f"{self.his_base}/log/import_currencies.log"
        imp_currencies = f"{self.his_base}/venv/bin/trytond_import_currencies"

        """ Load environment variables for this session
        """
        nenv = os.environ.copy()

        with open(log, "w") as logfile:
            try:
                subprocess.check_call(
                    [imp_currencies, '--database', dbname],
                    env=nenv, stdout=logfile, stderr=logfile)
            except BaseException:
                return -1
        return 0

    def backup(self):
        """ Make a backup of the database
        """
        timestamp = get_timestamp()

        win = curses.newwin(10, 50, 3, 30)
        win.box()
        curses.echo()
        curses.curs_set(1)
        win.addstr(2, 1, "Instance Name:")
        dbname = win.getstr(2, 20).decode()
        curses.curs_set(0)
        win.addstr(4, 1, "Backing up instance...")
        win.refresh()

        log = f"{self.his_base}/log/backup_instance.log"

        """ Update the environment variables for this session
        """
        nenv = os.environ.copy()

        bdest = f"{self.his_base}/backup/{dbname}-{timestamp}.sql"
        with open(log, "w") as logfile:
            try:
                # check_call to get the return code from trytond-admin
                subprocess.check_call(
                    ['pg_dump', '--dbname', dbname,
                     '--file', bdest],
                    env=nenv, stdout=logfile, stderr=logfile)
            except BaseException:
                attr = curses.color_pair(2) | curses.A_BOLD
                win.addstr(4, 25, "[ERROR]", attr)
                win.refresh()
                return -1

        attr = curses.color_pair(1) | curses.A_BOLD
        win.addstr(4, 25, "[OK]", attr)
        win.refresh()
        return 0

    def command_successful(self, *args):
        return 0

    def new(self, dbname=None):
        """ Get the instance/db name, admin password and email
        """
        win = curses.newwin(10, 50, 3, 30)
        win.box()
        curses.echo()
        curses.curs_set(1)
        win.addstr(2, 1, "Instance Name:")
        db = win.getstr(2, 20).decode()
        win.addstr(3, 1, "Password:")
        password = win.getstr(3, 20).decode()
        win.addstr(4, 1, "email:")
        email = win.getstr(4, 20).decode()
        win.addstr(6, 1, "Ready? (yes/no)")
        confirm = win.getstr(6, 20).decode()
        if (confirm != "yes"):
            return

        """
            If we answer yes, go ahead with the instance creation
        """
        curses.curs_set(0)
        win.clear()
        win.refresh()
        logwin = log_window()
        logwin.refresh()

        """ TASKS is an list of tuples, each element containing
            the method and it's arguments
        """
        TASKS = [('create_db', [db]),
                 ('create_instance', [db, email, password]),
                 ('install_health_package', [db]),
                 ('import_countries', [db]),
                 ('import_currencies', [db]),
                 ('command_successful', []),
                 ]
        row = 0
        for task in TASKS:
            row = row + 1
            tsk = getattr(self, task[0])
            # Pass the string and the actual method as arguments
            rc = task_engine(task=(task, tsk), window=logwin, row=row)
            if rc != 0:
                break


class Help:

    def display():
        """ show the help window
        """
        pass


class MenuPanel:
    def __init__(self, entries, win, footer, title, leaf=False, action=None):
        curses.start_color()
        # Init color pairs
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # OK
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)  # ERROR
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # WARNING
        self.window = win
        self.window_title = title
        self.panel = panel.new_panel(self.window)
        self.panel.hide()
        self.footer = footer
        self.footer_panel = panel.new_panel(self.footer)
        self.leaf = leaf
        self.action = action
        panel.update_panels()

        self.position = 0
        self.entries = entries

    def centerx(self, msg):
        x = int(curses.COLS / 2) - int(len(msg) / 2)
        return x

    def menu(self):
        """ Show the menu of the specific section
        """
        self.window.clear()
        self.window.addstr(
            0, self.centerx(self.window_title), self.window_title)
        self.panel.top()
        self.panel.show()

        """ Main menu loop"""
        while True:
            self.window.refresh()
            curses.doupdate()
            for index, entry in enumerate(self.entries):
                if index == self.position:
                    mode = curses.A_REVERSE
                else:
                    mode = curses.A_NORMAL

                entry_desc = f"{index}: {entry[0]}"
                self.window.addstr(5 + index, 2, entry_desc, mode)

                self.window.hline(1, 0, curses.ACS_HLINE, curses.COLS)

            key = self.window.getch()

            if key == ord("\n"):  # Map the Enter key
                # Exec the method associated to the entry
                if not self.leaf:
                    if self.entries[self.position][1]:
                        self.entries[self.position][1]()
                else:
                    self.entries[self.position][1]()

            if key == ord("q"):
                break

            if key == ord("h"):
                Help.display()

            if key == curses.KEY_UP and self.position > 0:
                self.position = self.position - 1

            if (key == curses.KEY_DOWN
                    and self.position < len(self.entries) - 1):
                self.position = self.position + 1

            if chr(key).isnumeric():
                entry_nr = int(chr(key))
                if entry_nr in range(0, len(self.entries)):
                    self.position = int(chr(key))
                else:
                    # Out of range
                    self.menu_error()

        self.window.clear()
        self.panel.hide()
        panel.update_panels()
        curses.doupdate()

    def menu_error(self):
        curses.beep()


class GHControl:
    def __init__(self, stdscr, arguments):
        curses.curs_set(False)  # Disable cursor
        basedir = arguments.basedir

        self.win = self.main_window(stdscr)
        self.footer = self.footer_window(stdscr)
        server = Server(self, arguments=arguments)
        instance = Instance(self, arguments=arguments)
        installation_entries = [
            ("Start Installation", server.setup, arguments),]
        installation_section = MenuPanel(
            installation_entries, self.win, self.footer,
            f"GNU Health HIS Installation (basedir = {basedir})", leaf=True)

        update_entries = [
            ("Start Packages Update", server.update, arguments),]
        update_section = MenuPanel(
            update_entries, self.win, self.footer,
            "GNU Health HIS Packages Update", leaf=True)

        package_entries = [
            ("Add Health package", server.add_package, arguments),]
        package_section = MenuPanel(
            package_entries, self.win, self.footer,
            "GNU Health HIS Add Package", leaf=True)

        instance_entries = [
            ("New Instance", instance.new, arguments),]
        instance_section = MenuPanel(
            instance_entries, self.win, self.footer,
            "GNU Health Instance", leaf=True)

        refresh_entries = [
            ("Refresh Instance", instance.refresh_instance),]
        refresh_section = MenuPanel(
            refresh_entries, self.win, self.footer,
            "GNU Health Instance", leaf=True)

        backup_entries = [("DB Instance Backup", instance.backup),]
        backup_section = MenuPanel(
            backup_entries, self.win, self.footer, "Backup", leaf=True)

        startstop_entries = [
            ("Start GNU Health HIS", server.start),
            ("Stop Server", server.stop),
        ]
        startstop_section = MenuPanel(
            startstop_entries, self.win, self.footer,
            "Server start / stop", leaf=True)

        main_entries = [
            ("Install GNU Health HIS", installation_section.menu),
            ("Create a new DB instance", instance_section.menu),
            ("Add Health package", package_section.menu),
            ("Refresh DB instance", refresh_section.menu),
            ("Start / stop instance", startstop_section.menu),
            ("Update packages / dependencies", update_section.menu),
            ("Backup instance", backup_section.menu),
        ]

        main_section = MenuPanel(
            main_entries, self.win, self.footer,
            f"Welcome to GNU Health Control Center {VERSION}")

        main_section.menu()

    def main_window(self, stdscr):
        """ We'll define a main window
        """
        win = curses.newwin(curses.LINES - 5, curses.COLS, 0, 0)
        win.keypad(True)  # Need keypad to map KEY_[UP|DOWN]
        return win

    def footer_window(self, stdscr):
        """ A footer for helpers
        """
        footer = curses.newwin(5, curses.COLS, curses.LINES - 5, 0)
        footer.box()
        server_status = Server.status(self)

        if server_status:
            attr = curses.color_pair(1) | curses.A_BOLD
            status = "running"
        else:
            attr = curses.color_pair(3) | curses.A_BOLD
            status = "stopped"

        footer_status = "Server status:"
        footer_hlp = "Press 'q' to go back or exit"
        footer.addstr(
            1, int(curses.COLS / 2 - len(footer_status + status) / 2),
            footer_status)

        footer.addstr(
            1,
            int(
                curses.COLS / 2 - len(footer_status + status) / 2)
            + len(footer_status) + 1, status, attr)

        footer.addstr(3, int(curses.COLS / 2 - len(footer_hlp) / 2),
                      footer_hlp)

        footer.refresh()
        return footer


def cmdline_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-b', '--basedir', default='/opt/gnuhealth',
                        help="Base directory of installation for "
                             "the gnuhealth components\n"
                             "default=/opt/gnuhealth.")

    parser.add_argument('-r', '--release',
                        help="GNU Health release (major and minor numbers), "
                        "﻿It will affect the installation directory of his, "
                        "for example: his-50.")

    parser.add_argument('-i', '--ignore-bashrc', action="store_true",
                        help="Does not modify .bashrc, "
                        "﻿If users want to install different HIS versions. "
                        "If used, the  user should use '/path/to/ghis_env'\n "
                        "For example: "
                        "'/opt/gnuhealth/his-50/ghis_env trytond', "
                        "'/opt/gnuhealth/his-50/ghis_env trytond-admin', "
                        "'/opt/gnuhealth/his-50/ghis_env pip install pandas'")

    parser.add_argument('-u', '--update-config', action="store_true",
                        help="Updates configuration files, namely "
                        "tryton.cfg, gnuhealthrc and bashrc, during "
                        "the server installation process.")

    parser.add_argument('-t', '--test', action="store_true",
                        help="Test mode. Uses the repository "
                        "test.pypi.org ")

    parser.add_argument('-p', '--pre', action="store_true",
                        help="Use pre-release packages. Usually used in  "
                        "combination with --test")

    return parser.parse_args()


def main():
    arguments = cmdline_args()
    wrapper(GHControl, arguments)


if __name__ == "__main__":
    main()
