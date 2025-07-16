import React, { useEffect, useState, useRef } from 'react'
import { Tag, Spin } from 'antd'
import { useSocketStore } from '../stores/socketStore'

const TaskOutput = ({ task }) => {
  const [output, setOutput] = useState('')
  const [status, setStatus] = useState(task?.status || 'pending')
  const outputRef = useRef(null)
  const { socket } = useSocketStore()

  useEffect(() => {
    if (!socket || !task) return

    const handleTaskOutput = (data) => {
      if (data.task_id === task.id) {
        setOutput(prev => prev + data.line + '\n')
      }
    }

    const handleTaskComplete = (data) => {
      if (data.task_id === task.id) {
        setStatus(data.status)
        if (data.output && !output) {
          setOutput(data.output)
        }
      }
    }

    const handleTaskState = (data) => {
      if (data.id === task.id) {
        setStatus(data.status)
        if (data.output) {
          setOutput(data.output)
        }
      }
    }

    socket.on('task_output', handleTaskOutput)
    socket.on('task_complete', handleTaskComplete)
    socket.on('task_state', handleTaskState)

    return () => {
      socket.off('task_output', handleTaskOutput)
      socket.off('task_complete', handleTaskComplete)
      socket.off('task_state', handleTaskState)
    }
  }, [socket, task])

  useEffect(() => {
    // Auto-scroll to bottom
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight
    }
  }, [output])

  const getStatusTag = () => {
    const statusConfig = {
      pending: { color: 'default', text: 'Pending' },
      running: { color: 'processing', text: 'Running' },
      completed: { color: 'success', text: 'Completed' },
      failed: { color: 'error', text: 'Failed' },
      cancelled: { color: 'warning', text: 'Cancelled' }
    }
    
    const config = statusConfig[status] || statusConfig.pending
    return <Tag color={config.color}>{config.text}</Tag>
  }

  if (!task) {
    return <div style={{ padding: 20, textAlign: 'center', color: '#999' }}>No task running</div>
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ marginBottom: 8 }}>
        Status: {getStatusTag()}
        {status === 'running' && <Spin size="small" style={{ marginLeft: 8 }} />}
      </div>
      <div
        ref={outputRef}
        style={{
          flex: 1,
          background: '#f5f5f5',
          padding: 12,
          borderRadius: 4,
          fontFamily: 'monospace',
          fontSize: 12,
          overflow: 'auto',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word'
        }}
      >
        {output || 'Waiting for output...'}
      </div>
    </div>
  )
}

export default TaskOutput