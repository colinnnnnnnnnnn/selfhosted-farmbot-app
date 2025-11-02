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
├── services/            # Business logic and API calls
│   ├── movementService.js         # Movement operations (move, nudge, home, unlock)
│   ├── photoService.js            # Photo operations (take, clear)
│   └── actionService.js           # Other actions (water, etc.)
├── utils/               # Utility functions and constants
│   ├── axiosConfig.js             # Axios setup with auth interceptor
│   └── constants.js               # Map dimensions and scaling constants
├── App.js               # Main application component (now just 245 lines!)
├── App-old.js           # Backup of the original monolithic App.js
├── LoginPage.js         # Login page component
└── ...
```

## Component Responsibilities

### Components (UI Layer)

- **BotVisibilityToggle**: Toggle switch to show/hide the FarmBot icon on the map
- **ControlButtons**: All action buttons (Get Position, Unlock, Water, Home, Take Photo, Clear Photos, Logout)
- **FarmBotMap**: Main map canvas with grid, photo overlays, and bot position
- **ManualJogPad**: D-pad interface for nudging the bot in small increments
- **MapOverlays**: Renders the bot icon and photo thumbnails on the map
- **MoveAbsoluteForm**: Form for moving to absolute X,Y,Z coordinates
- **MoveRelativeForm**: Form for moving relative to current position
- **StatusDisplay**: Shows current position, target position, and movement status

### Hooks (State Management)

- **useAuth**: Manages authentication state (login, logout, token storage)
- **useFarmBotPosition**: Fetches and manages the bot's current position
- **usePhotos**: Manages photo data and localStorage persistence

### Services (Business Logic)

- **movementService**: All movement operations
  - `getCurrentPosition()` - Get current bot position
  - `moveAbsolute()` - Move to absolute coordinates
  - `moveRelative()` - Move relative to current position
  - `nudge()` - Small incremental movements
  - `goHome()` - Return to home position
  - `unlock()` - Emergency unlock
  
- **photoService**: Photo management operations
  - `takePhoto()` - Capture and save a photo
  - `clearAllPhotos()` - Delete all photos
  
- **actionService**: Other FarmBot actions
  - `waterPlant()` - Activate watering

### Utils (Configuration & Constants)

- **axiosConfig**: Configures axios with authorization headers and API base URL
- **constants**: Defines map dimensions, scaling factors, and image sizes

## Benefits of This Structure

1. **Easier to Find Code**: Each file has a single, clear responsibility
2. **Separation of Concerns**: UI (components), state (hooks), logic (services) are separate
3. **Reusable Components**: Components and services can be easily reused
4. **Easier Testing**: Small, focused functions are easier to unit test
5. **Better Performance**: React can optimize re-renders better with smaller components
6. **Easier Collaboration**: Multiple developers can work on different files simultaneously
7. **Clearer Dependencies**: Import statements show exactly what each file needs
8. **Maintainable**: App.js reduced from 790 lines to 245 lines!

## Making Changes

### UI Changes
- **Adding a new control button**: Edit `components/ControlButtons.js`
- **Changing map appearance**: Edit `components/FarmBotMap.js` or `components/MapOverlays.js`
- **Modifying forms**: Edit `components/MoveAbsoluteForm.js` or `components/MoveRelativeForm.js`

### Logic Changes
- **Modifying movement behavior**: Edit `services/movementService.js`
- **Adding new movement operations**: Add new function to `services/movementService.js`
- **Photo handling logic**: Edit `services/photoService.js`
- **New FarmBot actions**: Add to `services/actionService.js`

### Configuration Changes
- **API endpoints**: Edit `utils/axiosConfig.js`
- **Map dimensions**: Edit `utils/constants.js`

### State Management
- **Authentication flow**: Edit `hooks/useAuth.js`
- **Position updates**: Edit `hooks/useFarmBotPosition.js`
- **Photo storage**: Edit `hooks/usePhotos.js`

## Backup

The original monolithic `App.js` has been saved as `App-old.js` in case you need to reference it.
