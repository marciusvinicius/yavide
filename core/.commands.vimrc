" """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Project commands
" """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
:command! -nargs=0 -complete=file YavideProjectNew                   :call Y_Project_New(1)
:command! -nargs=0 -complete=file YavideProjectOpen                  :call Y_Project_Open()
:command! -nargs=0 -complete=file YavideProjectImport                :call Y_Project_New(0)
:command! -nargs=0 -complete=file YavideProjectClose                 :call Y_Project_Close()
:command! -nargs=0 -complete=file YavideProjectSave                  :call Y_Project_Save()
:command! -nargs=0 -complete=file YavideProjectDelete                :call Y_Project_Delete()

" """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Layout commands
" """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
:command! -nargs=0 -complete=file YavideLayoutRefresh                :call Y_Layout_Refresh()

" """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Search commands
" """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
:command! -nargs=0 -complete=file YavidePromptFind                   :call Y_Prompt_Find()
:command! -nargs=0 -complete=file YavidePromptFindAndReplace         :call Y_Prompt_FindAndReplace()

" """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Buffer commands
" """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
:command! -nargs=0 -complete=file YavideBufferSave                   :call Y_Buffer_Save('%')
:command! -nargs=0 -complete=file YavideBufferClose                  :call Y_Buffer_Close('%', 0)
:command! -nargs=0 -complete=file YavideBufferCloseAllButCurrentOne  :call Y_Buffer_CloseAllButCurrentOne(0)
:command! -nargs=0 -complete=file YavideBufferCloseAll               :call Y_Buffer_CloseAll(0)
:command! -nargs=0 -complete=file YavideBufferPrev                   :call Y_Buffer_GoTo(0)
:command! -nargs=0 -complete=file YavideBufferNext                   :call Y_Buffer_GoTo(1)
:command! -nargs=0 -complete=file YavideBufferScrollUp               :call Y_Buffer_Scroll(0)
:command! -nargs=0 -complete=file YavideBufferScrollDown             :call Y_Buffer_Scroll(1)

" """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Buffer editing commands
" """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
:command! -nargs=0 -complete=file YavideTextSelectAll                :call Y_Text_SelectAll()
:command! -nargs=0 -complete=file YavideTextCut                      :call Y_Text_Cut()
:command! -nargs=0 -complete=file YavideTextCopy                     :call Y_Text_Copy()
:command! -nargs=0 -complete=file YavideTextPaste                    :call Y_Text_Paste()
:command! -nargs=0 -complete=file YavideTextUndo                     :call Y_Text_Undo()
:command! -nargs=0 -complete=file YavideTextRedo                     :call Y_Text_Redo()

" """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Source code navigation commands
" """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
:command! -nargs=0 -complete=file YavideSrcNavOpenFile                      CxxdGoToInclude
:command! -nargs=0 -complete=file YavideSrcNavGoToDefinition                CxxdGoToDefinition
:command! -nargs=0 -complete=file YavideSrcNavFindAllReferences             CxxdFindAllReferences
:command! -nargs=0 -complete=file YavideSrcNavRebuildIndex                  CxxdRebuildIndex
:command! -nargs=0 -complete=file YavideSrcNavSwitchBetweenHeaderImpl       :call Y_SrcNav_SwitchBetweenHeaderImpl(0)
:command! -nargs=0 -complete=file YavideSrcNavSwitchBetweenHeaderImplVSplit :call Y_SrcNav_SwitchBetweenHeaderImpl(1)

" """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Source code static analysis commands
" """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
:command! -nargs=* -complete=file YavideAnalyzerCppCheck                :call Y_Analyzer_RunCppCheck(".", <f-args>)
:command! -nargs=* -complete=file YavideAnalyzerCppCheckBuf             :call Y_Analyzer_RunCppCheck("%", <f-args>)
:command! -nargs=* -complete=file YavideAnalyzerClangCheck              :call Y_Analyzer_RunClangChecker("." <f-args>)
:command! -nargs=* -complete=file YavideAnalyzerClangTidyBuf            CxxdAnalyzerClangTidyBuf
:command! -nargs=* -complete=file YavideAnalyzerClangTidyApplyFixesBuf  CxxdAnalyzerClangTidyApplyFixesBuf

" """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Build commands
" """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
:command! -nargs=+ -complete=file YavideBuildRun                     CxxdBuildRun

