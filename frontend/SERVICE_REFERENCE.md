# Service Functions Reference

Quick reference for all service functions available in the application.

## Movement Service (`services/movementService.js`)

### `getCurrentPosition()`
Fetches the current position from the FarmBot API.

**Returns:** `Promise<[x, y, z]>` - Array of coordinates

**Example:**
```javascript
const position = await getCurrentPosition();
// Returns: [100, 200, 0]
```

---

### `moveAbsolute(target, setPosition, setTargetPosition, setMoveStatus)`
Moves the FarmBot to an absolute position with position tracking.

**Parameters:**
- `target` - Object with `{ x, y, z, speed }`
- `setPosition` - State setter for current position
- `setTargetPosition` - State setter for target position
- `setMoveStatus` - State setter for status messages

**Example:**
```javascript
const target = { x: 100, y: 200, z: 0, speed: 100 };
await moveAbsolute(target, setPosition, setTargetPosition, setMoveStatus);
```

---

### `moveRelative(delta, position, setPosition, setTargetPosition, setMoveStatus)`
Moves the FarmBot relative to its current position.

**Parameters:**
- `delta` - Object with `{ x, y, z, speed }` (relative offsets)
- `position` - Current position object
- `setPosition` - State setter for current position
- `setTargetPosition` - State setter for target position
- `setMoveStatus` - State setter for status messages

**Example:**
```javascript
const delta = { x: 10, y: -5, z: 0, speed: 50 };
await moveRelative(delta, position, setPosition, setTargetPosition, setMoveStatus);
```

---

### `nudge(step, speed, position, setPosition, setTargetPosition, setMoveStatus)`
Performs a small incremental movement (for manual jogging).

**Parameters:**
- `step` - Object with `{ x, y, z }` (small offsets, typically ±5)
- `speed` - Movement speed (0-100)
- `position` - Current position object
- `setPosition` - State setter for current position
- `setTargetPosition` - State setter for target position
- `setMoveStatus` - State setter for status messages

**Example:**
```javascript
const step = { x: 5, y: 0, z: 0 };
await nudge(step, 100, position, setPosition, setTargetPosition, setMoveStatus);
```

---

### `goHome(setPosition, setTargetPosition, setMoveStatus)`
Moves the FarmBot to its home position (0, 0, 0).

**Parameters:**
- `setPosition` - State setter for current position
- `setTargetPosition` - State setter for target position
- `setMoveStatus` - State setter for status messages

**Example:**
```javascript
await goHome(setPosition, setTargetPosition, setMoveStatus);
```

---

### `unlock(setMoveStatus)`
Performs an emergency unlock on the FarmBot.

**Parameters:**
- `setMoveStatus` - State setter for status messages

**Example:**
```javascript
await unlock(setMoveStatus);
```

---

## Photo Service (`services/photoService.js`)

### `takePhoto(position, photoData, setPhotoData, savePhotos, setMoveStatus)`
Takes a photo and saves it with metadata.

**Parameters:**
- `position` - Current bot position
- `photoData` - Current array of photos
- `setPhotoData` - State setter for photo array
- `savePhotos` - Function to save photos to localStorage
- `setMoveStatus` - State setter for status messages

**Returns:** `Promise<Photo>` - The new photo object

**Example:**
```javascript
const newPhoto = await takePhoto(position, photoData, setPhotoData, savePhotos, setMoveStatus);
```

---

### `clearAllPhotos(photoData, clearPhotos, setMoveStatus)`
Clears all photos from storage and backend.

**Parameters:**
- `photoData` - Current array of photos
- `clearPhotos` - Function to clear photos from state/localStorage
- `setMoveStatus` - State setter for status messages

**Example:**
```javascript
await clearAllPhotos(photoData, clearPhotos, setMoveStatus);
```

---

## Action Service (`services/actionService.js`)

### `waterPlant(setMoveStatus)`
Activates the watering system at the current position.

**Parameters:**
- `setMoveStatus` - State setter for status messages

**Example:**
```javascript
await waterPlant(setMoveStatus);
```

---

## Usage Tips

1. **Always await service calls** - They are all async functions
2. **Error handling** - Service functions throw errors, wrap in try-catch if needed
3. **Status updates** - Most functions update moveStatus automatically
4. **Position tracking** - Movement functions handle position polling automatically

## Adding New Services

To add a new service function:

1. Identify the category (movement, photo, action)
2. Add the function to the appropriate service file
3. Export it from that file
4. Import it in `App.js`
5. Create a handler function in `App.js` that calls it
6. Update this documentation

**Example:**
```javascript
// In services/actionService.js
export const plantSeed = async (setMoveStatus) => {
  try {
    setMoveStatus('Planting seed');
    await axios.post(`${API_BASE}/seed-injector/`);
    setMoveStatus('Seed planted');
  } catch (error) {
    setMoveStatus('Planting failed');
    throw error;
  }
};

// In App.js
import { waterPlant, plantSeed } from './services/actionService';

const handlePlantSeed = async () => {
  await plantSeed(setMoveStatus);
};
```
