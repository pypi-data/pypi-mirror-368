from typing import Union, List, Optional
from phenex.phenotypes.phenotype import Phenotype
from phenex.filters.codelist_filter import CodelistFilter
from phenex.filters.relative_time_range_filter import RelativeTimeRangeFilter
from phenex.filters.date_filter import DateFilter
from phenex.aggregators import First, Last
from phenex.codelists import Codelist
from phenex.tables import is_phenex_code_table, PHENOTYPE_TABLE_COLUMNS, PhenotypeTable
from phenex.phenotypes.functions import select_phenotype_columns
from ibis import _


class CodelistPhenotype(Phenotype):
    """
    CodelistPhenotype extracts patients from a CodeTable based on a specified codelist and other optional filters such as date range, relative time range and categorical filters.

    Parameters:
        domain: The domain of the phenotype.
        codelist: The codelist used for filtering.
        name: The name of the phenotype. Optional. If not passed, name will be derived from the name of the codelist.
        date_range: A date range filter to apply.
        relative_time_range: A relative time range filter or a list of filters to apply.
        return_date: Specifies whether to return the 'first', 'last', or 'nearest' event date. Default is 'first'.
        categorical_filter: Additional categorical filters to apply.

    Attributes:
        table (PhenotypeTable): The resulting phenotype table after filtering (None until execute is called)

    Examples:

    Example: Inpatient Atrial Fibrillation (OMOP)
        ```python
        from phenex.phenotypes import CodelistPhenotype
        from phenex.codelists import Codelist
        from phenex.mappers import OMOPDomains
        from phenex.filters import DateFilter, CategoricalFilter, Value
        from phenex.ibis_connect import SnowflakeConnector

        con = SnowflakeConnector() # requires some configuration
        mapped_tables = OMOPDomains.get_mapped_tables(con)

        af_codelist = Codelist([313217]) # list of concept ids
        date_range = DateFilter(
            min_date=After("2020-01-01"),
            max_date=Before("2020-12-31")
            )

        inpatient = CategoricalFilter(
            column_name='VISIT_DETAIL_CONCEPT_ID',
            allowed_values=[9201],
            domain='VISIT_DETAIL'
        )

        af_phenotype = CodelistPhenotype(
            name="af",
            domain='CONDITION_OCCURRENCE',
            codelist=af_codelist,
            date_range=date_range,
            return_date='first',
            categorical_filter=inpatient
        )

        af = af_phenotype.execute(mapped_tables)
        af.head()
        ```

    Example: Myocardial Infarction One Year Pre-index (OMOP)
        ```python
        from phenex.filters import RelativeTimeRangeFilter, Value

        af_phenotype = (...) # take from above example

        oneyear_preindex = RelativeTimeRangeFilter(
            min_days=Value('>', 0), # exclude index date
            max_days=Value('<', 365),
            anchor_phenotype=af_phenotype # use af phenotype above as reference date
            )

        mi_codelist = Codelist([49601007]) # list of concept ids
        mi_phenotype = CodelistPhenotype(
            name='mi',
            domain='CONDITION_OCCURRENCE',
            codelist=mi_codelist,
            return_date='first',
            relative_time_range=oneyear_preindex
        )
        mi = mi_phenotype.execute(mapped_tables)
        mi.head()
        ```
    """

    def __init__(
        self,
        domain: str,
        codelist: Codelist,
        name: Optional[str] = None,
        date_range: DateFilter = None,
        relative_time_range: Union[
            RelativeTimeRangeFilter, List[RelativeTimeRangeFilter]
        ] = None,
        return_date="first",
        categorical_filter: Optional["CategoricalFilter"] = None,
        **kwargs,
    ):
        if name is None:
            name = codelist.name
        super(CodelistPhenotype, self).__init__(name=name, **kwargs)

        self.codelist_filter = CodelistFilter(codelist)
        self.codelist = codelist
        self.categorical_filter = categorical_filter
        self.date_range = date_range
        self.return_date = return_date
        assert self.return_date in [
            "first",
            "last",
            "nearest",
            "all",
        ], f"Unknown return_date: {return_date}"
        self.table: PhenotypeTable = None
        self.domain = domain
        if isinstance(relative_time_range, RelativeTimeRangeFilter):
            relative_time_range = [relative_time_range]

        self.relative_time_range = relative_time_range
        if self.relative_time_range is not None:
            for rtr in self.relative_time_range:
                if rtr.anchor_phenotype is not None:
                    self.children.append(rtr.anchor_phenotype)

    def _execute(self, tables) -> PhenotypeTable:
        code_table = tables[self.domain]
        code_table = self._perform_codelist_filtering(code_table)
        code_table = self._perform_categorical_filtering(code_table, tables)
        code_table = self._perform_time_filtering(code_table)
        code_table = self._perform_date_selection(code_table)
        return select_phenotype_columns(code_table)

    def _perform_codelist_filtering(self, code_table):
        assert is_phenex_code_table(code_table)
        code_table = self.codelist_filter.filter(code_table)
        return code_table

    def _perform_categorical_filtering(self, code_table, tables):
        if self.categorical_filter is not None:
            assert is_phenex_code_table(code_table)
            code_table = self.categorical_filter.autojoin_filter(code_table, tables)
        return code_table

    def _perform_time_filtering(self, code_table):
        if self.date_range is not None:
            code_table = self.date_range.filter(code_table)
        if self.relative_time_range is not None:
            for rtr in self.relative_time_range:
                code_table = rtr.filter(code_table)
        return code_table

    def _perform_date_selection(self, code_table, reduce=True):
        if self.return_date is None or self.return_date == "all":
            return code_table
        if self.return_date == "first":
            aggregator = First(reduce=reduce)
        elif self.return_date == "last":
            aggregator = Last(reduce=reduce)
        else:
            raise ValueError(f"Unknown return_date: {self.return_date}")
        return aggregator.aggregate(code_table)

    def get_codelists(self) -> List[Codelist]:
        """
        Get all codelists used in the phenotype definition, including all children / dependent phenotypes.

        Returns:
            codeslist: A list of codelists used in the cohort definition.
        """
        codelists = [self.codelist]
        for p in self.children:
            codelists.extend(p.get_codelists())
        return codelists
