import { create } from 'zustand'
import { io } from 'socket.io-client'

export const useSocketStore = create((set, get) => ({
  socket: null,
  connected: false,
  
  connectSocket: () => {
    const socket = io('/', {
      transports: ['websocket'],
      autoConnect: true,
    })
    
    socket.on('connect', () => {
      console.log('Socket connected')
      set({ connected: true })
    })
    
    socket.on('disconnect', () => {
      console.log('Socket disconnected')
      set({ connected: false })
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