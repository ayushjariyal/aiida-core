# -*- coding: utf-8 -*-

from __future__ import absolute_import

from aiida.backends import settings
from aiida.backends.profile import load_profile
from aiida.common.exceptions import (
        ConfigurationError, AuthenticationError,
        InvalidOperation
    )


__copyright__ = u"Copyright (c), This file is part of the AiiDA platform. For further information please visit http://www.aiida.net/.. All rights reserved."
__license__ = "MIT license, see LICENSE.txt file"
__authors__ = "The AiiDA team."
__version__ = "0.6.0"


def is_dbenv_loaded():
    """
    Return True of the dbenv was already loaded (with a call to load_dbenv),
    False otherwise.
    """
    return settings.LOAD_DBENV_CALLED


def load_dbenv(process=None, profile=None, *args, **kwargs):
    if is_dbenv_loaded():
        raise InvalidOperation("You cannot call load_dbenv multiple times!")
    settings.LOAD_DBENV_CALLED = True

    # This is going to set global variables in settings, including
    # settings.BACKEND
    load_profile(process=process, profile=profile)

    if settings.BACKEND == "sqlalchemy":
        # Maybe schema version should be also checked for SQLAlchemy version.
        from aiida.backends.sqlalchemy.utils \
            import load_dbenv as load_dbenv_sqlalchemy
        return load_dbenv_sqlalchemy(
            process=process, profile=profile, *args, **kwargs)
    elif settings.BACKEND == "django":
        from aiida.backends.djsite.utils import load_dbenv as load_dbenv_django
        return load_dbenv_django(
            process=process, profile=profile, *args, **kwargs)
    else:
        raise ConfigurationError("Invalid settings.BACKEND: {}".format(
            settings.BACKEND))


def get_automatic_user():
    if settings.BACKEND == "sqlalchemy":
        from aiida.backends.sqlalchemy.utils import (
            get_automatic_user as get_automatic_user_sqla)
        return get_automatic_user_sqla()
    elif settings.BACKEND == "django":
        from aiida.backends.djsite.utils import (
            get_automatic_user as get_automatic_user_dj)
        return get_automatic_user_dj()
    else:
        raise ValueError("This method doesn't exist for this backend")


def get_workflow_list(*args, **kwargs):
    if settings.BACKEND == "sqlalchemy":
        raise ValueError("This method doesn't exist for this backend")
    elif settings.BACKEND == "django":
        from aiida.backends.djsite.cmdline import (
            get_workflow_list as get_workflow_list_dj)
        return get_workflow_list_dj(*args, **kwargs)
    else:
        raise ValueError("This method doesn't exist for this backend")


def get_log_messages(*args, **kwargs):
    if settings.BACKEND == "sqlalchemy":
        from aiida.backends.sqlalchemy.cmdline import (
            get_log_messages as get_log_messages_sqla)
        return get_log_messages_sqla(*args, **kwargs)
    elif settings.BACKEND == "django":
        from aiida.backends.djsite.cmdline import (
            get_log_messages as get_log_messages_dj)
        return get_log_messages_dj(*args, **kwargs)
    else:
        raise ValueError("This method doesn't exist for this backend")


def get_authinfo(computer, aiidauser):

    if settings.BACKEND == "django":
        from aiida.backends.djsite.db.models import DbComputer, DbAuthInfo

        try:
            authinfo = DbAuthInfo.objects.get(
                # converts from name, Computer or DbComputer instance to
                # a DbComputer instance
                dbcomputer=DbComputer.get_dbcomputer(computer),
                aiidauser=aiidauser)
        except ObjectDoesNotExist:
            raise AuthenticationError(
                "The aiida user {} is not configured to use computer {}".format(
                    aiidauser.email, computer.name))
        except MultipleObjectsReturned:
            raise ConfigurationError(
                "The aiida user {} is configured more than once to use "
                "computer {}! Only one configuration is allowed".format(
                    aiidauser.email, computer.name))
    elif settings.BACKEND == "sqlalchemy":
        from aiida.backends.sqlalchemy.models.authinfo import DbAuthInfo
        from aiida.backends.sqlalchemy import session
        from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
        try:
            authinfo = session.query(DbAuthInfo).filter_by(
                dbcomputer_id=computer.id,
                aiidauser_id=aiidauser.id,
            ).one()
        except NoResultFound:
            raise AuthenticationError(
                "The aiida user {} is not configured to use computer {}".format(
                    aiidauser.email, computer.name))
        except MultipleResultsFound:
            raise ConfigurationError(
                "The aiida user {} is configured more than once to use "
                "computer {}! Only one configuration is allowed".format(
                    aiidauser.email, computer.name))

    else:
        raise Exception("unknown backend {}".format(settings.BACKEND))
    return authinfo


def get_daemon_user():
    if settings.BACKEND == "django":
        from aiida.backends.djsite.utils import get_daemon_user as get_daemon_user_dj
        daemon_user = get_daemon_user_dj()
    elif settings.BACKEND ==  "sqlalchemy":
        from aiida.backends.sqlalchemy.utils import get_daemon_user as get_daemon_user_sqla
        daemon_user = get_daemon_user_sqla()
    return daemon_user
