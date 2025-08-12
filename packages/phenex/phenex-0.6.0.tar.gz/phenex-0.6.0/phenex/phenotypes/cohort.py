from typing import List, Dict, Optional
from phenex.phenotypes.phenotype import Phenotype
import ibis
from ibis.expr.types.relations import Table
from phenex.tables import PhenotypeTable
from phenex.phenotypes.functions import hstack
from phenex.reporting import Table1
from phenex.util import create_logger
from concurrent.futures import ThreadPoolExecutor

logger = create_logger(__name__)


def subset_and_add_index_date(tables: Dict[str, Table], index_table: PhenotypeTable):
    subset_tables = {}
    for key, table in tables.items():
        columns = list(set(["INDEX_DATE"] + table.columns))
        subset_tables[key] = type(table)(
            table.inner_join(index_table, "PERSON_ID").select(columns)
        )
    return subset_tables


class Cohort(Phenotype):
    """
    The Cohort class represents a cohort of individuals based on specified entry criteria,
    inclusions, exclusions, and baseline characteristics. It extends the Phenotype class.

    Parameters:
        name: A descriptive name for the cohort.
        entry_criterion: The phenotype used to define index date for the cohort.
        inclusions: A list of phenotypes that must evaluate to True for patients to be included in the cohort.
        exclusions: A list of phenotypes that must evaluate to False for patients to be included in the cohort.
        characteristics: A list of phenotypes representing baseline characteristics of the cohort to be computed for all patients passing the inclusion and exclusion criteria.
        outcomes: A list of phenotypes representing outcomes of the cohort.

    Attributes:
        table (PhenotypeTable): The resulting index table after filtering (None until execute is called)
        inclusions_table (Table): The patient-level result of all inclusion criteria calculations (None until execute is called)
        exclusions_table (Table): The patient-level result of all exclusion criteria calculations (None until execute is called)
        characteristics_table (Table): The patient-level result of all baseline characteristics caclulations. (None until execute is called)
        outcomes_table (Table): The patient-level result of all outcomes caclulations. (None until execute is called)
        subset_tables_entry (Dict[str, PhenexTable]): Tables that have been subset by those patients satisfying the entry criterion.
        subset_tables_index (Dict[str, PhenexTable]): Tables that have been subset by those patients satisfying the entry, inclusion and exclusion criteria.
    """

    table = None

    def __init__(
        self,
        entry_criterion: Phenotype,
        inclusions: Optional[List[Phenotype]] = None,
        exclusions: Optional[List[Phenotype]] = None,
        characteristics: Optional[List[Phenotype]] = None,
        derived_tables: Optional[List["DerivedTable"]] = None,
        outcomes: Optional[List[Phenotype]] = None,
        **kwargs,
    ):
        super(Cohort, self).__init__(**kwargs)
        self.entry_criterion = entry_criterion
        self.inclusions = inclusions if inclusions is not None else []
        self.exclusions = exclusions if exclusions is not None else []
        self.characteristics = characteristics if characteristics is not None else []
        self.outcomes = outcomes if outcomes is not None else []
        self.index_table = None
        self.exclusions_table = None
        self.inclusions_table = None
        self.characteristics_table = None
        self.outcomes_table = None
        self.derived_tables = derived_tables
        self.children = (
            [entry_criterion]
            + self.inclusions
            + self.exclusions
            + self.characteristics
            + self.outcomes
        )
        self._table1 = None
        logger.info(
            f"Cohort '{self.name}' initialized with entry criterion '{self.entry_criterion.name}'"
        )

    def execute(
        self,
        tables: Dict[str, Table],
        con: "SnowflakeConnector" = None,
        write_subset_tables=False,
        overwrite: bool = False,
        n_threads: int = 1,
    ) -> PhenotypeTable:
        """
        The execute method executes the full cohort in order of computation. The order is entry criterion -> inclusion -> exclusion -> baseline characteristics. Tables are subset at two points, after entry criterion and after full inclusion/exclusion calculation to result in subset_entry data (contains all source data for patients that fulfill the entry criterion, with a possible index date) and subset_index data (contains all source data for patients that fulfill all in/ex criteria, with a set index date). Additionally, default reporters are executed such as table 1 for baseline characteristics.

        Args:
            tables (Dict[str, Table]): A dictionary of table names to Table objects.
            con (SnowflakeConnector, optional): A connection to Snowflake. Defaults to None. If passed, will write entry, inclusions, exclusions, index, characteristics and outcomes tables.
            write_subset_tables (bool, optional): Whether to write subset tables (subset-entry and subset-index) in addition to the standard intermediate tables.
            overwrite (bool, optional): Whether to overwrite existing tables when writing to disk.
            n_threads (int, optional): Number of threads to use for parallel execution. Defaults to 1.

        Returns:
            PhenotypeTable: The index table corresponding the cohort.
        """
        logger.info(f"Executing cohort '{self.name}' with {n_threads} threads...")
        # Compute entry criterion
        logger.debug("Computing entry criterion ...")
        self.entry_criterion.execute(tables)
        if con:
            logger.debug("Writing entry table ...")
            self.entry_criterion.table = con.create_table(
                self.entry_criterion.table, f"{self.name}__entry", overwrite=overwrite
            )

        logger.debug("Entry criterion computed.")
        index_table = self.entry_criterion.table.mutate(INDEX_DATE="EVENT_DATE")

        self.subset_tables_entry = subset_and_add_index_date(tables, index_table)
        if write_subset_tables:
            logger.debug("Writing subset entry tables ...")
            with ThreadPoolExecutor(max_workers=n_threads) as executor:
                futures = {}
                for key, table in self.subset_tables_entry.items():
                    futures[key] = executor.submit(
                        con.create_table,
                        table.table,
                        f"{self.name}__subset_entry_{key}".upper(),
                        overwrite,
                    )
                for key, future in futures.items():
                    self.subset_tables_entry[key] = type(self.subset_tables_entry[key])(
                        future.result()
                    )

        self.subset_tables_entry = self.derive_tables(
            self.subset_tables_entry, index_table, con, overwrite=overwrite
        )

        # Apply inclusions if any
        if self.inclusions:
            logger.debug("Applying inclusions ...")
            self._compute_inclusions_table(n_threads)
            if con:
                logger.debug("Writing inclusions table ...")
                self.inclusions_table = con.create_table(
                    self.inclusions_table,
                    f"{self.name}__inclusions".upper(),
                    overwrite=overwrite,
                )
            include = self.inclusions_table.filter(
                self.inclusions_table["BOOLEAN"] == True
            ).select(["PERSON_ID"])
            index_table = index_table.inner_join(include, ["PERSON_ID"])
            logger.debug("Inclusions applied.")

        # Apply exclusions if any
        if self.exclusions:
            logger.debug("Applying exclusions ...")
            self._compute_exclusions_table(n_threads)
            if con:
                logger.debug("Writing exclusions table ...")
                self.exclusions_table = con.create_table(
                    self.exclusions_table,
                    f"{self.name}__exclusions".upper(),
                    overwrite=overwrite,
                )
            exclude = self.exclusions_table.filter(
                self.exclusions_table["BOOLEAN"] == False
            ).select(["PERSON_ID"])
            index_table = index_table.inner_join(exclude, ["PERSON_ID"])
            logger.debug("Exclusions applied.")

        self.index_table = index_table
        if con:
            logger.debug("Writing index table ...")
            self.index_table = con.create_table(
                index_table, f"{self.name}__index".upper(), overwrite=overwrite
            )

        self.subset_tables_index = subset_and_add_index_date(
            self.subset_tables_entry, self.index_table.select("PERSON_ID")
        )
        if write_subset_tables:
            logger.debug("Writing subset index tables ...")
            with ThreadPoolExecutor(max_workers=n_threads) as executor:
                futures = {}
                for key, table in self.subset_tables_index.items():
                    futures[key] = executor.submit(
                        con.create_table,
                        table.table,
                        f"{self.name}__subset_index_{key}".upper(),
                        overwrite,
                    )
                for key, future in futures.items():
                    self.subset_tables_index[key] = type(self.subset_tables_index[key])(
                        future.result()
                    )
            logger.debug("Finished writing subset index tables ...")

        if self.characteristics:
            logger.debug("Computing characteristics ...")
            self._compute_characteristics_table(n_threads)
            if con:
                logger.debug("Writing characteristics table ...")
                self.characteristics_table = con.create_table(
                    self.characteristics_table,
                    f"{self.name}__characteristics".upper(),
                    overwrite=overwrite,
                )
            logger.debug("Characteristics computed.")
            _ = self.table1

        if self.outcomes:
            logger.debug("Computing outcomes ...")
            self._compute_outcomes_table(n_threads)
            logger.debug("Outcomes computed.")

        logger.info(f"Cohort '{self.name}' execution completed.")
        return index_table

    def _compute_inclusions_table(self, n_threads: int) -> Table:
        logger.debug("Computing inclusions table")
        """
        Compute the inclusions table from the individual inclusions phenotypes.
        Meant only to be called internally from execute() so that all dependent phenotypes
        have already been computed.

        Returns:
            Table: The join of all inclusion phenotypes together with a single "BOOLEAN"
            column that is the logical AND of all individual inclusion phenotypes
        """
        # create an inex table;
        # rows are persons that fulfill the entry criterion
        # columns are inclusion criteria with true of false if that column pt criteria are fulfilled
        inclusions_table = self._compute_inex_table(self.inclusions, n_threads)

        # create the final boolean inclusion column
        # this is true only if all inclusion criteria are true
        inclusions_table = inclusions_table.mutate(
            BOOLEAN=ibis.least(
                *[inclusions_table[f"{x.name}_BOOLEAN"] for x in self.inclusions]
            )
        )
        self.inclusions_table = inclusions_table
        logger.debug("Inclusions table computed")
        return self.inclusions_table

    def _compute_exclusions_table(self, n_threads: int) -> Table:
        logger.debug("Computing exclusions table")
        """
        Compute the exclusions table from the individual exclusions phenotypes.

        Returns:
            Table: The join of all exclusions phenotypes together with a single "BOOLEAN"
            column that is the logical OR of all individual inclusion phenotypes
        """
        # create an inex table;
        # rows are persons that fulfill the entry criterion
        # columns are inclusion criteria with true of false if fulfill
        exclusions_table = self._compute_inex_table(self.exclusions, n_threads)

        # create the boolean inclusions column
        # this is true only if all inclusions criteria are true
        exclusions_table = exclusions_table.mutate(
            BOOLEAN=ibis.greatest(
                *[exclusions_table[f"{x.name}_BOOLEAN"] for x in self.exclusions]
            )
        )
        self.exclusions_table = exclusions_table
        logger.debug("Exclusions table computed")
        return self.exclusions_table

    def _compute_inex_table(
        self, phenotypes: List["Phenotype"], n_threads: int
    ) -> Table:
        logger.debug("Computing inex table")
        """
        Compute the exclusion table from the individual exclusion phenotypes.

        Returns:
            Table: The join of all inclusion phenotypes together with a single "BOOLEAN"
            column that is the logical AND of all individual inclusion phenotypes
        """
        inex_table = self.entry_criterion.table.select(["PERSON_ID"])
        # execute all phenotypes and join the boolean column only
        with ThreadPoolExecutor(max_workers=n_threads) as executor:
            futures = [
                executor.submit(pt.execute, self.subset_tables_entry)
                for pt in phenotypes
            ]
            for future in futures:
                future.result()
        for pt in phenotypes:
            pt_table = pt.table.select(["PERSON_ID", "BOOLEAN"]).rename(
                **{
                    f"{pt.name}_BOOLEAN": "BOOLEAN",
                }
            )
            inex_table = inex_table.left_join(pt_table, ["PERSON_ID"])
            columns = inex_table.columns
            columns.remove("PERSON_ID_right")
            inex_table = inex_table.select(columns)

        # fill all nones with False
        boolean_columns = [col for col in inex_table.columns if "BOOLEAN" in col]
        for col in boolean_columns:
            inex_table = inex_table.mutate({col: inex_table[col].fill_null(False)})
        logger.debug("Inex table computed")
        return inex_table

    def _compute_characteristics_table(self, n_threads: int) -> Table:
        logger.debug("Computing characteristics table")
        """
        Retrieves and joins all characteristic tables.
        Meant only to be called internally from _execute() so that all dependent phenotypes
        have already been computed.

        Returns:
            Table: The join of all characteristic tables.
        """
        with ThreadPoolExecutor(max_workers=n_threads) as executor:
            futures = [
                executor.submit(c.execute, self.subset_tables_index)
                for c in self.characteristics
            ]
            for future in futures:
                future.result()
        self.characteristics_table = hstack(
            self.characteristics,
            join_table=self.index_table.select(["PERSON_ID", "INDEX_DATE"]),
        )
        logger.debug("Characteristics table computed")
        return self.characteristics_table

    def _compute_outcomes_table(self, n_threads: int) -> Table:
        logger.debug("Computing outcomes table")
        """
        Retrieves and joins all outcome tables. Meant only to be called internally from execute() so that all dependent phenotypes have already been computed.

        Returns:
            Table: The join of all outcome tables.
        """
        with ThreadPoolExecutor(max_workers=n_threads) as executor:
            futures = [
                executor.submit(o.execute, self.subset_tables_index)
                for o in self.outcomes
            ]
            for future in futures:
                future.result()
        self.outcomes_table = hstack(
            self.outcomes,
            join_table=self.index_table.select(["PERSON_ID", "INDEX_DATE"]),
        )
        logger.debug("Outcomes table computed")
        return self.outcomes_table

    @property
    def table1(self):
        if self._table1 is None:
            logger.debug("Generating Table1 report ...")
            reporter = Table1()
            self._table1 = reporter.execute(self)
            logger.debug("Table1 report generated.")
        return self._table1

    def derive_tables(self, tables, index_table, con, overwrite=False):
        if self.derived_tables is None:
            return tables
        for derived_table in self.derived_tables:
            logger.info(f"Deriving table {derived_table.dest_domain}")
            # derive the table
            table = derived_table.execute(
                tables=tables,
            )
            # join on index table to get index date
            columns = ["INDEX_DATE"] + table.columns
            table = type(table)(
                table.inner_join(index_table, "PERSON_ID").select(columns)
            )

            if con:
                logger.info(
                    f"Saving derived table {self.name}__subset_entry_{derived_table.dest_domain}"
                )
                table_name = f"{self.name}__subset_entry_{derived_table.dest_domain}"
                tables[derived_table.dest_domain] = type(table)(
                    con.create_table(table, table_name, overwrite=overwrite)
                )
            else:
                tables[derived_table.dest_domain] = table
        return tables
