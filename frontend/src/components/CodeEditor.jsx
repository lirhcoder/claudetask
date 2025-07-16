import React from 'react'
import Editor from '@monaco-editor/react'
import { useThemeStore } from '../stores/themeStore'

const CodeEditor = ({ value, onChange, language = 'javascript', path, readOnly = false }) => {
  const { isDarkMode } = useThemeStore()

  return (
    <Editor
      height="100%"
      language={language}
      value={value}
      onChange={onChange}
      theme={isDarkMode ? 'vs-dark' : 'light'}
      path={path}
      options={{
        readOnly,
        minimap: { enabled: false },
        fontSize: 14,
        wordWrap: 'on',
        automaticLayout: true,
        formatOnPaste: true,
        formatOnType: true,
      }}
    />
  )
}

export default CodeEditor