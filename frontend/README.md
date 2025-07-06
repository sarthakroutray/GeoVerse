# GeoVerse Frontend 🌐

React-based frontend for the GeoVerse AI-powered geospatial question-answering system.

## 🎯 Overview

A modern, responsive React application that provides an intuitive interface for interacting with geospatial data through natural language queries.

## 🛠️ Technology Stack

- **Framework**: React 18
- **Styling**: Tailwind CSS
- **State Management**: Redux Toolkit
- **HTTP Client**: Axios
- **Routing**: React Router v6
- **UI Components**: Custom components with Tailwind
- **Charts/Maps**: Recharts, Leaflet
- **Testing**: Jest, React Testing Library

## 📁 Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # Reusable components
│   │   ├── Chat/       # Chat interface components
│   │   ├── Search/     # Search functionality
│   │   ├── Layout/     # Layout components
│   │   └── Common/     # Shared components
│   ├── pages/          # Page components
│   ├── services/       # API and external services
│   ├── hooks/          # Custom React hooks
│   ├── store/          # Redux store and slices
│   ├── utils/          # Utility functions
│   └── styles/         # Global styles
├── build/              # Production build
└── tests/              # Test files
```

## 🚦 Getting Started

### Prerequisites
- Node.js 16+
- npm or yarn

### Installation

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your backend API URL
   ```

3. **Start development server**
   ```bash
   npm start
   ```

   The app will open at http://localhost:3000

### Environment Variables
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws
REACT_APP_VERSION=1.0.0
```

## 🎨 UI/UX Features

### Chat Interface
- Real-time messaging with WebSocket support
- Message history and persistence
- Typing indicators and message status
- Rich media support (images, charts, maps)

### Search Functionality
- Advanced search with filters
- Auto-suggestions and autocompletion
- Result categorization and sorting
- Visual result previews

### Responsive Design
- Mobile-first approach
- Touch-friendly interface
- Progressive Web App (PWA) capabilities
- Offline mode support

## 🔧 Development

### Component Structure
```jsx
// Example component structure
import React from 'react';
import PropTypes from 'prop-types';

const ComponentName = ({ prop1, prop2 }) => {
  return (
    <div className="component-wrapper">
      {/* Component content */}
    </div>
  );
};

ComponentName.propTypes = {
  prop1: PropTypes.string.isRequired,
  prop2: PropTypes.number,
};

export default ComponentName;
```

### State Management
Using Redux Toolkit for global state:

```javascript
// store/slices/chatSlice.js
import { createSlice } from '@reduxjs/toolkit';

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [],
    isLoading: false,
    error: null,
  },
  reducers: {
    addMessage: (state, action) => {
      state.messages.push(action.payload);
    },
    setLoading: (state, action) => {
      state.isLoading = action.payload;
    },
  },
});
```

### API Integration
```javascript
// services/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatAPI = {
  sendMessage: (message) => api.post('/api/v1/chat', { message }),
  getHistory: () => api.get('/api/v1/chat/history'),
};
```

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch

# Run specific test file
npm test ChatInterface.test.js
```

### Test Structure
```javascript
// components/Chat/__tests__/ChatInterface.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import ChatInterface from '../ChatInterface';
import store from '../../../store';

describe('ChatInterface', () => {
  test('renders chat interface', () => {
    render(
      <Provider store={store}>
        <ChatInterface />
      </Provider>
    );
    
    expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
  });
});
```

## 🎨 Styling Guidelines

### Tailwind CSS Classes
- Use Tailwind utility classes
- Create custom components for repeated patterns
- Maintain consistent spacing and colors
- Follow mobile-first responsive design

```jsx
// Example styling
<div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
  <h1 className="text-3xl font-bold text-gray-900 mb-4">
    GeoVerse Chat
  </h1>
  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
    {/* Content */}
  </div>
</div>
```

### Custom CSS
```css
/* styles/components.css */
.chat-message {
  @apply p-4 rounded-lg mb-4 max-w-lg;
}

.chat-message--user {
  @apply bg-blue-500 text-white ml-auto;
}

.chat-message--bot {
  @apply bg-gray-100 text-gray-900 mr-auto;
}
```

## 📦 Build & Deployment

### Production Build
```bash
npm run build
```

### Docker Deployment
```bash
docker build -t geoverse-frontend .
docker run -p 3000:3000 geoverse-frontend
```

### Environment-specific Builds
```bash
# Staging
npm run build:staging

# Production
npm run build:production
```

## 🔌 Key Components

### ChatInterface
- Real-time chat functionality
- Message rendering and formatting
- File upload support
- WebSocket integration

### SearchBar
- Advanced search with filters
- Auto-suggestions
- Search history
- Voice search support

### ResultsDisplay
- Grid and list view options
- Pagination and infinite scroll
- Result filtering and sorting
- Export functionality

### MapComponent
- Interactive geospatial visualization
- Layer management
- Custom markers and overlays
- Integration with search results

## 🚀 Performance Optimization

### Code Splitting
```javascript
// Lazy loading components
const ChatPage = lazy(() => import('./pages/Chat'));
const SearchPage = lazy(() => import('./pages/Search'));
```

### Memoization
```javascript
// Optimizing re-renders
const MemoizedComponent = React.memo(Component);
const memoizedValue = useMemo(() => computeExpensiveValue(a, b), [a, b]);
```

### Bundle Analysis
```bash
npm run analyze
```

## 🤝 Contributing

### Code Style
- Use ESLint and Prettier for code formatting
- Follow React best practices
- Write meaningful component and variable names
- Use TypeScript for better type safety (future enhancement)

### Git Workflow
1. Create feature branch from `main`
2. Implement feature with tests
3. Submit pull request
4. Code review and merge

## 📱 Progressive Web App

The frontend is configured as a PWA with:
- Service worker for offline functionality
- App manifest for installation
- Caching strategies for API responses
- Background sync for offline actions

## 🐛 Common Issues

### API Connection
- Check `REACT_APP_API_URL` in `.env`
- Verify backend server is running
- Check browser console for CORS errors

### State Management
- Use Redux DevTools for debugging
- Check action dispatching and state updates
- Verify reducer logic

### Styling Issues
- Clear browser cache after Tailwind changes
- Check for conflicting CSS classes
- Verify responsive breakpoints

## 📞 Support

For frontend-specific issues:
- Check browser developer console
- Review network tab for API calls
- Test with React Developer Tools
- Check Redux state in DevTools
