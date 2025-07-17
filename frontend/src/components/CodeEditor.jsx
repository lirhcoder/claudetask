import React from 'react'
import Editor from '@monaco-editor/react'
import { useThemeStore } from '../stores/themeStore'

const CodeEditor = ({ value, onChange, language = 'javascript', path, readOnly = false, options = {} }) => {
  const { isDarkMode } = useThemeStore()

  const defaultOptions = {
    readOnly,
    minimap: { enabled: false },
    fontSize: 14,
    wordWrap: 'on',
    automaticLayout: true,
    formatOnPaste: true,
    formatOnType: true,
    scrollBeyondLastLine: false,
    renderWhitespace: 'selection',
    lineHeight: 20,
    padding: { top: 10, bottom: 10 },
    ...options
  }

  return (
    <Editor
      height="100%"
      language={language}
      value={value}
      onChange={onChange}
      theme={isDarkMode ? 'vs-dark' : 'light'}
      path={path}
      options={defaultOptions}
    />
  )
}

export default CodeEditor