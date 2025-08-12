###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
########################################################################
"""DIRAC Basic Oracle Class It provides access to the basic Oracle methods in a
multithread-safe mode using oracledb connection pooling for connection reuse.

These are the coded methods:

__init__( user, passwd, tns, [maxQueueSize=100] )

Initializes the connection pool and tries to connect to the DB server.
"maxQueueSize" defines the maximum number of connections in the pool.


_except( methodName, exception, errorMessage )

Helper method for exceptions: the "methodName" and the "errorMessage"
are printed with ERROR level, then the "exception" is printed (with
full description if it is a Oracle Exception) and S_ERROR is returned
with the errorMessage and the exception.


_connect()

Creates the connection pool and sets the _connected flag to True upon success.
Returns S_OK or S_ERROR.


query( cmd, [conn] )

Executes SQL command "cmd".
Gets a connection from the pool (or uses the provided connection),
automatically returning it to the pool when done.
Returns S_OK with fetchall() out in Value or S_ERROR upon failure.


_getConnection()

Gets a connection from the pool.
Returns S_OK with connection in Value or S_ERROR
the calling method is responsible for closing this connection once it is no
longer needed.
"""
from contextlib import contextmanager

import oracledb
from oracledb import STRING as oracledb_STRING  # pylint: disable=no-name-in-module
from oracledb import NUMBER as oracledb_NUMBER  # pylint: disable=no-name-in-module

from DIRAC import gLogger
from DIRAC import S_OK, S_ERROR
from DIRAC.Core.Utilities.ReturnValues import DReturnType


gInstancesCount = 0
gModeFixed = False

maxConnectRetry = 100
maxArraysize = 5000  # max allowed


class OracleDB:
    """Basic multithreaded DIRAC Oracle Client Class."""

    def __init__(
        self, userName, password="", tnsEntry="", confDir="", mode="", maxQueueSize=100, call_timeout_ms=None, **kwargs
    ):
        """set Oracle connection parameters and try to connect."""
        global gInstancesCount
        gInstancesCount += 1

        self.__initialized = False
        self._connected = False
        self.call_timeout_ms = call_timeout_ms

        if "logger" not in dir(self):
            self.logger = gLogger.getSubLogger("Oracle")

        # let the derived class decide what to do with if is not 1
        self._threadsafe = oracledb.threadsafety
        self.logger.debug(f"thread_safe = {self._threadsafe}")

        self.__checkQueueSize(maxQueueSize)

        self.__connect_kwargs = kwargs | dict(
            user=userName,
            password=password,
            dsn=tnsEntry,
            config_dir=confDir,
        )
        self.__mode = mode
        self.__maxQueueSize = maxQueueSize
        self.__pool = None

        self.__initialized = True
        self._connect()

        if not self._connected:
            raise RuntimeError("Can not connect, exiting...")

        self.logger.info("===================== Oracle =====================")
        self.logger.info("User:           " + self.__connect_kwargs.get("user"))
        self.logger.info("TNS:            " + self.__connect_kwargs.get("dsn"))
        self.logger.info("Pool size:      " + str(maxQueueSize))
        self.logger.info("==================================================")

    def __del__(self):
        global gInstancesCount

        if self.__initialized and self.__pool:
            try:
                self.__pool.close()
                self.logger.debug("Connection pool closed")
            except Exception as e:
                self.logger.debug(f"Error closing connection pool: {e}")

    @staticmethod
    def __checkQueueSize(maxQueueSize):
        """the size of the connection pool is limited."""

        if maxQueueSize <= 0:
            raise Exception("OracleDB.__init__: maxQueueSize must positive")
        try:
            test = maxQueueSize - 1
        except TypeError:
            raise TypeError(f"OracleDB.__init__: wrong type for maxQueueSize {type(maxQueueSize)}")

    def _except(self, methodName, x, err):
        """print Oracle error or exeption return S_ERROR with Exception."""

        try:
            raise x
        except oracledb.Error as e:
            self.logger.error(f"{methodName}: {err}", str(e))
            return S_ERROR(f"{err}: ( {e} )")
        except Exception as x:
            self.logger.error(f"{methodName}: {err}", str(x))
            return S_ERROR(f"{err}: ({x})")

    def _connect(self):
        """create connection pool and set connected flag to True upon success."""
        self.logger.debug("_connect:", self._connected)
        if self._connected:
            return S_OK()

        self.logger.debug(
            "_connect: Attempting to create connection pool", f"for user {self.__connect_kwargs.get('user')}."
        )
        try:
            self.__createPool()
            self.logger.debug("_connect: Connection pool created.")
            self._connected = True
            return S_OK()
        except Exception as x:
            return self._except("_connect", x, "Could not create connection pool.")

    def query(self, cmd, conn=False, params=[], kwparams={}, pre_inserts=[]):
        """execute Oracle query command return S_OK structure with fetchall result
        as tuple it returns an empty tuple if no matching rows are found return
        S_ERROR upon error.

        Use of params and kwparams to pass bind variabes is strongly encouraged
        to prevent SQL injection and improve performance. See the python-oracledb
        documentation for more information.

        :param str cmd: the SQL string to be executed
        :param conn: the connection to use, optional
        :param list params: positional bind variables to pass to oracledb.Cursor.execute
        :param dict kwparams: named bind variables to pass to oracledb.Cursor.execute
        :param list pre_inserts: list of tuples with the query and data to be inserted before the main query
        :param call_timeout_ms: optional timeout in milliseconds for the query execution
        """
        self.logger.debug("query:", f"{cmd!r} {params!r} {kwparams!r}")

        with self.__getConnection(conn) as retDict:
            if not retDict["OK"]:  # pylint: disable=unsubscriptable-object
                return retDict
            connection = retDict["Value"]  # pylint: disable=unsubscriptable-object

            try:
                cursor = connection.cursor()
                cursor.arraysize = maxArraysize

                for pre_insert_query, pre_insert_data in pre_inserts:
                    self.logger.debug(
                        "query: Pre-inserting data into temp table", f"{pre_insert_query!r} {pre_insert_data!r}"
                    )
                    cursor.executemany(pre_insert_query, pre_insert_data)

                if cursor.execute(cmd, *params, **kwparams):
                    res = cursor.fetchall()
                else:
                    res = ()

                # Log the result limiting it to just 10 records
                if len(res) < 10:
                    self.logger.debug("query: Records returned", res)
                else:
                    self.logger.debug(
                        "query: First 10 records returned out of",
                        f"{len(res)}: {res[:10]} ...",
                    )

                retDict = S_OK(res)
            except Exception as x:
                self.logger.debug("query:", cmd)
                retDict = self._except("query", x, "Execution failed.")
                self.logger.debug("Start Rollback transaction")
                connection.rollback()
                self.logger.debug("End Rollback transaction")

            try:
                connection.commit()
                cursor.close()
            except Exception:
                pass

        return retDict

    def executeStoredProcedure(self, packageName, parameters, output=True, array=None, conn=False):
        """executes a stored procedure."""
        self.logger.debug("_query:", packageName + "(" + str(parameters) + ")")

        with self.__getConnection(conn) as retDict:
            if not retDict["OK"]:  # pylint: disable=unsubscriptable-object
                return retDict
            connection = retDict["Value"]  # pylint: disable=unsubscriptable-object

            try:
                cursor = connection.cursor()
                result = None
                results = None
                if array:
                    fArray = array[0]
                    if isinstance(fArray, str):
                        result = cursor.arrayvar(oracledb_STRING, array)
                        parameters += [result]
                    elif isinstance(fArray, int):
                        result = cursor.arrayvar(oracledb_NUMBER, array)
                        parameters += [result]
                    elif isinstance(fArray, list):
                        for i in array:
                            if isinstance(i, (bool, str, int)):
                                parameters += [i]
                            elif i:
                                if isinstance(i[0], str):
                                    result = cursor.arrayvar(oracledb_STRING, i)
                                    parameters += [result]
                                elif isinstance(i[0], int):
                                    result = cursor.arrayvar(oracledb_NUMBER, i)
                                    parameters += [result]
                                else:
                                    return S_ERROR("The array type is not supported!!!")
                            else:
                                result = cursor.arrayvar(oracledb_STRING, [], 0)
                                parameters += [result]
                    else:
                        return S_ERROR("The array type is not supported!!!")
                if output:
                    result = connection.cursor()
                    result.arraysize = maxArraysize  # 500x faster!!
                    parameters += [result]
                    cursor.callproc(packageName, parameters)
                    results = result.fetchall()
                else:
                    cursor.callproc(packageName, parameters)
                retDict = S_OK(results)
            except Exception as x:
                self.logger.debug("query:", packageName + "(" + str(parameters) + ")")
                retDict = self._except("query", x, "Execution failed.")
                connection.rollback()

            try:
                cursor.close()
            except Exception as ex:
                self._except("executeStoredProcedure:", ex, "Failed to close cursor")

        return retDict

    def executeStoredFunctions(self, packageName, returnType, parameters=None, conn=False):
        """executes a stored function."""
        if parameters is None:
            parameters = []
        with self.__getConnection(conn) as retDict:
            if not retDict["OK"]:  # pylint: disable=unsubscriptable-object
                return retDict
            connection = retDict["Value"]  # pylint: disable=unsubscriptable-object
            try:
                cursor = connection.cursor()
                cursor.arraysize = maxArraysize
                result = cursor.callfunc(packageName, returnType, parameters)
                retDict = S_OK(result)
            except Exception as x:
                self.logger.debug(f"_query: {packageName} ({parameters})")
                retDict = self._except("_query", x, "Execution failed.")
                connection.rollback()

            try:
                cursor.close()
            except Exception as ex:
                self._except("executeStoredFunctions:", ex, "Failed to close cursor")
        return retDict

    def __createPool(self):
        """Create a connection pool."""
        global gModeFixed
        self.logger.debug("__createPool:")
        if not gModeFixed:
            gModeFixed = True
            if self.__mode == "":
                try:
                    # Test connection in thin mode first
                    test_conn = oracledb.connect(**self.__connect_kwargs)
                    test_conn.close()
                except Exception as ex:
                    self.logger.exception()
                    self.logger.debug(f"Thin mode has failed: {ex}, we will try thick")
                    self.__mode = "Thick"
                else:
                    self.logger.debug("Using implicit thin mode")
            if self.__mode == "Thick":
                oracledb.init_oracle_client(config_dir=self.__connect_kwargs.get("config_dir"))
            self.logger.debug(f'Using {"thin" if oracledb.is_thin_mode() else "thick"} mode')

        self.__pool = oracledb.create_pool(
            min=1, max=self.__maxQueueSize, increment=1, timeout=120, **self.__connect_kwargs
        )
        self.logger.debug(f"Created connection pool with max {self.__maxQueueSize} connections")

    @contextmanager
    def __getConnection(self, conn=None) -> DReturnType:
        """Context manager to get a connection from the pool.

        If a connection is provided, it will be used instead of acquiring a new one."""
        self.logger.debug("__getConnection:")
        if conn:
            yield conn
            return

        if not self.__pool:
            return S_ERROR("Connection pool not initialized")

        try:
            with self.__pool.acquire() as connection:
                self.logger.debug("__getConnection: Got a connection from pool")
                if self.call_timeout_ms is not None:
                    orig_call_timeout = connection.call_timeout
                    connection.call_timeout = self.call_timeout_ms
                try:
                    yield S_OK(connection)
                finally:
                    if self.call_timeout_ms is not None:
                        connection.call_timeout = orig_call_timeout
        except Exception as x:
            yield self._except("__getConnection:", x, "Failed to get connection from pool")
