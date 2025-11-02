# Frontend Structure

The frontend has been refactored into a modular component structure for better maintainability.

## Directory Structure

```
src/
├── components/          # Reusable UI components
│   ├── BotVisibilityToggle.js    # Toggle to show/hide the bot on map
│   ├── ControlButtons.js          # Main control buttons (unlock, water, home, etc.)
│   ├── FarmBotMap.js              # The main map/grid component
│   ├── ManualJogPad.js            # D-pad for manual jogging
│   ├── MapOverlays.js             # Photo and bot overlays on the map
│   ├── MoveAbsoluteForm.js        # Form for absolute positioning
│   ├── MoveRelativeForm.js        # Form for relative movement
│   └── StatusDisplay.js           # Current position and status display
├── hooks/               # Custom React hooks
│   ├── useAuth.js                 # Authentication state management
│   ├── useFarmBotPosition.js     # Position fetching and management
│   └── usePhotos.js               # Photo data management with localStorage
├── utils/               # Utility functions and constants
│   ├── axiosConfig.js             # Axios setup with auth interceptor
│   └── constants.js               # Map dimensions and scaling constants
├── App.js               # Main application component
├── App-old.js           # Backup of the original monolithic App.js
├── LoginPage.js         # Login page component
└── ...
```

## Component Responsibilities

### Components

- **BotVisibilityToggle**: Toggle switch to show/hide the FarmBot icon on the map
- **ControlButtons**: All action buttons (Get Position, Unlock, Water, Home, Take Photo, Clear Photos, Logout)
- **FarmBotMap**: Main map canvas with grid, photo overlays, and bot position
- **ManualJogPad**: D-pad interface for nudging the bot in small increments
- **MapOverlays**: Renders the bot icon and photo thumbnails on the map
- **MoveAbsoluteForm**: Form for moving to absolute X,Y,Z coordinates
- **MoveRelativeForm**: Form for moving relative to current position
- **StatusDisplay**: Shows current position, target position, and movement status

### Hooks

- **useAuth**: Manages authentication state (login, logout, token storage)
- **useFarmBotPosition**: Fetches and manages the bot's current position
- **usePhotos**: Manages photo data and localStorage persistence

### Utils

- **axiosConfig**: Configures axios with authorization headers and API base URL
- **constants**: Defines map dimensions, scaling factors, and image sizes

## Benefits of This Structure

1. **Easier to Find Code**: Each component has a single, clear responsibility
2. **Reusable Components**: Components can be easily reused or modified
3. **Easier Testing**: Small, focused components are easier to test
4. **Better Performance**: React can optimize re-renders better with smaller components
5. **Easier Collaboration**: Multiple developers can work on different components simultaneously
6. **Clearer Dependencies**: Import statements show what each component needs

## Making Changes

- **Adding a new control button**: Edit `ControlButtons.js`
- **Changing map appearance**: Edit `FarmBotMap.js` or `MapOverlays.js`
- **Modifying movement logic**: Edit `App.js` or the specific form component
- **Adding new API calls**: Edit `axiosConfig.js` or create a new utility
- **Changing map dimensions**: Edit `constants.js`

## Backup

The original monolithic `App.js` has been saved as `App-old.js` in case you need to reference it.
