# Claude Code Web Application

A web-based interface for Claude Code that enables remote code generation and project management through a browser.

## Features

- 🚀 **Real-time Code Execution**: Execute Claude Code commands with live output streaming
- 📁 **Project Management**: Create, manage, and organize multiple projects
- 💻 **Code Editor**: Built-in Monaco editor with syntax highlighting
- 🔄 **Real-time Updates**: WebSocket-based real-time communication
- 📊 **Task History**: Track and review all executed tasks
- 🎨 **Modern UI**: Clean, responsive interface with dark mode support

## Architecture

### Backend (Flask + Python)
- RESTful API for project and task management
- Socket.IO for real-time communication
- Multi-threaded task executor
- File management service
- SQLite database for task persistence

### Frontend (React + Vite)
- Modern React with hooks and functional components
- Ant Design UI components
- Monaco Editor for code viewing
- Socket.IO client for real-time updates
- Zustand for state management

## Prerequisites

- Python 3.8+
- Node.js 16+
- Claude Code CLI installed and accessible

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd claudetask
```

2. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
cd ..
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

## Configuration

### Backend Configuration

Edit `backend/config.py` or set environment variables:

- `CLAUDE_CODE_PATH`: Path to Claude Code executable (default: 'claude')
- `MAX_CONCURRENT_TASKS`: Maximum concurrent tasks (default: 5)
- `PROJECTS_DIR`: Directory for project storage (default: './projects')

### Frontend Configuration

The frontend is configured to proxy API requests to the backend on port 5000.

## Running the Application

### Development Mode

Use the provided startup script:
```bash
./start.sh development
```

Or run manually:

Backend:
```bash
cd backend
python app.py
```

Frontend:
```bash
cd frontend
npm run dev
```

Access the application at http://localhost:3000

### Production Mode

```bash
./start.sh production
```

This will:
- Build the frontend for production
- Start the backend with Gunicorn

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## API Documentation

### REST Endpoints

- `POST /api/execute` - Execute Claude Code
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create new project
- `GET /api/projects/:name` - Get project details
- `GET /api/tasks` - List all tasks
- `GET /api/tasks/:id` - Get task details
- `POST /api/tasks/:id/cancel` - Cancel running task
- `POST /api/files/upload` - Upload file to project
- `GET /api/files/:path` - Get file content

### WebSocket Events

Client → Server:
- `execute_code` - Execute Claude Code
- `subscribe_task` - Subscribe to task updates
- `cancel_task` - Cancel running task

Server → Client:
- `task_output` - Real-time task output
- `task_complete` - Task completion notification
- `task_state` - Current task state

## Project Structure

```
claudetask/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration
│   ├── routes/             # API routes
│   ├── services/           # Business logic
│   ├── models/             # Data models
│   ├── utils/              # Utilities
│   └── tests/              # Backend tests
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── stores/         # State management
│   │   └── App.jsx         # Main app component
│   └── package.json
├── start.sh                # Startup script
└── README.md
```

## Security Considerations

- Input validation for all user inputs
- Path traversal protection
- File type restrictions for uploads
- Command injection prevention
- CORS configuration for production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

[Your License Here]

## Troubleshooting

### Common Issues

1. **Claude Code not found**: Ensure Claude Code is installed and the path is correctly configured
2. **Port already in use**: Change the port in the configuration or kill the process using the port
3. **WebSocket connection failed**: Check that both frontend and backend are running and CORS is configured

### Logs

- Backend logs: Console output or configure logging in `app.py`
- Frontend logs: Browser developer console

## Future Enhancements

- User authentication and authorization
- Project templates
- Collaborative features
- VS Code extension
- Docker deployment
- CI/CD pipeline