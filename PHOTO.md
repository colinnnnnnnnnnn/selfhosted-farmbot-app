Photo Model with fields:

image_path - Path to the stored image file
farmbot_id - FarmBot's image ID
created_at - Timestamp
coordinates - X,Y,Z coordinates where photo was taken
meta_data - Additional metadata

API Endpoints:

GET /api/photos/ - List all photos
GET /api/photos/<id>/ - Get specific photo details
DELETE /api/photos/<id>/ - Delete a photo (removes both database entry and file)
GET /api/take-photo/ - Take a new photo (now saves to Photo model)

PhotoModelSerializer provides:

Photo ID
Image URL (auto-generated from image path)
Created timestamp
Coordinates
Metadata