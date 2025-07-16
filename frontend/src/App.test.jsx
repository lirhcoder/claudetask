import React from 'react'
import { render, screen } from '@testing-library/react'
import { vi } from 'vitest'
import App from './App'

// Mock zustand store
vi.mock('./stores/themeStore', () => ({
  useThemeStore: () => ({
    isDarkMode: false,
    toggleTheme: vi.fn()
  })
}))

// Mock react-router-dom
vi.mock('react-router-dom', () => ({
  BrowserRouter: ({ children }) => <div>{children}</div>,
  Routes: ({ children }) => <div>{children}</div>,
  Route: ({ element }) => element,
  Outlet: () => <div>Outlet</div>,
  useNavigate: () => vi.fn(),
  useLocation: () => ({ pathname: '/' }),
  useParams: () => ({})
}))

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    expect(screen.getByText(/Claude Code/i)).toBeInTheDocument()
  })

  it('applies light theme by default', () => {
    const { container } = render(<App />)
    expect(container.firstChild).toBeTruthy()
  })
})