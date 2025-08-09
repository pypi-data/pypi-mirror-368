from sqlglot import expressions as exp

from ...schema import Reference
from .base import BaseSQLConverter


class ReferenceConverter(BaseSQLConverter[Reference]):
    """
    SQL converter for DBML Reference objects.

    Converts DBML reference definitions to SQLGlot foreign key constraint expressions,
    including support for ON DELETE and ON UPDATE actions.
    """

    def convert(self, node):
        """
        Convert a DBML Reference object to a SQLGlot foreign key constraint expression.

        Args:
            node: The Reference object to convert.

        Returns:
            exp.Constraint: The SQLGlot foreign key constraint expression.
        """
        reference = node
        options = []
        if reference.settings:
            if reference.settings.delete:
                options.append(f"ON DELETE {reference.settings.delete.upper()}")
            if reference.settings.update:
                options.append(f"ON UPDATE {reference.settings.update.upper()}")
        return exp.Constraint(
            this=(
                exp.Identifier(this=reference.name, quoted=False)
                if reference.name
                else None
            ),
            expressions=[
                exp.ForeignKey(
                    expressions=list(
                        map(
                            lambda column: exp.Identifier(this=column, quoted=True),
                            reference.from_columns,
                        )
                    ),
                    reference=exp.Reference(
                        this=exp.Schema(
                            this=exp.Table(
                                this=exp.Identifier(
                                    this=reference.to_table.name, quoted=True
                                ),
                                db=exp.Identifier(
                                    this=reference.to_table.db_schema, quoted=True
                                )
                                if reference.to_table.db_schema
                                else None,
                            ),
                            expressions=list(
                                map(
                                    lambda column: exp.Identifier(
                                        this=column, quoted=True
                                    ),
                                    reference.to_columns,
                                )
                            ),
                        ),
                        options=options,
                    ),
                )
            ],
        )
