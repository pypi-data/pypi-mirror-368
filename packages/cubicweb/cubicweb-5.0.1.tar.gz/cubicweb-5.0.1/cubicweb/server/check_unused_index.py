# copyright 2003-2022 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact https://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of CubicWeb.
#
# CubicWeb is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# CubicWeb is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with CubicWeb.  If not, see <https://www.gnu.org/licenses/>.
import os


def check_unused_index(cnx, min_usage=0):
    source = cnx.repo.system_source
    if source.dbdriver != "postgres":
        print("This command is only available for postgres.")
        return os.EX_UNAVAILABLE
    cursor = cnx.cnxset.cu
    cursor.execute(
        """
    SELECT
        s.relname AS tablename,
        s.indexrelname AS indexname,
        s.idx_scan AS indexusage,
        pg_size_pretty(pg_relation_size(s.indexrelid)) AS index_size,
        string_agg(a.attname, '|') as column_names
    FROM
        pg_catalog.pg_stat_all_indexes s
        JOIN pg_catalog.pg_index i ON s.indexrelid = i.indexrelid
        JOIN pg_attribute a ON (a.attnum = ANY(i.indkey) and i.indrelid = a.attrelid)
    WHERE
        s.idx_scan <= %(min_usage)s
        AND NOT EXISTS          -- does not enforce a constraint
        (
            SELECT 1 FROM pg_catalog.pg_constraint c
            WHERE c.conindid = s.indexrelid
        )
    GROUP BY s.relname, s.indexrelname, s.indexrelid, s.idx_scan
    ORDER BY pg_relation_size(s.indexrelid) DESC;
    """,
        {"min_usage": min_usage},
    )
    results = {
        "custom_indexes": [],
        "schema_indexes": [],
    }
    for tablename, index_name, index_size, column_names in cursor.fetchall():
        if not column_names:
            continue
        if index_name.startswith("pg_"):
            continue
        columns = column_names.split("|")
        if (
            not tablename.startswith("cw_")
            or len(columns) > 1
            or not column_names.startswith("cw_")
        ):
            # not an etype table
            results["custom_indexes"].append((tablename, index_name, index_size))
            continue
        etype = tablename[3:]
        attribute = column_names[3:]
        results["schema_indexes"].append((etype, attribute, index_size))
    if not (results["schema_indexes"] or results["schema_indexes"]):
        print("All indexes are used :)")
        return os.EX_OK
    if results["schema_indexes"]:
        print("Unused indexation in the schema:")
        for etype, attribute, size in results["schema_indexes"]:
            print(f"entity {etype.capitalize()}: attribute {attribute} (use {size})")
    if results["custom_indexes"]:
        print("Unused custom indexes:")
        for table, index_name, size in results["custom_indexes"]:
            print(f"table: {table}, index name: {index_name} (use {size})")
    return os.EX_OK
