"""
holland.mysql.mysqldump.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

View auto-exclude support for mysqldump plugin
"""

import logging
import time
import codecs
from textwrap import dedent
from holland.version import __version__ as holland_version

LOG = logging.getLogger(__name__)

def generate_sqlfile_header(mysql):
    header = dedent(u'''
    -- Generated by Holland {holland_version}
    --
    -- Host: {host} Database:
    -- ------------------------------------------------------
    -- Server version: {server_version}

    /*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
    /*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
    /*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
    /*!40101 SET NAMES utf8 */;
    /*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
    /*!40103 SET TIME_ZONE='+00:00' */;
    /*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
    /*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
    /*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
    /*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
    ''').lstrip()

    version = mysql.var('version')
    return header.format(holland_version=holland_version,
                         server_version=version,
                         host=mysql.host_info())

def generate_sqlfile_footer(mysql):
    footer = dedent(u'''

    /*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
    /*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
    /*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
    /*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
    /*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
    /*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
    /*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
    /*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

    -- Dump completed on {timestamp}
    ''').rstrip()

    return footer.format(timestamp=time.strftime('%Y-%m-%d %H:%M:%S'))

def dump_and_exclude_invalid_views(output_path, defaults_file, information_schema):
    LOG.info("Discovering invalid views")
    databases = information_schema.databases()
    invalid_views = information_schema.broken_views
    show_create_view = information_schema.mysql.show_create_view
    invalid_view_count = 0
    with codecs.open(defaults_file, 'ab', encoding='utf8') as fileobj:
        with codecs.open(output_path, 'wb', encoding='utf8') as sqlf:
            LOG.info("Writing invalid view definitions to %s", sqlf.name)
            # start option file config section
            print >>fileobj, u"# Invalid views detected by holland"
            print >>fileobj, u"[mysqldump]"
            # output header for .sql file
            print >>sqlf, generate_sqlfile_header(information_schema.mysql)
            for schema_name in databases:
                LOG.debug(u"Checking %s for invalid views", schema_name)
                schema_header = False
                table_exclusions = []
                for table_schema, table_name, message in invalid_views(schema_name):
                    if not schema_header:
                        print >>sqlf, u"--"
                        print >>sqlf, u"-- Current Database: `%s`" % (schema_name)
                        print >>sqlf, u"--"
                        print >>sqlf
                        schema_header = True

                    LOG.info(u"Invalid view detected. Adding ignore-table=%s.%s: %s",
                             table_schema, table_name, message)
                    table_exclusions.append((table_schema + '.' + table_name))
                    print >>fileobj, u"ignore-table=%s.%s" % \
                                     (table_schema,table_name)
                    print >>sqlf, u"--"
                    print >>sqlf, u"-- Invalid View `%s`.`%s` : %s" % \
                                  (table_schema, table_name, message)
                    print >>sqlf, u"--"
                    try:
                        print >>sqlf, show_create_view(table_name, table_schema)
                    except:
                        LOG.info("View defintion retrieval failed.", exc_info=True)
                        print >>sqlf, "-- Failed to load invalid view definition"
                    print >>sqlf # newline
                    invalid_view_count += 1

                # XXX: this is a hack for file-per-table, so that
                # information_schema.tables() skips invalid views
                if table_exclusions:
                    from holland.mysql.schema import tablename_exclusion_filter
                    information_schema.add_table_filter(tablename_exclusion_filter(table_exclusions))
            print >>sqlf, generate_sqlfile_footer(information_schema.mysql)
    LOG.info("%d views excluded", invalid_view_count)
