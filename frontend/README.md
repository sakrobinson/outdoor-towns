# OutdoorTowns Frontend

## Project Vision
OutdoorTowns is a platform designed to help outdoor enthusiasts discover and evaluate communities based on their outdoor recreation opportunities. Similar to nomadlist.com for digital nomads, OutdoorTowns helps people find their ideal location for an outdoor-focused lifestyle.

### Core Problem
Finding the perfect town for outdoor activities is challenging without living there first. Current solutions are fragmented across various websites, forums, and personal recommendations, making it difficult to make informed decisions.

### Solution
A comprehensive platform that:
1. Aggregates data about outdoor recreation opportunities
2. Provides community-driven insights and ratings
3. Enables detailed location comparison
4. Connects users with local outdoor communities

## Development Plan

### Phase 1: MVP (Current Phase)
**Goal**: Basic location discovery and evaluation
- Basic location database & search
- Essential location attributes
- Map integration
- Simple upvoting/downvoting system

#### Key Features
- Interactive map showing locations
- Location cards with basic information
- Search and filter functionality
- Basic attribute scoring system

### Phase 2: Community & Premium Features
**Goal**: User engagement and initial monetization
- User authentication
- Community reviews and comments
- Premium features (advanced filtering, detailed analytics)
- Save favorite locations
- Compare locations side by side
- API integration from MountainProject, Mountain Bike project, powder project, etc(scrape)


### Phase 3: Advanced Features
**Goal**: Enhanced user experience and community building
- Local expert insights
- Seasonal reports
- Community forums
- Mobile app development
- API access for developers

## Tech Stack
- **Frontend Framework**: React.js
- **UI Components**: Material-UI
- **Mapping**: Mapbox GL JS
- **State Management**: Context API (Redux if needed)
- **API Integration**: Axios
- **Authentication**: Auth0
- **Payment Processing**: Stripe

## Getting Started

### Prerequisites
- Node.js (v14 or higher)
- npm (v6 or higher)
- Git

## Key Components

### Map View
- Interactive map showing location markers
- Cluster markers for dense areas
- Popup information on hover/click

### Location Cards
- Summary of key attributes
- Quick action buttons
- Visual scoring indicators

### Search & Filter
- Location search
- Activity type filters
- Attribute-based filtering
- Score range filters


## Development Guidelines

### Code Style
- Follow React best practices
- Use functional components with hooks
- Implement proper error handling
- Write meaningful comments
- Use TypeScript for new features

### Component Structure
- Keep components small and focused
- Use proper prop validation
- Implement error boundaries
- Follow atomic design principles

### State Management
- Use Context API for global state
- Keep component state local when possible
- Implement proper loading states
- Handle errors gracefully

## Contributing
1. Create a feature branch
2. Implement changes
3. Write/update tests
4. Submit pull request
5. Code review process
