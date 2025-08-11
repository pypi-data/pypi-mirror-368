# flake8: noqa
# type: ignore
# Generated from verse/ql/grammar/VerseQLParser.g4 by ANTLR 4.13.0
from antlr4 import *
if "." in __name__:
    from .VerseQLParser import VerseQLParser
else:
    from VerseQLParser import VerseQLParser

# This class defines a complete listener for a parse tree produced by VerseQLParser.
class VerseQLParserListener(ParseTreeListener):

    # Enter a parse tree produced by VerseQLParser#parse_statement.
    def enterParse_statement(self, ctx:VerseQLParser.Parse_statementContext):
        pass

    # Exit a parse tree produced by VerseQLParser#parse_statement.
    def exitParse_statement(self, ctx:VerseQLParser.Parse_statementContext):
        pass


    # Enter a parse tree produced by VerseQLParser#parse_search.
    def enterParse_search(self, ctx:VerseQLParser.Parse_searchContext):
        pass

    # Exit a parse tree produced by VerseQLParser#parse_search.
    def exitParse_search(self, ctx:VerseQLParser.Parse_searchContext):
        pass


    # Enter a parse tree produced by VerseQLParser#parse_where.
    def enterParse_where(self, ctx:VerseQLParser.Parse_whereContext):
        pass

    # Exit a parse tree produced by VerseQLParser#parse_where.
    def exitParse_where(self, ctx:VerseQLParser.Parse_whereContext):
        pass


    # Enter a parse tree produced by VerseQLParser#parse_select.
    def enterParse_select(self, ctx:VerseQLParser.Parse_selectContext):
        pass

    # Exit a parse tree produced by VerseQLParser#parse_select.
    def exitParse_select(self, ctx:VerseQLParser.Parse_selectContext):
        pass


    # Enter a parse tree produced by VerseQLParser#parse_collection.
    def enterParse_collection(self, ctx:VerseQLParser.Parse_collectionContext):
        pass

    # Exit a parse tree produced by VerseQLParser#parse_collection.
    def exitParse_collection(self, ctx:VerseQLParser.Parse_collectionContext):
        pass


    # Enter a parse tree produced by VerseQLParser#parse_order_by.
    def enterParse_order_by(self, ctx:VerseQLParser.Parse_order_byContext):
        pass

    # Exit a parse tree produced by VerseQLParser#parse_order_by.
    def exitParse_order_by(self, ctx:VerseQLParser.Parse_order_byContext):
        pass


    # Enter a parse tree produced by VerseQLParser#parse_update.
    def enterParse_update(self, ctx:VerseQLParser.Parse_updateContext):
        pass

    # Exit a parse tree produced by VerseQLParser#parse_update.
    def exitParse_update(self, ctx:VerseQLParser.Parse_updateContext):
        pass


    # Enter a parse tree produced by VerseQLParser#statement_single.
    def enterStatement_single(self, ctx:VerseQLParser.Statement_singleContext):
        pass

    # Exit a parse tree produced by VerseQLParser#statement_single.
    def exitStatement_single(self, ctx:VerseQLParser.Statement_singleContext):
        pass


    # Enter a parse tree produced by VerseQLParser#statement_multi.
    def enterStatement_multi(self, ctx:VerseQLParser.Statement_multiContext):
        pass

    # Exit a parse tree produced by VerseQLParser#statement_multi.
    def exitStatement_multi(self, ctx:VerseQLParser.Statement_multiContext):
        pass


    # Enter a parse tree produced by VerseQLParser#clause.
    def enterClause(self, ctx:VerseQLParser.ClauseContext):
        pass

    # Exit a parse tree produced by VerseQLParser#clause.
    def exitClause(self, ctx:VerseQLParser.ClauseContext):
        pass


    # Enter a parse tree produced by VerseQLParser#generic_clause.
    def enterGeneric_clause(self, ctx:VerseQLParser.Generic_clauseContext):
        pass

    # Exit a parse tree produced by VerseQLParser#generic_clause.
    def exitGeneric_clause(self, ctx:VerseQLParser.Generic_clauseContext):
        pass


    # Enter a parse tree produced by VerseQLParser#select_clause.
    def enterSelect_clause(self, ctx:VerseQLParser.Select_clauseContext):
        pass

    # Exit a parse tree produced by VerseQLParser#select_clause.
    def exitSelect_clause(self, ctx:VerseQLParser.Select_clauseContext):
        pass


    # Enter a parse tree produced by VerseQLParser#select_all.
    def enterSelect_all(self, ctx:VerseQLParser.Select_allContext):
        pass

    # Exit a parse tree produced by VerseQLParser#select_all.
    def exitSelect_all(self, ctx:VerseQLParser.Select_allContext):
        pass


    # Enter a parse tree produced by VerseQLParser#select_terms.
    def enterSelect_terms(self, ctx:VerseQLParser.Select_termsContext):
        pass

    # Exit a parse tree produced by VerseQLParser#select_terms.
    def exitSelect_terms(self, ctx:VerseQLParser.Select_termsContext):
        pass


    # Enter a parse tree produced by VerseQLParser#select_parameter.
    def enterSelect_parameter(self, ctx:VerseQLParser.Select_parameterContext):
        pass

    # Exit a parse tree produced by VerseQLParser#select_parameter.
    def exitSelect_parameter(self, ctx:VerseQLParser.Select_parameterContext):
        pass


    # Enter a parse tree produced by VerseQLParser#select_term.
    def enterSelect_term(self, ctx:VerseQLParser.Select_termContext):
        pass

    # Exit a parse tree produced by VerseQLParser#select_term.
    def exitSelect_term(self, ctx:VerseQLParser.Select_termContext):
        pass


    # Enter a parse tree produced by VerseQLParser#collection_clause.
    def enterCollection_clause(self, ctx:VerseQLParser.Collection_clauseContext):
        pass

    # Exit a parse tree produced by VerseQLParser#collection_clause.
    def exitCollection_clause(self, ctx:VerseQLParser.Collection_clauseContext):
        pass


    # Enter a parse tree produced by VerseQLParser#collection_identifier.
    def enterCollection_identifier(self, ctx:VerseQLParser.Collection_identifierContext):
        pass

    # Exit a parse tree produced by VerseQLParser#collection_identifier.
    def exitCollection_identifier(self, ctx:VerseQLParser.Collection_identifierContext):
        pass


    # Enter a parse tree produced by VerseQLParser#collection_parameter.
    def enterCollection_parameter(self, ctx:VerseQLParser.Collection_parameterContext):
        pass

    # Exit a parse tree produced by VerseQLParser#collection_parameter.
    def exitCollection_parameter(self, ctx:VerseQLParser.Collection_parameterContext):
        pass


    # Enter a parse tree produced by VerseQLParser#search_clause.
    def enterSearch_clause(self, ctx:VerseQLParser.Search_clauseContext):
        pass

    # Exit a parse tree produced by VerseQLParser#search_clause.
    def exitSearch_clause(self, ctx:VerseQLParser.Search_clauseContext):
        pass


    # Enter a parse tree produced by VerseQLParser#where_clause.
    def enterWhere_clause(self, ctx:VerseQLParser.Where_clauseContext):
        pass

    # Exit a parse tree produced by VerseQLParser#where_clause.
    def exitWhere_clause(self, ctx:VerseQLParser.Where_clauseContext):
        pass


    # Enter a parse tree produced by VerseQLParser#expression_operand.
    def enterExpression_operand(self, ctx:VerseQLParser.Expression_operandContext):
        pass

    # Exit a parse tree produced by VerseQLParser#expression_operand.
    def exitExpression_operand(self, ctx:VerseQLParser.Expression_operandContext):
        pass


    # Enter a parse tree produced by VerseQLParser#expression_not.
    def enterExpression_not(self, ctx:VerseQLParser.Expression_notContext):
        pass

    # Exit a parse tree produced by VerseQLParser#expression_not.
    def exitExpression_not(self, ctx:VerseQLParser.Expression_notContext):
        pass


    # Enter a parse tree produced by VerseQLParser#expression_or.
    def enterExpression_or(self, ctx:VerseQLParser.Expression_orContext):
        pass

    # Exit a parse tree produced by VerseQLParser#expression_or.
    def exitExpression_or(self, ctx:VerseQLParser.Expression_orContext):
        pass


    # Enter a parse tree produced by VerseQLParser#expression_comparison.
    def enterExpression_comparison(self, ctx:VerseQLParser.Expression_comparisonContext):
        pass

    # Exit a parse tree produced by VerseQLParser#expression_comparison.
    def exitExpression_comparison(self, ctx:VerseQLParser.Expression_comparisonContext):
        pass


    # Enter a parse tree produced by VerseQLParser#expression_comparison_in.
    def enterExpression_comparison_in(self, ctx:VerseQLParser.Expression_comparison_inContext):
        pass

    # Exit a parse tree produced by VerseQLParser#expression_comparison_in.
    def exitExpression_comparison_in(self, ctx:VerseQLParser.Expression_comparison_inContext):
        pass


    # Enter a parse tree produced by VerseQLParser#expression_paranthesis.
    def enterExpression_paranthesis(self, ctx:VerseQLParser.Expression_paranthesisContext):
        pass

    # Exit a parse tree produced by VerseQLParser#expression_paranthesis.
    def exitExpression_paranthesis(self, ctx:VerseQLParser.Expression_paranthesisContext):
        pass


    # Enter a parse tree produced by VerseQLParser#expression_comparison_between.
    def enterExpression_comparison_between(self, ctx:VerseQLParser.Expression_comparison_betweenContext):
        pass

    # Exit a parse tree produced by VerseQLParser#expression_comparison_between.
    def exitExpression_comparison_between(self, ctx:VerseQLParser.Expression_comparison_betweenContext):
        pass


    # Enter a parse tree produced by VerseQLParser#expression_and.
    def enterExpression_and(self, ctx:VerseQLParser.Expression_andContext):
        pass

    # Exit a parse tree produced by VerseQLParser#expression_and.
    def exitExpression_and(self, ctx:VerseQLParser.Expression_andContext):
        pass


    # Enter a parse tree produced by VerseQLParser#operand_value.
    def enterOperand_value(self, ctx:VerseQLParser.Operand_valueContext):
        pass

    # Exit a parse tree produced by VerseQLParser#operand_value.
    def exitOperand_value(self, ctx:VerseQLParser.Operand_valueContext):
        pass


    # Enter a parse tree produced by VerseQLParser#operand_field.
    def enterOperand_field(self, ctx:VerseQLParser.Operand_fieldContext):
        pass

    # Exit a parse tree produced by VerseQLParser#operand_field.
    def exitOperand_field(self, ctx:VerseQLParser.Operand_fieldContext):
        pass


    # Enter a parse tree produced by VerseQLParser#operand_parameter.
    def enterOperand_parameter(self, ctx:VerseQLParser.Operand_parameterContext):
        pass

    # Exit a parse tree produced by VerseQLParser#operand_parameter.
    def exitOperand_parameter(self, ctx:VerseQLParser.Operand_parameterContext):
        pass


    # Enter a parse tree produced by VerseQLParser#operand_ref.
    def enterOperand_ref(self, ctx:VerseQLParser.Operand_refContext):
        pass

    # Exit a parse tree produced by VerseQLParser#operand_ref.
    def exitOperand_ref(self, ctx:VerseQLParser.Operand_refContext):
        pass


    # Enter a parse tree produced by VerseQLParser#operand_function.
    def enterOperand_function(self, ctx:VerseQLParser.Operand_functionContext):
        pass

    # Exit a parse tree produced by VerseQLParser#operand_function.
    def exitOperand_function(self, ctx:VerseQLParser.Operand_functionContext):
        pass


    # Enter a parse tree produced by VerseQLParser#order_by_clause.
    def enterOrder_by_clause(self, ctx:VerseQLParser.Order_by_clauseContext):
        pass

    # Exit a parse tree produced by VerseQLParser#order_by_clause.
    def exitOrder_by_clause(self, ctx:VerseQLParser.Order_by_clauseContext):
        pass


    # Enter a parse tree produced by VerseQLParser#order_by_terms.
    def enterOrder_by_terms(self, ctx:VerseQLParser.Order_by_termsContext):
        pass

    # Exit a parse tree produced by VerseQLParser#order_by_terms.
    def exitOrder_by_terms(self, ctx:VerseQLParser.Order_by_termsContext):
        pass


    # Enter a parse tree produced by VerseQLParser#order_by_parameter.
    def enterOrder_by_parameter(self, ctx:VerseQLParser.Order_by_parameterContext):
        pass

    # Exit a parse tree produced by VerseQLParser#order_by_parameter.
    def exitOrder_by_parameter(self, ctx:VerseQLParser.Order_by_parameterContext):
        pass


    # Enter a parse tree produced by VerseQLParser#order_by_term.
    def enterOrder_by_term(self, ctx:VerseQLParser.Order_by_termContext):
        pass

    # Exit a parse tree produced by VerseQLParser#order_by_term.
    def exitOrder_by_term(self, ctx:VerseQLParser.Order_by_termContext):
        pass


    # Enter a parse tree produced by VerseQLParser#set_clause.
    def enterSet_clause(self, ctx:VerseQLParser.Set_clauseContext):
        pass

    # Exit a parse tree produced by VerseQLParser#set_clause.
    def exitSet_clause(self, ctx:VerseQLParser.Set_clauseContext):
        pass


    # Enter a parse tree produced by VerseQLParser#update_operations.
    def enterUpdate_operations(self, ctx:VerseQLParser.Update_operationsContext):
        pass

    # Exit a parse tree produced by VerseQLParser#update_operations.
    def exitUpdate_operations(self, ctx:VerseQLParser.Update_operationsContext):
        pass


    # Enter a parse tree produced by VerseQLParser#update_parameter.
    def enterUpdate_parameter(self, ctx:VerseQLParser.Update_parameterContext):
        pass

    # Exit a parse tree produced by VerseQLParser#update_parameter.
    def exitUpdate_parameter(self, ctx:VerseQLParser.Update_parameterContext):
        pass


    # Enter a parse tree produced by VerseQLParser#update_operation.
    def enterUpdate_operation(self, ctx:VerseQLParser.Update_operationContext):
        pass

    # Exit a parse tree produced by VerseQLParser#update_operation.
    def exitUpdate_operation(self, ctx:VerseQLParser.Update_operationContext):
        pass


    # Enter a parse tree produced by VerseQLParser#function.
    def enterFunction(self, ctx:VerseQLParser.FunctionContext):
        pass

    # Exit a parse tree produced by VerseQLParser#function.
    def exitFunction(self, ctx:VerseQLParser.FunctionContext):
        pass


    # Enter a parse tree produced by VerseQLParser#function_no_args.
    def enterFunction_no_args(self, ctx:VerseQLParser.Function_no_argsContext):
        pass

    # Exit a parse tree produced by VerseQLParser#function_no_args.
    def exitFunction_no_args(self, ctx:VerseQLParser.Function_no_argsContext):
        pass


    # Enter a parse tree produced by VerseQLParser#function_with_args.
    def enterFunction_with_args(self, ctx:VerseQLParser.Function_with_argsContext):
        pass

    # Exit a parse tree produced by VerseQLParser#function_with_args.
    def exitFunction_with_args(self, ctx:VerseQLParser.Function_with_argsContext):
        pass


    # Enter a parse tree produced by VerseQLParser#function_with_named_args.
    def enterFunction_with_named_args(self, ctx:VerseQLParser.Function_with_named_argsContext):
        pass

    # Exit a parse tree produced by VerseQLParser#function_with_named_args.
    def exitFunction_with_named_args(self, ctx:VerseQLParser.Function_with_named_argsContext):
        pass


    # Enter a parse tree produced by VerseQLParser#named_arg.
    def enterNamed_arg(self, ctx:VerseQLParser.Named_argContext):
        pass

    # Exit a parse tree produced by VerseQLParser#named_arg.
    def exitNamed_arg(self, ctx:VerseQLParser.Named_argContext):
        pass


    # Enter a parse tree produced by VerseQLParser#ref.
    def enterRef(self, ctx:VerseQLParser.RefContext):
        pass

    # Exit a parse tree produced by VerseQLParser#ref.
    def exitRef(self, ctx:VerseQLParser.RefContext):
        pass


    # Enter a parse tree produced by VerseQLParser#ref_path.
    def enterRef_path(self, ctx:VerseQLParser.Ref_pathContext):
        pass

    # Exit a parse tree produced by VerseQLParser#ref_path.
    def exitRef_path(self, ctx:VerseQLParser.Ref_pathContext):
        pass


    # Enter a parse tree produced by VerseQLParser#parameter.
    def enterParameter(self, ctx:VerseQLParser.ParameterContext):
        pass

    # Exit a parse tree produced by VerseQLParser#parameter.
    def exitParameter(self, ctx:VerseQLParser.ParameterContext):
        pass


    # Enter a parse tree produced by VerseQLParser#field.
    def enterField(self, ctx:VerseQLParser.FieldContext):
        pass

    # Exit a parse tree produced by VerseQLParser#field.
    def exitField(self, ctx:VerseQLParser.FieldContext):
        pass


    # Enter a parse tree produced by VerseQLParser#field_path.
    def enterField_path(self, ctx:VerseQLParser.Field_pathContext):
        pass

    # Exit a parse tree produced by VerseQLParser#field_path.
    def exitField_path(self, ctx:VerseQLParser.Field_pathContext):
        pass


    # Enter a parse tree produced by VerseQLParser#field_primitive.
    def enterField_primitive(self, ctx:VerseQLParser.Field_primitiveContext):
        pass

    # Exit a parse tree produced by VerseQLParser#field_primitive.
    def exitField_primitive(self, ctx:VerseQLParser.Field_primitiveContext):
        pass


    # Enter a parse tree produced by VerseQLParser#value_null.
    def enterValue_null(self, ctx:VerseQLParser.Value_nullContext):
        pass

    # Exit a parse tree produced by VerseQLParser#value_null.
    def exitValue_null(self, ctx:VerseQLParser.Value_nullContext):
        pass


    # Enter a parse tree produced by VerseQLParser#value_true.
    def enterValue_true(self, ctx:VerseQLParser.Value_trueContext):
        pass

    # Exit a parse tree produced by VerseQLParser#value_true.
    def exitValue_true(self, ctx:VerseQLParser.Value_trueContext):
        pass


    # Enter a parse tree produced by VerseQLParser#value_false.
    def enterValue_false(self, ctx:VerseQLParser.Value_falseContext):
        pass

    # Exit a parse tree produced by VerseQLParser#value_false.
    def exitValue_false(self, ctx:VerseQLParser.Value_falseContext):
        pass


    # Enter a parse tree produced by VerseQLParser#value_string.
    def enterValue_string(self, ctx:VerseQLParser.Value_stringContext):
        pass

    # Exit a parse tree produced by VerseQLParser#value_string.
    def exitValue_string(self, ctx:VerseQLParser.Value_stringContext):
        pass


    # Enter a parse tree produced by VerseQLParser#value_integer.
    def enterValue_integer(self, ctx:VerseQLParser.Value_integerContext):
        pass

    # Exit a parse tree produced by VerseQLParser#value_integer.
    def exitValue_integer(self, ctx:VerseQLParser.Value_integerContext):
        pass


    # Enter a parse tree produced by VerseQLParser#value_decimal.
    def enterValue_decimal(self, ctx:VerseQLParser.Value_decimalContext):
        pass

    # Exit a parse tree produced by VerseQLParser#value_decimal.
    def exitValue_decimal(self, ctx:VerseQLParser.Value_decimalContext):
        pass


    # Enter a parse tree produced by VerseQLParser#value_json.
    def enterValue_json(self, ctx:VerseQLParser.Value_jsonContext):
        pass

    # Exit a parse tree produced by VerseQLParser#value_json.
    def exitValue_json(self, ctx:VerseQLParser.Value_jsonContext):
        pass


    # Enter a parse tree produced by VerseQLParser#value_array.
    def enterValue_array(self, ctx:VerseQLParser.Value_arrayContext):
        pass

    # Exit a parse tree produced by VerseQLParser#value_array.
    def exitValue_array(self, ctx:VerseQLParser.Value_arrayContext):
        pass


    # Enter a parse tree produced by VerseQLParser#literal_string.
    def enterLiteral_string(self, ctx:VerseQLParser.Literal_stringContext):
        pass

    # Exit a parse tree produced by VerseQLParser#literal_string.
    def exitLiteral_string(self, ctx:VerseQLParser.Literal_stringContext):
        pass


    # Enter a parse tree produced by VerseQLParser#array_empty.
    def enterArray_empty(self, ctx:VerseQLParser.Array_emptyContext):
        pass

    # Exit a parse tree produced by VerseQLParser#array_empty.
    def exitArray_empty(self, ctx:VerseQLParser.Array_emptyContext):
        pass


    # Enter a parse tree produced by VerseQLParser#array_items.
    def enterArray_items(self, ctx:VerseQLParser.Array_itemsContext):
        pass

    # Exit a parse tree produced by VerseQLParser#array_items.
    def exitArray_items(self, ctx:VerseQLParser.Array_itemsContext):
        pass


    # Enter a parse tree produced by VerseQLParser#json.
    def enterJson(self, ctx:VerseQLParser.JsonContext):
        pass

    # Exit a parse tree produced by VerseQLParser#json.
    def exitJson(self, ctx:VerseQLParser.JsonContext):
        pass


    # Enter a parse tree produced by VerseQLParser#json_obj.
    def enterJson_obj(self, ctx:VerseQLParser.Json_objContext):
        pass

    # Exit a parse tree produced by VerseQLParser#json_obj.
    def exitJson_obj(self, ctx:VerseQLParser.Json_objContext):
        pass


    # Enter a parse tree produced by VerseQLParser#json_pair.
    def enterJson_pair(self, ctx:VerseQLParser.Json_pairContext):
        pass

    # Exit a parse tree produced by VerseQLParser#json_pair.
    def exitJson_pair(self, ctx:VerseQLParser.Json_pairContext):
        pass


    # Enter a parse tree produced by VerseQLParser#json_arr.
    def enterJson_arr(self, ctx:VerseQLParser.Json_arrContext):
        pass

    # Exit a parse tree produced by VerseQLParser#json_arr.
    def exitJson_arr(self, ctx:VerseQLParser.Json_arrContext):
        pass


    # Enter a parse tree produced by VerseQLParser#json_value.
    def enterJson_value(self, ctx:VerseQLParser.Json_valueContext):
        pass

    # Exit a parse tree produced by VerseQLParser#json_value.
    def exitJson_value(self, ctx:VerseQLParser.Json_valueContext):
        pass


    # Enter a parse tree produced by VerseQLParser#json_string.
    def enterJson_string(self, ctx:VerseQLParser.Json_stringContext):
        pass

    # Exit a parse tree produced by VerseQLParser#json_string.
    def exitJson_string(self, ctx:VerseQLParser.Json_stringContext):
        pass


    # Enter a parse tree produced by VerseQLParser#json_number.
    def enterJson_number(self, ctx:VerseQLParser.Json_numberContext):
        pass

    # Exit a parse tree produced by VerseQLParser#json_number.
    def exitJson_number(self, ctx:VerseQLParser.Json_numberContext):
        pass



del VerseQLParser
