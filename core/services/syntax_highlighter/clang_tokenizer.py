import sys
import logging
import subprocess
import clang.cindex
from services.syntax_highlighter.token_identifier import TokenIdentifier

class ChildVisitResult(clang.cindex.BaseEnumeration):
    """
    A ChildVisitResult describes how the traversal of the children of a particular cursor should proceed after visiting a particular child cursor.
    """
    _kinds = []
    _name_map = None

    def __repr__(self):
        return 'ChildVisitResult.%s' % (self.name,)

ChildVisitResult.BREAK = ChildVisitResult(0) # Terminates the cursor traversal.
ChildVisitResult.CONTINUE = ChildVisitResult(1) # Continues the cursor traversal with the next sibling of the cursor just visited, without visiting its children.
ChildVisitResult.RECURSE = ChildVisitResult(2) # Recursively traverse the children of this cursor, using the same visitor and client data.

def default_visitor(child, parent, client_data):
    """Default implementation of AST node visitor."""

    return ChildVisitResult.CONTINUE.value

def traverse(self, client_data, client_visitor = default_visitor):
    """Traverse AST using the client provided visitor."""

    def visitor(child, parent, client_data):
        assert child != clang.cindex.conf.lib.clang_getNullCursor()
        child._tu = self._tu
        child.ast_parent = parent
        return client_visitor(child, parent, client_data)

    return clang.cindex.conf.lib.clang_visitChildren(self, clang.cindex.callbacks['cursor_visit'](visitor), client_data)

def get_children_patched(self):
    """
    Return an iterator for accessing the children of this cursor.
    This is a patched version of Cursor.get_children() but which is built on top of new traversal interface.
    See traverse() for more details.
    """

    def visitor(child, parent, children):
        children.append(child)
        return ChildVisitResult.CONTINUE.value

    children = []
    traverse(self, children, visitor)
    return iter(children)

"""
Monkey-patch the existing Cursor.get_children() with get_children_patched().
This is a temporary solution and should be removed once, and if, it becomes available in official libclang Python bindings.
New version provides more functionality (i.e. AST parent node) which is needed in certain cases.
"""
clang.cindex.Cursor.get_children = get_children_patched

def get_system_includes():
    output = subprocess.Popen(["g++", "-v", "-E", "-x", "c++", "-"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    pattern = ["#include <...> search starts here:", "End of search list."]
    output = str(output)
    return output[output.find(pattern[0]) + len(pattern[0]) : output.find(pattern[1])].replace(' ', '-I').split('\\n')

class ClangTokenizer():
    def __init__(self):
        self.filename = ''
        self.token_list = []
        self.index = clang.cindex.Index.create()
        self.default_args = ['-x', 'c++', '-std=c++14'] + get_system_includes()

    def run(self, filename, compiler_args, project_root_directory):
        self.filename = filename
        self.token_list = []
        logging.info('Filename = {0}'.format(self.filename))
        logging.info('Default args = {0}'.format(self.default_args))
        logging.info('User-provided compiler args = {0}'.format(compiler_args))
        logging.info('Compiler working-directory = {0}'.format(project_root_directory))
        translation_unit = self.index.parse(
            path = self.filename,
            args = self.default_args + compiler_args + ['-working-directory=' + project_root_directory],
            options = clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
        )

        diag = translation_unit.diagnostics
        for d in diag:
            logging.info('Parsing error: ' + str(d))

        logging.info('Translation unit: '.format(translation_unit.spelling))
        self.__visit_all_nodes(translation_unit.cursor)

    def get_token_list(self):
        return self.token_list

    def get_token_id(self, token):
        # CursorKind.OVERLOADED_DECL_REF basically identifies a reference to a set of overloaded functions
        # or function templates which have not yet been resolved to a specific function or function template.
        # This means that token kind might be one of the following:
        #   CursorKind.FUNCTION_DECL, CursorKind.FUNCTION_TEMPLATE, CursorKind.CXX_METHOD
        # To extract more information about the token we can use `clang_getNumOverloadedDecls()` to get how
        # many overloads there are and then use `clang_getOverloadedDecl()` to get a specific overload.
        # In our case, we can always use the first overload which explains hard-coded 0 as an index.
        if token.referenced:
            if (token.referenced.kind == clang.cindex.CursorKind.OVERLOADED_DECL_REF):
                if (ClangTokenizer.__get_num_overloaded_decls(token.referenced)):
                    return ClangTokenizer.to_token_id(ClangTokenizer.__get_overloaded_decl(token.referenced, 0).kind)
            return ClangTokenizer.to_token_id(token.referenced.kind)
        if (token.kind == clang.cindex.CursorKind.OVERLOADED_DECL_REF):
            if (ClangTokenizer.__get_num_overloaded_decls(token)):
                return ClangTokenizer.to_token_id(ClangTokenizer.__get_overloaded_decl(token, 0).kind)
        return ClangTokenizer.to_token_id(token.kind)

    def get_token_name(self, token):
        if (token.referenced):
            return token.referenced.spelling
        else:
            return token.spelling

    def get_token_line(self, token):
        return token.location.line

    def get_token_column(self, token):
        return token.location.column

    def dump_token_list(self):
        for idx, token in enumerate(self.token_list):
            logging.debug(
                '%-12s' % ('[' + str(token.location.line) + ', ' + str(token.location.column) + ']') +
                '%-40s ' % str(token.spelling) +
                '%-40s ' % str(token.kind) +
                ('%-40s ' % str(ClangTokenizer.__get_overloaded_decl(token, 0).spelling) if (token.kind ==
                    clang.cindex.CursorKind.OVERLOADED_DECL_REF and ClangTokenizer.__get_num_overloaded_decls(token)) else '') +
                ('%-40s ' % str(ClangTokenizer.__get_overloaded_decl(token, 0).kind) if (token.kind ==
                    clang.cindex.CursorKind.OVERLOADED_DECL_REF and ClangTokenizer.__get_num_overloaded_decls(token)) else '') +
                ('%-40s ' % str(token.referenced.spelling) if (token.referenced) else '') +
                ('%-40s ' % str(token.referenced.kind) if (token.referenced) else ''))
                #('%-40s ' % str(token.referenced.type.spelling) if (token.referenced) else '') +
                #('%-40s ' % str(token.referenced.result_type.spelling) if (token.referenced) else '') +
                #('%-40s ' % str(token.referenced.canonical.spelling) if (token.referenced) else '') +
                #('%-40s ' % str(token.referenced.canonical.kind) if (token.referenced) else '') +
                #('%-40s ' % str(token.referenced.semantic_parent.spelling) if (token.referenced and token.referenced.semantic_parent) else '') +
                #('%-40s ' % str(token.referenced.semantic_parent.kind) if (token.referenced and token.referenced.semantic_parent) else '') +
                #('%-40s ' % str(token.referenced.lexical_parent.spelling) if (token.referenced and token.referenced.lexical_parent) else '') +
                #('%-40s ' % str(token.referenced.lexical_parent.kind) if (token.referenced and token.referenced.lexical_parent) else ''))

    def __visit_all_nodes(self, node):
        for n in node.get_children():
            if n.location.file and n.location.file.name == self.filename:
                self.token_list.append(n)
                self.__visit_all_nodes(n)

    @staticmethod
    def to_token_id(kind):
        if (kind == clang.cindex.CursorKind.NAMESPACE):
            return TokenIdentifier.getNamespaceId()
        if (kind in [clang.cindex.CursorKind.CLASS_DECL, clang.cindex.CursorKind.CLASS_TEMPLATE, clang.cindex.CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION]):
            return TokenIdentifier.getClassId()
        if (kind == clang.cindex.CursorKind.STRUCT_DECL):
            return TokenIdentifier.getStructId()
        if (kind == clang.cindex.CursorKind.ENUM_DECL):
            return TokenIdentifier.getEnumId()
        if (kind == clang.cindex.CursorKind.ENUM_CONSTANT_DECL):
            return TokenIdentifier.getEnumValueId()
        if (kind == clang.cindex.CursorKind.UNION_DECL):
            return TokenIdentifier.getUnionId()
        if (kind == clang.cindex.CursorKind.FIELD_DECL):
            return TokenIdentifier.getFieldId()
        if (kind == clang.cindex.CursorKind.VAR_DECL):
            return TokenIdentifier.getLocalVariableId()
        if (kind in [clang.cindex.CursorKind.FUNCTION_DECL, clang.cindex.CursorKind.FUNCTION_TEMPLATE]):
            return TokenIdentifier.getFunctionId()
        if (kind in [clang.cindex.CursorKind.CXX_METHOD, clang.cindex.CursorKind.CONSTRUCTOR, clang.cindex.CursorKind.DESTRUCTOR]):
            return TokenIdentifier.getMethodId()
        if (kind == clang.cindex.CursorKind.PARM_DECL):
            return TokenIdentifier.getFunctionParameterId()
        if (kind == clang.cindex.CursorKind.TEMPLATE_TYPE_PARAMETER):
            return TokenIdentifier.getTemplateTypeParameterId()
        if (kind == clang.cindex.CursorKind.TEMPLATE_NON_TYPE_PARAMETER):
            return TokenIdentifier.getTemplateNonTypeParameterId()
        if (kind == clang.cindex.CursorKind.TEMPLATE_TEMPLATE_PARAMETER):
            return TokenIdentifier.getTemplateTemplateParameterId()
        if (kind == clang.cindex.CursorKind.MACRO_DEFINITION):
            return TokenIdentifier.getMacroDefinitionId()
        if (kind == clang.cindex.CursorKind.MACRO_INSTANTIATION):
            return TokenIdentifier.getMacroInstantiationId()
        if (kind in [clang.cindex.CursorKind.TYPEDEF_DECL, clang.cindex.CursorKind.TYPE_ALIAS_DECL]):
            return TokenIdentifier.getTypedefId()
        if (kind == clang.cindex.CursorKind.NAMESPACE_ALIAS):
            return TokenIdentifier.getNamespaceAliasId()
        if (kind == clang.cindex.CursorKind.USING_DIRECTIVE):
            return TokenIdentifier.getUsingDirectiveId()
        if (kind == clang.cindex.CursorKind.USING_DECLARATION):
            return TokenIdentifier.getUsingDeclarationId()
        return TokenIdentifier.getUnsupportedId()

    # TODO Shall be removed once 'cindex.py' exposes it in its interface.
    @staticmethod
    def __get_num_overloaded_decls(cursor):
        return clang.cindex.conf.lib.clang_getNumOverloadedDecls(cursor)

    # TODO Shall be removed once 'cindex.py' exposes it in its interface.
    @staticmethod
    def __get_overloaded_decl(cursor, num):
        return clang.cindex.conf.lib.clang_getOverloadedDecl(cursor, num)

