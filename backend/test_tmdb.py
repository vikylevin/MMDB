"""
Unit tests for TMDB API functions
"""
import unittest
from unittest.mock import patch, Mock
import requests
from tmdb import (
    fetch_movie_details, 
    search_movies, 
    get_popular_movies, 
    get_top_rated_movies,
    get_upcoming_movies,
    get_movie_genres
)


class TestTMDBFunctions(unittest.TestCase):
    """Test cases for TMDB API wrapper functions"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.sample_movie_data = {
            'id': 550,
            'title': 'Fight Club',
            'overview': 'A ticking-time-bomb insomniac...',
            'vote_average': 8.4,
            'vote_count': 26280,
            'poster_path': '/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg',
            'backdrop_path': '/fCayJrkfRaCRCTh8GqN30f8oyQF.jpg',
            'release_date': '1999-10-15'
        }
        
        self.sample_search_response = {
            'page': 1,
            'results': [self.sample_movie_data],
            'total_pages': 1,
            'total_results': 1
        }

    @patch('tmdb.requests.get')
    def test_fetch_movie_details_success(self, mock_get):
        """Test successful movie details fetch"""
        # Arrange
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.sample_movie_data
        mock_get.return_value = mock_response
        
        # Act
        result = fetch_movie_details(550)
        
        # Assert
        self.assertEqual(result['id'], 550)
        self.assertEqual(result['title'], 'Fight Club')
        self.assertEqual(result['vote_average'], 8.4)
        mock_get.assert_called_once()

    @patch('tmdb.requests.get')
    def test_fetch_movie_details_api_error(self, mock_get):
        """Test movie details fetch with API error"""
        # Arrange
        mock_get.side_effect = requests.RequestException("API Error")
        
        # Act
        result = fetch_movie_details(550)
        
        # Assert
        self.assertIsNone(result)

    @patch('tmdb.requests.get')
    def test_search_movies_success(self, mock_get):
        """Test successful movie search"""
        # Arrange
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.sample_search_response
        mock_get.return_value = mock_response
        
        # Act
        result = search_movies("Fight Club")
        
        # Assert
        self.assertEqual(result['total_results'], 1)
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0]['title'], 'Fight Club')

    @patch('tmdb.requests.get')
    def test_get_popular_movies_with_filters(self, mock_get):
        """Test get popular movies with rating filters"""
        # Arrange
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.sample_search_response
        mock_get.return_value = mock_response
        
        # Act
        result = get_popular_movies(
            page=1, 
            vote_average_gte=8.0, 
            vote_average_lte=9.0,
            with_genres="28,12"  # Action, Adventure
        )
        
        # Assert
        self.assertIsNotNone(result)
        mock_get.assert_called_once()
        # Verify the API call includes the filters
        args, kwargs = mock_get.call_args
        self.assertIn('vote_average.gte', kwargs['params'])
        self.assertIn('vote_average.lte', kwargs['params'])
        self.assertIn('with_genres', kwargs['params'])

    @patch('tmdb.requests.get')
    def test_get_upcoming_movies_date_filter(self, mock_get):
        """Test upcoming movies includes future date filter"""
        # Arrange
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.sample_search_response
        mock_get.return_value = mock_response
        
        # Act
        result = get_upcoming_movies(page=1)
        
        # Assert
        self.assertIsNotNone(result)
        mock_get.assert_called_once()
        # Verify the API call includes date filter
        args, kwargs = mock_get.call_args
        self.assertIn('primary_release_date.gte', kwargs['params'])

    def test_invalid_movie_id(self):
        """Test handling of invalid movie ID"""
        # Test with None
        result = fetch_movie_details(None)
        self.assertIsNone(result)
        
        # Test with negative number
        with patch('tmdb.requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException("Invalid ID")
            result = fetch_movie_details(-1)
            self.assertIsNone(result)

    @patch('tmdb.requests.get')
    def test_empty_search_query(self, mock_get):
        """Test search with empty query"""
        # Arrange
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'page': 1, 'results': [], 'total_results': 0}
        mock_get.return_value = mock_response
        
        # Act
        result = search_movies("")
        
        # Assert
        self.assertEqual(result['total_results'], 0)
        self.assertEqual(len(result['results']), 0)


if __name__ == '__main__':
    # Run the tests
    unittest.main()
