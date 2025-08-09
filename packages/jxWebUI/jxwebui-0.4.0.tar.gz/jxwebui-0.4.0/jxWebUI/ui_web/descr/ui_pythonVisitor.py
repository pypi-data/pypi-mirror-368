# Generated from ui_python.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .ui_pythonParser import ui_pythonParser
else:
    from ui_pythonParser import ui_pythonParser

# This class defines a complete generic visitor for a parse tree produced by ui_pythonParser.

class ui_pythonVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by ui_pythonParser#kv.
    def visitKv(self, ctx:ui_pythonParser.KvContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#jsonObj.
    def visitJsonObj(self, ctx:ui_pythonParser.JsonObjContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#jsonArr.
    def visitJsonArr(self, ctx:ui_pythonParser.JsonArrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#json.
    def visitJson(self, ctx:ui_pythonParser.JsonContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#numberValue.
    def visitNumberValue(self, ctx:ui_pythonParser.NumberValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#stringValue.
    def visitStringValue(self, ctx:ui_pythonParser.StringValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#booleanValue.
    def visitBooleanValue(self, ctx:ui_pythonParser.BooleanValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#variableValue.
    def visitVariableValue(self, ctx:ui_pythonParser.VariableValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#jsonValue.
    def visitJsonValue(self, ctx:ui_pythonParser.JsonValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#attrStatement.
    def visitAttrStatement(self, ctx:ui_pythonParser.AttrStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#computeOP.
    def visitComputeOP(self, ctx:ui_pythonParser.ComputeOPContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#computeCol.
    def visitComputeCol(self, ctx:ui_pythonParser.ComputeColContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#colSingleOP.
    def visitColSingleOP(self, ctx:ui_pythonParser.ColSingleOPContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#colOPBrackets.
    def visitColOPBrackets(self, ctx:ui_pythonParser.ColOPBracketsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#computeMultiCol.
    def visitComputeMultiCol(self, ctx:ui_pythonParser.ComputeMultiColContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#computeEquality.
    def visitComputeEquality(self, ctx:ui_pythonParser.ComputeEqualityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#rowCompute.
    def visitRowCompute(self, ctx:ui_pythonParser.RowComputeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#colCompute.
    def visitColCompute(self, ctx:ui_pythonParser.ColComputeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#computeStyle.
    def visitComputeStyle(self, ctx:ui_pythonParser.ComputeStyleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#computeStatement.
    def visitComputeStatement(self, ctx:ui_pythonParser.ComputeStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#webStatement.
    def visitWebStatement(self, ctx:ui_pythonParser.WebStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#tableRowStatement.
    def visitTableRowStatement(self, ctx:ui_pythonParser.TableRowStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#tableStatement.
    def visitTableStatement(self, ctx:ui_pythonParser.TableStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#tableColStatement.
    def visitTableColStatement(self, ctx:ui_pythonParser.TableColStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#dataTableStatement.
    def visitDataTableStatement(self, ctx:ui_pythonParser.DataTableStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#uiStatement.
    def visitUiStatement(self, ctx:ui_pythonParser.UiStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#uiPageStatement.
    def visitUiPageStatement(self, ctx:ui_pythonParser.UiPageStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#sqlAliasCol.
    def visitSqlAliasCol(self, ctx:ui_pythonParser.SqlAliasColContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#sqlAs.
    def visitSqlAs(self, ctx:ui_pythonParser.SqlAsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#selectCol.
    def visitSelectCol(self, ctx:ui_pythonParser.SelectColContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#selectColDef.
    def visitSelectColDef(self, ctx:ui_pythonParser.SelectColDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#selectStatementBody.
    def visitSelectStatementBody(self, ctx:ui_pythonParser.SelectStatementBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#sqlSelect.
    def visitSqlSelect(self, ctx:ui_pythonParser.SqlSelectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#selectStatement.
    def visitSelectStatement(self, ctx:ui_pythonParser.SelectStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#fromTableDef.
    def visitFromTableDef(self, ctx:ui_pythonParser.FromTableDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#sqlFrom.
    def visitSqlFrom(self, ctx:ui_pythonParser.SqlFromContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#fromStatement.
    def visitFromStatement(self, ctx:ui_pythonParser.FromStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#sqlOrder.
    def visitSqlOrder(self, ctx:ui_pythonParser.SqlOrderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#sqlByr.
    def visitSqlByr(self, ctx:ui_pythonParser.SqlByrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#sqlDesc.
    def visitSqlDesc(self, ctx:ui_pythonParser.SqlDescContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#orderByStatement.
    def visitOrderByStatement(self, ctx:ui_pythonParser.OrderByStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#colCompare.
    def visitColCompare(self, ctx:ui_pythonParser.ColCompareContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#jxSqlCompare.
    def visitJxSqlCompare(self, ctx:ui_pythonParser.JxSqlCompareContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#valueCompare.
    def visitValueCompare(self, ctx:ui_pythonParser.ValueCompareContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#sqlWhere.
    def visitSqlWhere(self, ctx:ui_pythonParser.SqlWhereContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#whereStatement.
    def visitWhereStatement(self, ctx:ui_pythonParser.WhereStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ui_pythonParser#sqlStatement.
    def visitSqlStatement(self, ctx:ui_pythonParser.SqlStatementContext):
        return self.visitChildren(ctx)



del ui_pythonParser