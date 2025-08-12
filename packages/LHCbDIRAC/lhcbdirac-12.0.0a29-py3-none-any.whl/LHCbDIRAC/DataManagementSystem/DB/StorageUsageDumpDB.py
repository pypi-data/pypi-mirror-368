###############################################################################
# (c) Copyright 2025 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import json
from datetime import datetime, timezone
from urllib.parse import quote_plus

from sqlalchemy import create_engine, Column, Integer, String, BigInteger, Boolean, text, delete, Engine, select, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.expression import and_, false, true

from DIRAC.ConfigurationSystem.Client.Utilities import getDBParameters
from DIRAC.Core.Base.DIRACDB import DIRACDB
from DIRAC.Core.Utilities.ReturnValues import returnValueOrRaise

# Define the SQLAlchemy model
Base = declarative_base()


class StorageSummary(Base):
    __tablename__ = "dump_storage_summary"

    SEName = Column(String(255), primary_key=True)
    SESize = Column(BigInteger)
    SEFiles = Column(BigInteger)
    SESite = Column(String(255))
    SEType = Column(String(255))
    IsDisk = Column(Boolean)


# Some folders are "duplicated", with case sensitivity issue
# PHYSICS / physics
# ALICE / alice
# +----------------------------------------+---+
# | Name                                   | t |
# +----------------------------------------+---+
# | /lhcb/data/2008/RAW/LHCb/PHYSICS/21188 | 2 |
# | /lhcb/data/2008/RAW/LHCb/PHYSICS/21192 | 2 |
# | /lhcb/data/2008/RAW/RICH2/ALICE/21933  | 2 |
# | /lhcb/data/2008/RAW/RICH2/ALICE/21936  | 2 |
# | /lhcb/data/2008/RAW/RICH2/ALICE/21937  | 2 |
# | /lhcb/data/2008/RAW/RICH2/ALICE/21938  | 2 |
# +----------------------------------------+---+
# that's why we need the specific mysql collate


class DirectoryMetadata(Base):
    __tablename__ = "dump_directory_metadata"

    Name = Column(String(255), primary_key=True)
    production = Column(Integer)
    filetype = Column(String(255))
    online_stream = Column(String(255))
    maybe_eventtype = Column(Integer)
    ConfigName = Column(String(255))
    ConfigVersion = Column(String(255))
    Description = Column(String(255))
    ProcPath = Column(String(255))
    EventTypeID = Column(Integer)

    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_bin"}


class StorageUsageDumpDB(DIRACDB):

    def __init__(self, *, url=None, parentLogger=None):
        self.fullname = self.__class__.__name__
        super().__init__(parentLogger=parentLogger)
        if url is None:
            param = returnValueOrRaise(getDBParameters("DataManagement/StorageUsageDB"))
            url = f"mysql://{param['User']}:{quote_plus(param['Password'])}@{param['Host']}:{param['Port']}/{param['DBName']}"

        self.engine = create_engine(
            url,
            echo=False,
            pool_recycle=30 * 60,
        )
        Base.metadata.create_all(self.engine)

    def directory_metadata_to_sql(self, df):
        with self.engine.connect() as conn:
            conn.execute(delete(DirectoryMetadata))

            df.to_sql(
                DirectoryMetadata.__tablename__,
                conn,
                index=False,
                method="multi",
                chunksize=10000,
                if_exists="append",
            )
            new_comment = json.dumps({"LastUpdate": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")})
            conn.execute(text(f"ALTER TABLE {DirectoryMetadata.__tablename__} COMMENT = '{new_comment}';"))

    def get_storage_summary_last_update(self) -> datetime:
        with self.engine.connect() as conn:
            comment = conn.execute(text(f"SHOW TABLE STATUS WHERE name = '{StorageSummary.__tablename__}';")).one()[-1]
            return datetime.strptime(json.loads(comment)["LastUpdate"], "%Y-%m-%d %H:%M:%S")

    def storage_summary_to_sql(self, df):
        with self.engine.connect() as conn:
            conn.execute(delete(StorageSummary))
            df.to_sql(
                StorageSummary.__tablename__,
                conn,
                index=False,
                method="multi",
                chunksize=10000,
                if_exists="append",
            )
            new_comment = json.dumps({"LastUpdate": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")})
            conn.execute(text(f"ALTER TABLE {StorageSummary.__tablename__} COMMENT = '{new_comment}';"))

    def get_site_usage(self, site_name: str, *, tape: bool = True, disk: bool = True) -> tuple[int, datetime]:
        """
        Retrieves the total storage usage and the last update time for a given site.

        Parameters:
        site_name (str): The name of the site for which to retrieve the storage usage.
        tape (bool): Flag indicating whether to include tape storage in the calculation. Default is True.
        disk (bool): Flag indicating whether to include disk storage in the calculation. Default is True.

        Returns:
        tuple[int, datetime]: A tuple containing the total storage size in bytes and the last update time.
        """
        with self.engine.connect() as conn:
            whereConditions = [StorageSummary.SESite == site_name]
            if tape and not disk:
                whereConditions.append(StorageSummary.IsDisk == false())
            elif disk and not tape:
                whereConditions.append(StorageSummary.IsDisk == true())
            query = select(func.sum(StorageSummary.SESize)).where(and_(*whereConditions))
            size_scal = conn.execute(query).scalar()
            if size_scal is None:
                raise ValueError(f"No such site {site_name}")
            size = int(size_scal)
            last_update = self.get_storage_summary_last_update()
            # Execute the query
            return (size, last_update)

    def get_se_usage(self, se_name: str) -> tuple[int, datetime]:
        """
        Retrieves the total storage usage and the last update time for a given site.

        Parameters:
        site_name (str): The name of the se for which to retrieve the storage usage.

        Returns:
        tuple[int, datetime]: A tuple containing the total storage size in bytes and the last update time.
        """
        with self.engine.connect() as conn:
            query = select(StorageSummary.SESize).where(StorageSummary.SEName == se_name)
            size_scal = conn.execute(query).scalar()
            if size_scal is None:
                raise ValueError(f"No such se {se_name}")
            size = int(size_scal)
            last_update = self.get_storage_summary_last_update()
            return (size, last_update)
