# flake8: noqa
# type: ignore
import decimal
import json

from antlr4 import *

from ..core._operation import Operation
from ._models import (
    And,
    Collection,
    Comparison,
    ComparisonOp,
    Field,
    Function,
    Not,
    Or,
    OrderBy,
    OrderByTerm,
    Parameter,
    Ref,
    Select,
    SelectTerm,
    Update,
    UpdateOperation,
)
from .generated.VerseQLParser import VerseQLParser


# This class defines a complete listener for a parse tree produced by VerseQLParser.
class VerseQLParserListener(ParseTreeListener):
    operation = None
    select = None
    collection = None
    where = None
    order_by = None
    update = None
    search = None

    # Enter a parse tree produced by VerseQLParser#parse_statement.
    def enterParse_statement(self, ctx: VerseQLParser.Parse_statementContext):
        pass

    # Exit a parse tree produced by VerseQLParser#parse_statement.
    def exitParse_statement(self, ctx: VerseQLParser.Parse_statementContext):
        self.operation = ctx.statement().val

    # Enter a parse tree produced by VerseQLParser#parse_search.
    def enterParse_search(self, ctx: VerseQLParser.Parse_searchContext):
        pass

    # Exit a parse tree produced by VerseQLParser#parse_search.
    def exitParse_search(self, ctx: VerseQLParser.Parse_searchContext):
        self.search = ctx.expression().val

    # Enter a parse tree produced by VerseQLParser#parse_where.
    def enterParse_where(self, ctx: VerseQLParser.Parse_whereContext):
        pass

    # Exit a parse tree produced by VerseQLParser#parse_where.
    def exitParse_where(self, ctx: VerseQLParser.Parse_whereContext):
        self.where = ctx.expression().val

    # Enter a parse tree produced by VerseQLParser#parse_select.
    def enterParse_select(self, ctx: VerseQLParser.Parse_selectContext):
        pass

    # Exit a parse tree produced by VerseQLParser#parse_select.
    def exitParse_select(self, ctx: VerseQLParser.Parse_selectContext):
        self.select = ctx.select().val

    # Enter a parse tree produced by VerseQLParser#parse_collection.
    def enterParse_collection(
        self, ctx: VerseQLParser.Parse_collectionContext
    ):
        pass

    # Exit a parse tree produced by VerseQLParser#parse_collection.
    def exitParse_collection(self, ctx: VerseQLParser.Parse_collectionContext):
        self.collection = ctx.collection().val

    # Enter a parse tree produced by VerseQLParser#parse_order_by.
    def enterParse_order_by(self, ctx: VerseQLParser.Parse_order_byContext):
        pass

    # Exit a parse tree produced by VerseQLParser#parse_order_by.
    def exitParse_order_by(self, ctx: VerseQLParser.Parse_order_byContext):
        self.order_by = ctx.order_by().val

    # Enter a parse tree produced by VerseQLParser#parse_update.
    def enterParse_update(self, ctx: VerseQLParser.Parse_updateContext):
        pass

    # Exit a parse tree produced by VerseQLParser#parse_update.
    def exitParse_update(self, ctx: VerseQLParser.Parse_updateContext):
        self.update = ctx.update().val

    # Enter a parse tree produced by VerseQLParser#statement_single.
    def enterStatement_single(
        self, ctx: VerseQLParser.Statement_singleContext
    ):
        pass

    # Exit a parse tree produced by VerseQLParser#statement_single.
    def exitStatement_single(self, ctx: VerseQLParser.Statement_singleContext):
        op = ctx.op.text.lower()
        args = dict()
        for clause in ctx.clause():
            args[clause.key] = clause.val
        ctx.val = Operation(name=op, args=args)

    # Enter a parse tree produced by VerseQLParser#statement_multi.
    def enterStatement_multi(self, ctx: VerseQLParser.Statement_multiContext):
        pass

    # Exit a parse tree produced by VerseQLParser#statement_multi.
    def exitStatement_multi(self, ctx: VerseQLParser.Statement_multiContext):
        op = ctx.op.text.lower()
        operations = []
        for statement in ctx.statement():
            operations.append(statement.val)
        if op == "batch":
            arg = "batch"
        elif op == "transact":
            arg = "transaction"
        else:
            arg = op
        ctx.val = Operation(name=op, args={arg: {"operations": operations}})

    # Enter a parse tree produced by VerseQLParser#clause.
    def enterClause(self, ctx: VerseQLParser.ClauseContext):
        pass

    # Exit a parse tree produced by VerseQLParser#clause.
    def exitClause(self, ctx: VerseQLParser.ClauseContext):
        clause = None
        if ctx.select_clause() is not None:
            clause = ctx.select_clause()
        elif ctx.collection_clause() is not None:
            clause = ctx.collection_clause()
        elif ctx.set_clause() is not None:
            clause = ctx.set_clause()
        elif ctx.where_clause() is not None:
            clause = ctx.where_clause()
        elif ctx.order_by_clause() is not None:
            clause = ctx.order_by_clause()
        elif ctx.search_clause() is not None:
            clause = ctx.search_clause()
        elif ctx.generic_clause() is not None:
            clause = ctx.generic_clause()
        ctx.key = clause.key
        ctx.val = clause.val

    # Enter a parse tree produced by VerseQLParser#generic_clause.
    def enterGeneric_clause(self, ctx: VerseQLParser.Generic_clauseContext):
        pass

    # Exit a parse tree produced by VerseQLParser#generic_clause.
    def exitGeneric_clause(self, ctx: VerseQLParser.Generic_clauseContext):
        ctx.key = ctx.name.text.lower()
        ctx.val = ctx.operand().val

    # Enter a parse tree produced by VerseQLParser#select_clause.
    def enterSelect_clause(self, ctx: VerseQLParser.Select_clauseContext):
        pass

    # Exit a parse tree produced by VerseQLParser#select_clause.
    def exitSelect_clause(self, ctx: VerseQLParser.Select_clauseContext):
        ctx.key = "select"
        ctx.val = ctx.select().val

    # Enter a parse tree produced by VerseQLParser#select_all.
    def enterSelect_all(self, ctx: VerseQLParser.Select_allContext):
        pass

    # Exit a parse tree produced by VerseQLParser#select_all.
    def exitSelect_all(self, ctx: VerseQLParser.Select_allContext):
        ctx.val = Select()

    # Enter a parse tree produced by VerseQLParser#select_terms.
    def enterSelect_terms(self, ctx: VerseQLParser.Select_termsContext):
        pass

    # Exit a parse tree produced by VerseQLParser#select_terms.
    def exitSelect_terms(self, ctx: VerseQLParser.Select_termsContext):
        ctx.val = Select(terms=[item.val for item in ctx.select_term()])

    # Enter a parse tree produced by VerseQLParser#select_parameter.
    def enterSelect_parameter(
        self, ctx: VerseQLParser.Select_parameterContext
    ):
        pass

    # Exit a parse tree produced by VerseQLParser#select_parameter.
    def exitSelect_parameter(self, ctx: VerseQLParser.Select_parameterContext):
        ctx.val = ctx.parameter().val

    # Enter a parse tree produced by VerseQLParser#select_term.
    def enterSelect_term(self, ctx: VerseQLParser.Select_termContext):
        pass

    # Exit a parse tree produced by VerseQLParser#select_term.
    def exitSelect_term(self, ctx: VerseQLParser.Select_termContext):
        ctx.val = SelectTerm(
            field=ctx.field()[0].val.path,
            alias=None if len(ctx.field()) == 1 else ctx.field()[1].val.path,
        )

    # Enter a parse tree produced by VerseQLParser#collection_clause.
    def enterCollection_clause(
        self, ctx: VerseQLParser.Collection_clauseContext
    ):
        pass

    # Exit a parse tree produced by VerseQLParser#collection_clause.
    def exitCollection_clause(
        self, ctx: VerseQLParser.Collection_clauseContext
    ):
        ctx.key = "collection"
        ctx.val = ctx.collection().val

    # Enter a parse tree produced by VerseQLParser#collection_identifier.
    def enterCollection_identifier(
        self, ctx: VerseQLParser.Collection_identifierContext
    ):
        pass

    # Exit a parse tree produced by VerseQLParser#collection_identifier.
    def exitCollection_identifier(
        self, ctx: VerseQLParser.Collection_identifierContext
    ):
        ctx.val = Collection(name=ctx.getText())

    # Enter a parse tree produced by VerseQLParser#collection_parameter.
    def enterCollection_parameter(
        self, ctx: VerseQLParser.Collection_parameterContext
    ):
        pass

    # Exit a parse tree produced by VerseQLParser#collection_parameter.
    def exitCollection_parameter(
        self, ctx: VerseQLParser.Collection_parameterContext
    ):
        ctx.val = ctx.parameter().val

    # Enter a parse tree produced by VerseQLParser#search_clause.
    def enterSearch_clause(self, ctx: VerseQLParser.Search_clauseContext):
        pass

    # Exit a parse tree produced by VerseQLParser#search_clause.
    def exitSearch_clause(self, ctx: VerseQLParser.Search_clauseContext):
        ctx.key = "search"
        ctx.val = ctx.expression().val

    # Enter a parse tree produced by VerseQLParser#where_clause.
    def enterWhere_clause(self, ctx: VerseQLParser.Where_clauseContext):
        pass

    # Exit a parse tree produced by VerseQLParser#where_clause.
    def exitWhere_clause(self, ctx: VerseQLParser.Where_clauseContext):
        ctx.key = "where"
        ctx.val = ctx.expression().val

    # Enter a parse tree produced by VerseQLParser#expression_operand.
    def enterExpression_operand(
        self, ctx: VerseQLParser.Expression_operandContext
    ):
        pass

    # Exit a parse tree produced by VerseQLParser#expression_operand.
    def exitExpression_operand(
        self, ctx: VerseQLParser.Expression_operandContext
    ):
        ctx.val = ctx.operand().val

    # Enter a parse tree produced by VerseQLParser#expression_paranthesis.
    def enterExpression_paranthesis(
        self, ctx: VerseQLParser.Expression_paranthesisContext
    ):
        pass

    # Exit a parse tree produced by VerseQLParser#expression_paranthesis.
    def exitExpression_paranthesis(
        self, ctx: VerseQLParser.Expression_paranthesisContext
    ):
        ctx.val = ctx.expression().val

    # Enter a parse tree produced by VerseQLParser#expression_comparison.
    def enterExpression_comparison(
        self, ctx: VerseQLParser.Expression_comparisonContext
    ):
        pass

    # Exit a parse tree produced by VerseQLParser#expression_comparison.
    def exitExpression_comparison(
        self, ctx: VerseQLParser.Expression_comparisonContext
    ):
        ctx.val = Comparison(
            lexpr=ctx.lhs.val,
            op=ctx.op.text.lower(),
            rexpr=ctx.rhs.val,
        )

    # Enter a parse tree produced by VerseQLParser#expression_comparison_between.
    def enterExpression_comparison_between(
        self, ctx: VerseQLParser.Expression_comparison_betweenContext
    ):
        pass

    # Exit a parse tree produced by VerseQLParser#expression_comparison_between.
    def exitExpression_comparison_between(
        self, ctx: VerseQLParser.Expression_comparison_betweenContext
    ):
        ctx.val = Comparison(
            lexpr=ctx.lhs.val,
            op=ComparisonOp.BETWEEN,
            rexpr=[ctx.low.val, ctx.high.val],
        )

    # Enter a parse tree produced by VerseQLParser#expression_comparison_in.
    def enterExpression_comparison_in(
        self, ctx: VerseQLParser.Expression_comparison_inContext
    ):
        pass

    # Exit a parse tree produced by VerseQLParser#expression_comparison_in.
    def exitExpression_comparison_in(
        self, ctx: VerseQLParser.Expression_comparison_inContext
    ):
        op = ComparisonOp.IN if ctx.not_in is None else ComparisonOp.NIN
        args = ctx.operand()
        ctx.val = Comparison(
            lexpr=ctx.lhs.val,
            op=op,
            rexpr=[args[i].val for i in range(1, len(args))],
        )

    # Enter a parse tree produced by VerseQLParser#expression_not.
    def enterExpression_not(self, ctx: VerseQLParser.Expression_notContext):
        pass

    # Exit a parse tree produced by VerseQLParser#expression_not.
    def exitExpression_not(self, ctx: VerseQLParser.Expression_notContext):
        ctx.val = Not(expr=ctx.expression().val)

    # Enter a parse tree produced by VerseQLParser#expression_and.
    def enterExpression_and(self, ctx: VerseQLParser.Expression_andContext):
        pass

    # Exit a parse tree produced by VerseQLParser#expression_and.
    def exitExpression_and(self, ctx: VerseQLParser.Expression_andContext):
        ctx.val = And(lexpr=ctx.lhs.val, rexpr=ctx.rhs.val)

    # Enter a parse tree produced by VerseQLParser#expression_or.
    def enterExpression_or(self, ctx: VerseQLParser.Expression_orContext):
        pass

    # Exit a parse tree produced by VerseQLParser#expression_or.
    def exitExpression_or(self, ctx: VerseQLParser.Expression_orContext):
        ctx.val = Or(lexpr=ctx.lhs.val, rexpr=ctx.rhs.val)

        # Enter a parse tree produced by VerseQLParser#operand_value.

    def enterOperand_value(self, ctx: VerseQLParser.Operand_valueContext):
        pass

    # Exit a parse tree produced by VerseQLParser#operand_value.
    def exitOperand_value(self, ctx: VerseQLParser.Operand_valueContext):
        ctx.val = ctx.value().val

    # Enter a parse tree produced by VerseQLParser#operand_field.
    def enterOperand_field(self, ctx: VerseQLParser.Operand_fieldContext):
        pass

    # Exit a parse tree produced by VerseQLParser#operand_field.
    def exitOperand_field(self, ctx: VerseQLParser.Operand_fieldContext):
        ctx.val = ctx.field().val

    # Enter a parse tree produced by VerseQLParser#operand_parameter.
    def enterOperand_parameter(
        self, ctx: VerseQLParser.Operand_parameterContext
    ):
        pass

    # Exit a parse tree produced by VerseQLParser#operand_parameter.
    def exitOperand_parameter(
        self, ctx: VerseQLParser.Operand_parameterContext
    ):
        ctx.val = ctx.parameter().val

    # Enter a parse tree produced by VerseQLParser#operand_ref.
    def enterOperand_ref(self, ctx: VerseQLParser.Operand_refContext):
        pass

    # Exit a parse tree produced by VerseQLParser#operand_ref.
    def exitOperand_ref(self, ctx: VerseQLParser.Operand_refContext):
        ctx.val = ctx.ref().val

    # Enter a parse tree produced by VerseQLParser#operand_function.
    def enterOperand_function(
        self, ctx: VerseQLParser.Operand_functionContext
    ):
        pass

    # Exit a parse tree produced by VerseQLParser#operand_function.
    def exitOperand_function(self, ctx: VerseQLParser.Operand_functionContext):
        ctx.val = ctx.function().val

    # Enter a parse tree produced by VerseQLParser#order_by_clause.
    def enterOrder_by_clause(self, ctx: VerseQLParser.Order_by_clauseContext):
        pass

    # Exit a parse tree produced by VerseQLParser#order_by_clause.
    def exitOrder_by_clause(self, ctx: VerseQLParser.Order_by_clauseContext):
        ctx.key = "order_by"
        ctx.val = ctx.order_by().val

    # Enter a parse tree produced by VerseQLParser#order_by_terms.
    def enterOrder_by_terms(self, ctx: VerseQLParser.Order_by_termsContext):
        pass

    # Exit a parse tree produced by VerseQLParser#order_by_terms.
    def exitOrder_by_terms(self, ctx: VerseQLParser.Order_by_termsContext):
        ctx.val = OrderBy(terms=[term.val for term in ctx.order_by_term()])

    # Enter a parse tree produced by VerseQLParser#order_by_parameter.
    def enterOrder_by_parameter(
        self, ctx: VerseQLParser.Order_by_parameterContext
    ):
        pass

    # Exit a parse tree produced by VerseQLParser#order_by_parameter.
    def exitOrder_by_parameter(
        self, ctx: VerseQLParser.Order_by_parameterContext
    ):
        ctx.val = ctx.parameter().val

    # Enter a parse tree produced by VerseQLParser#order_by_term.
    def enterOrder_by_term(self, ctx: VerseQLParser.Order_by_termContext):
        pass

    # Exit a parse tree produced by VerseQLParser#order_by_term.
    def exitOrder_by_term(self, ctx: VerseQLParser.Order_by_termContext):
        ctx.val = OrderByTerm(
            field=ctx.field().val.path,
            direction=(
                None if ctx.direction is None else ctx.direction.text.lower()
            ),
        )

    # Enter a parse tree produced by VerseQLParser#set_clause.
    def enterSet_clause(self, ctx: VerseQLParser.Set_clauseContext):
        pass

    # Exit a parse tree produced by VerseQLParser#set_clause.
    def exitSet_clause(self, ctx: VerseQLParser.Set_clauseContext):
        ctx.key = "set"
        ctx.val = ctx.update().val

    # Enter a parse tree produced by VerseQLParser#update_operations.
    def enterUpdate_operations(
        self, ctx: VerseQLParser.Update_operationsContext
    ):
        pass

    # Exit a parse tree produced by VerseQLParser#update_operations.
    def exitUpdate_operations(
        self, ctx: VerseQLParser.Update_operationsContext
    ):
        ctx.val = Update(operations=[op.val for op in ctx.update_operation()])

    # Enter a parse tree produced by VerseQLParser#update_parameter.
    def enterUpdate_parameter(
        self, ctx: VerseQLParser.Update_parameterContext
    ):
        pass

    # Exit a parse tree produced by VerseQLParser#update_parameter.
    def exitUpdate_parameter(self, ctx: VerseQLParser.Update_parameterContext):
        ctx.val = ctx.parameter().val

    # Enter a parse tree produced by VerseQLParser#update_operation.
    def enterUpdate_operation(
        self, ctx: VerseQLParser.Update_operationContext
    ):
        pass

    # Exit a parse tree produced by VerseQLParser#update_operation.
    def exitUpdate_operation(self, ctx: VerseQLParser.Update_operationContext):
        args = ctx.function().val.args
        if args is None:
            ctx.val = UpdateOperation(
                field=ctx.field().val.path,
                op=ctx.function().val.name.lower(),
            )
        else:
            ctx.val = UpdateOperation(
                field=ctx.field().val.path,
                op=ctx.function().val.name.lower(),
                args=args,
            )

    # Enter a parse tree produced by VerseQLParser#function.
    def enterFunction(self, ctx: VerseQLParser.FunctionContext):
        pass

    # Exit a parse tree produced by VerseQLParser#function.
    def exitFunction(self, ctx: VerseQLParser.FunctionContext):
        args = ctx.function_args()
        if ctx.namespace is None:
            if isinstance(args.val, list):
                ctx.val = Function(name=ctx.name.text.lower(), args=args.val)
            elif isinstance(args.val, dict):
                ctx.val = Function(
                    name=ctx.name.text.lower(), named_args=args.val
                )
            else:
                ctx.val = Function(name=ctx.name.text.lower())
        else:
            if isinstance(args.val, list):
                ctx.val = Function(
                    name=ctx.name.text.lower(),
                    args=args.val,
                    namespace=ctx.namespace.text.lower(),
                )
            elif isinstance(args, dict):
                ctx.val = Function(
                    name=ctx.name.text.lower(),
                    named_args=args.val,
                    namespace=ctx.namespace.text.lower(),
                )
            else:
                ctx.val = Function(
                    ctx.name.text.lower(),
                    ctx.namespace.text.lower(),
                )

    # Enter a parse tree produced by VerseQLParser#function_no_args.
    def enterFunction_no_args(
        self, ctx: VerseQLParser.Function_no_argsContext
    ):
        pass

    # Exit a parse tree produced by VerseQLParser#function_no_args.
    def exitFunction_no_args(self, ctx: VerseQLParser.Function_no_argsContext):
        ctx.val = None

    # Enter a parse tree produced by VerseQLParser#function_with_args.
    def enterFunction_with_args(
        self, ctx: VerseQLParser.Function_with_argsContext
    ):
        pass

    # Exit a parse tree produced by VerseQLParser#function_with_args.
    def exitFunction_with_args(
        self, ctx: VerseQLParser.Function_with_argsContext
    ):
        ctx.val = [expr.val for expr in ctx.operand()]

    # Enter a parse tree produced by VerseQLParser#function_with_named_args.
    def enterFunction_with_named_args(
        self, ctx: VerseQLParser.Function_with_named_argsContext
    ):
        pass

    # Exit a parse tree produced by VerseQLParser#function_with_named_args.
    def exitFunction_with_named_args(
        self, ctx: VerseQLParser.Function_with_named_argsContext
    ):
        kwargs = dict()
        for arg in ctx.named_arg():
            kwargs[arg.val[0]] = arg.val[1]
        ctx.val = kwargs

    # Enter a parse tree produced by VerseQLParser#named_arg.
    def enterNamed_arg(self, ctx: VerseQLParser.Named_argContext):
        pass

    # Exit a parse tree produced by VerseQLParser#named_arg.
    def exitNamed_arg(self, ctx: VerseQLParser.Named_argContext):
        ctx.val = (ctx.name.text, ctx.operand().val)

    # Enter a parse tree produced by VerseQLParser#ref.
    def enterRef(self, ctx: VerseQLParser.RefContext):
        pass

    # Exit a parse tree produced by VerseQLParser#ref.
    def exitRef(self, ctx: VerseQLParser.RefContext):
        ctx.val = Ref(path=ctx.path)

    # Enter a parse tree produced by VerseQLParser#parameter.
    def enterParameter(self, ctx: VerseQLParser.ParameterContext):
        pass

    # Exit a parse tree produced by VerseQLParser#parameter.
    def exitParameter(self, ctx: VerseQLParser.ParameterContext):
        ctx.val = Parameter(name=ctx.name.text)

    # Enter a parse tree produced by VerseQLParser#field.
    def enterField(self, ctx: VerseQLParser.FieldContext):
        pass

    # Exit a parse tree produced by VerseQLParser#field.
    def exitField(self, ctx: VerseQLParser.FieldContext):
        ctx.val = Field(path=ctx.getText())

    # Enter a parse tree produced by VerseQLParser#field_path.
    def enterField_path(self, ctx: VerseQLParser.Field_pathContext):
        pass

    # Exit a parse tree produced by VerseQLParser#field_path.
    def exitField_path(self, ctx: VerseQLParser.Field_pathContext):
        pass

    # Enter a parse tree produced by VerseQLParser#field_primitive.
    def enterField_primitive(self, ctx: VerseQLParser.Field_primitiveContext):
        pass

    # Exit a parse tree produced by VerseQLParser#field_primitive.
    def exitField_primitive(self, ctx: VerseQLParser.Field_primitiveContext):
        pass

    # Enter a parse tree produced by VerseQLParser#value_null.
    def enterValue_null(self, ctx: VerseQLParser.Value_nullContext):
        pass

    # Exit a parse tree produced by VerseQLParser#value_null.
    def exitValue_null(self, ctx: VerseQLParser.Value_nullContext):
        ctx.val = None

    # Enter a parse tree produced by VerseQLParser#value_true.
    def enterValue_true(self, ctx: VerseQLParser.Value_trueContext):
        pass

    # Exit a parse tree produced by VerseQLParser#value_true.
    def exitValue_true(self, ctx: VerseQLParser.Value_trueContext):
        ctx.val = True

    # Enter a parse tree produced by VerseQLParser#value_false.
    def enterValue_false(self, ctx: VerseQLParser.Value_falseContext):
        pass

    # Exit a parse tree produced by VerseQLParser#value_false.
    def exitValue_false(self, ctx: VerseQLParser.Value_falseContext):
        ctx.val = False

    # Enter a parse tree produced by VerseQLParser#value_string.
    def enterValue_string(self, ctx: VerseQLParser.Value_stringContext):
        pass

    # Exit a parse tree produced by VerseQLParser#value_string.
    def exitValue_string(self, ctx: VerseQLParser.Value_stringContext):
        ctx.val = eval(ctx.getText())

    # Enter a parse tree produced by VerseQLParser#value_integer.
    def enterValue_integer(self, ctx: VerseQLParser.Value_integerContext):
        pass

    # Exit a parse tree produced by VerseQLParser#value_integer.
    def exitValue_integer(self, ctx: VerseQLParser.Value_integerContext):
        ctx.val = int(ctx.getText())

    # Enter a parse tree produced by VerseQLParser#value_decimal.
    def enterValue_decimal(self, ctx: VerseQLParser.Value_decimalContext):
        pass

    # Exit a parse tree produced by VerseQLParser#value_decimal.
    def exitValue_decimal(self, ctx: VerseQLParser.Value_decimalContext):
        ctx.val = float(decimal.Decimal(ctx.getText()))

    # Enter a parse tree produced by VerseQLParser#value_json.
    def enterValue_json(self, ctx: VerseQLParser.Value_jsonContext):
        pass

    # Exit a parse tree produced by VerseQLParser#value_json.
    def exitValue_json(self, ctx: VerseQLParser.Value_jsonContext):
        ctx.val = json.loads(ctx.getText())

    # Enter a parse tree produced by VerseQLParser#value_array.
    def enterValue_array(self, ctx: VerseQLParser.Value_arrayContext):
        pass

    # Exit a parse tree produced by VerseQLParser#value_array.
    def exitValue_array(self, ctx: VerseQLParser.Value_arrayContext):
        ctx.val = ctx.array().val

    # Enter a parse tree produced by VerseQLParser#array_empty.
    def enterArray_empty(self, ctx: VerseQLParser.Array_emptyContext):
        pass

    # Exit a parse tree produced by VerseQLParser#array_empty.
    def exitArray_empty(self, ctx: VerseQLParser.Array_emptyContext):
        ctx.val = []

    # Enter a parse tree produced by VerseQLParser#array_items.
    def enterArray_items(self, ctx: VerseQLParser.Array_itemsContext):
        pass

    # Exit a parse tree produced by VerseQLParser#array_items.
    def exitArray_items(self, ctx: VerseQLParser.Array_itemsContext):
        ctx.val = [item.val for item in ctx.value()]

    # Enter a parse tree produced by VerseQLParser#json.
    def enterJson(self, ctx: VerseQLParser.JsonContext):
        pass

    # Exit a parse tree produced by VerseQLParser#json.
    def exitJson(self, ctx: VerseQLParser.JsonContext):
        pass

    # Enter a parse tree produced by VerseQLParser#json_obj.
    def enterJson_obj(self, ctx: VerseQLParser.Json_objContext):
        pass

    # Exit a parse tree produced by VerseQLParser#json_obj.
    def exitJson_obj(self, ctx: VerseQLParser.Json_objContext):
        pass

    # Enter a parse tree produced by VerseQLParser#json_pair.
    def enterJson_pair(self, ctx: VerseQLParser.Json_pairContext):
        pass

    # Exit a parse tree produced by VerseQLParser#json_pair.
    def exitJson_pair(self, ctx: VerseQLParser.Json_pairContext):
        pass

    # Enter a parse tree produced by VerseQLParser#json_arr.
    def enterJson_arr(self, ctx: VerseQLParser.Json_arrContext):
        pass

    # Exit a parse tree produced by VerseQLParser#json_arr.
    def exitJson_arr(self, ctx: VerseQLParser.Json_arrContext):
        pass

    # Enter a parse tree produced by VerseQLParser#json_value.
    def enterJson_value(self, ctx: VerseQLParser.Json_valueContext):
        pass

    # Exit a parse tree produced by VerseQLParser#json_value.
    def exitJson_value(self, ctx: VerseQLParser.Json_valueContext):
        pass


del VerseQLParser
