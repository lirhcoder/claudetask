import { create } from 'zustand'
import { io } from 'socket.io-client'

export const useSocketStore = create((set, get) => ({
  socket: null,
  connected: false,
  
  connectSocket: () => {
    // 检查是否禁用了 Socket.IO
    if (import.meta.env.VITE_ENABLE_SOCKET === 'false') {
      console.log('Socket.IO is disabled via environment variable');
      return null;
    }
    
    // 如果已经连接，先断开
    const existingSocket = get().socket
    if (existingSocket) {
      existingSocket.disconnect()
    }
    
    const socket = io('/', {
      transports: ['websocket', 'polling'],
      autoConnect: true,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      timeout: 20000,
    })
    
    socket.on('connect', () => {
      console.log('Socket connected')
      set({ connected: true })
    })
    
    socket.on('disconnect', () => {
      console.log('Socket disconnected')
      set({ connected: false })
    })
    
    socket.on('connect_error', (error) => {
      console.log('Socket connection error:', error.message)
      // 如果是后端未启动，不要一直重试
      if (error.message.includes('ECONNREFUSED')) {
        console.log('Backend server is not running')
        socket.io.opts.reconnection = false
      }
    })
    
    socket.on('connected', (data) => {
      console.log('Server acknowledged connection:', data)
    })
    
    set({ socket })
    
    return socket
  },
  
  disconnectSocket: () => {
    const { socket } = get()
    if (socket) {
      socket.disconnect()
      set({ socket: null, connected: false })
    }
  },
}))