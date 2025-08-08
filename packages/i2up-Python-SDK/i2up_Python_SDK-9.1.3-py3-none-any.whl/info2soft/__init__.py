# -*- coding: utf-8 -*-
'''
    info2soft Resource Storage SDK for Python
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    For detailed document, please see:
    <https://code.info2soft.com/web/sdk/python-sdk>
'''

# flake8: noqa

__version__ = 'v20181227'

from .config import set_default


from info2soft.common.Auth import Auth, RequestsAuth
from info2soft.common.DataBaseBackup import DataBaseBackup
from info2soft.common.Dir import Dir
from info2soft.common.GeneralInterface import GeneralInterface
from info2soft.common.Logs import Logs
from info2soft.common.Permission import Permission
from info2soft.common.Qr import Qr
from info2soft.common.Storage import Storage
from .common import Client


from info2soft.dashboard.v20181227.Dashboard import Dashboard


from info2soft.fsp.FspRecovery import FspRecovery
from info2soft.fsp.FspBackup import FspBackup
from info2soft.fsp.FspMove import FspMove


from info2soft.ha.v20181227.AppHighAvailability import AppHighAvailability


from info2soft.nas.v20190102.NAS import NAS


from info2soft.notifications.v20181227.Notifications import Notifications


from .rep.v20181227.RepBackup import RepBackup
from .rep.v20181227.RepRecovery import RepRecovery


from .resource.v20181227.Node import Node
from .resource.v20181227.Cluster import Cluster
from .resource.v20181227.BizGroup import BizGroup
from .resource import AppSystem

from .resource import BoxVm


from .system.v20181227.User import User
from .system.v20181227.Lic import Lic


from .timing.TimingBackup import TimingBackup
from .timing.TimingRecovery import TimingRecovery


from .tools.v20181227.Compare import Compare
from .tools.v20181227.Diagnose import Diagnose


from .vp.VirtualizationSupport import VirtualizationSupport

from .active import DataChk, Db2, Dm, Gauss, Hetero, Infomix, Log, Mask, MongoDB, Mysql, Node, Notifications
from .active import Postgres, QianBaseSync, QianBasexTP, ScriptMask, Sqlserver, Summary, SyncRules, Tidb
from .active import Oceanbase, OracleRule


from .ha import haCluster

from .cloud import CloudBackup, CloudVolume, CloudRehearse, CloudPlatform, CloudEcs

from .bigdata import bigDataRecovery, bigDataBackup

from .distributor import DistributorSystem, DistributorGroup, DistributorNode

from .cdm import Cdm

from .system import Credential