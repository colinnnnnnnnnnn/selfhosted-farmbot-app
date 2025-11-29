from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import Photo
from django.utils import timezone


class PhotoPaginationTestCase(TestCase):
    """Test cases for photo pagination"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test photos
        for i in range(55):  # More than default page size
            Photo.objects.create(
                image_path=f"farm_images/test_image_{i}.jpg",
                farmbot_id=1000 + i,
                created_at=timezone.now(),
                coordinates={'x': i, 'y': i, 'z': 0},
                meta_data={'test': True}
            )

    def test_photo_list_pagination_default_page_size(self):
        """Test that photos are paginated with default page size of 20"""
        response = self.client.get('/api/photos/')
        self.assertEqual(response.status_code, 200)
        
        # Should have pagination structure
        self.assertIn('results', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        
        # Default page size is 20
        self.assertEqual(len(response.data['results']), 20)

    def test_photo_list_pagination_custom_page_size(self):
        """Test that photos respect custom page size parameter"""
        response = self.client.get('/api/photos/?page_size=10')
        self.assertEqual(response.status_code, 200)
        
        # Should return 10 items
        self.assertEqual(len(response.data['results']), 10)

    def test_photo_list_pagination_max_page_size(self):
        """Test that page size respects maximum limit"""
        # Request more than max (100)
        response = self.client.get('/api/photos/?page_size=200')
        self.assertEqual(response.status_code, 200)
        
        # Should be capped at max_page_size of 100
        self.assertLessEqual(len(response.data['results']), 100)

    def test_photo_list_pagination_ordering(self):
        """Test that photos are ordered by created_at descending"""
        response = self.client.get('/api/photos/?page_size=5')
        self.assertEqual(response.status_code, 200)
        
        results = response.data['results']
        # Verify ordering by farmbot_id (which corresponds to creation order)
        farmbot_ids = [photo['farmbot_id'] for photo in results]
        self.assertEqual(farmbot_ids, sorted(farmbot_ids, reverse=True))

    def test_photo_list_pagination_cursor(self):
        """Test that cursor pagination works for navigating pages"""
        # Get first page
        response1 = self.client.get('/api/photos/?page_size=10')
        self.assertEqual(response1.status_code, 200)
        self.assertIsNotNone(response1.data['next'])
        
        # Get second page using next cursor
        next_cursor = response1.data['next'].split('cursor=')[1]
        response2 = self.client.get(f'/api/photos/?cursor={next_cursor}&page_size=10')
        self.assertEqual(response2.status_code, 200)
        
        # Results should be different
        ids1 = [p['farmbot_id'] for p in response1.data['results']]
        ids2 = [p['farmbot_id'] for p in response2.data['results']]
        self.assertNotEqual(ids1, ids2)

    def test_photo_list_first_page_no_previous(self):
        """Test that first page has no previous cursor"""
        response = self.client.get('/api/photos/?page_size=10')
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data['previous'])

    def test_photo_list_last_page_no_next(self):
        """Test that last page has no next cursor"""
        # Get first page to find how many we have
        response = self.client.get('/api/photos/?page_size=100')
        self.assertEqual(response.status_code, 200)
        
        # Should be last page (55 items total, 100 per page)
        self.assertIsNone(response.data['next'])

