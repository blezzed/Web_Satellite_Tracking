from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch, mock_open
from datetime import timedelta
from main.entities.tle import SatelliteTLE
from satellite_tracker.operations.get_tles import downloaded_satellites_tle

class FilterDownloadedSatellitesTest(TestCase):

    def setUp(self):
        # Create a sample satellite for testing
        self.satellite = SatelliteTLE.objects.create(
            name='SAT1',
            line1='1 25544U 98067A   21275.17388254  .00001448  00000-0  39749-4 0  9993',
            line2='2 25544  51.6443  20.1569 0002873 206.2892 153.7154 15.48920414470029'
        )

    @patch('builtins.open', new_callable=mock_open, read_data='''SAT1
1 25544U 98067A   21275.17388254  .00001448  00000-0  39749-4 0  9993
2 25544  51.6443  20.1569 0002873 206.2892 153.7154 15.48920414470029
''')
    @patch('skyfield.api.load.download')  # Mock the download function
    def test_download_tle_data_updates_existing_satellites(self, mock_download, mock_file):
        # Set last_updated to more than max_days ago
        self.satellite.last_updated = timezone.now() - timedelta(days=8)
        self.satellite.save()

        # Call the function
        downloaded_satellites_tle()

        # Refresh the satellite from the database
        self.satellite.refresh_from_db()

        # Check that the satellite data was updated
        self.assertEqual(self.satellite.line1.strip(), '1 25544U 98067A   21275.17388254  .00001448  00000-0  39749-4 0  9993')
        self.assertEqual(self.satellite.line2.strip(), '2 25544  51.6443  20.1569 0002873 206.2892 153.7154 15.48920414470029')

    @patch('skyfield.api.load.download')  # Mock the download function
    def test_no_download_if_recently_updated(self, mock_download):
        # Set last_updated to within max_days
        self.satellite.last_updated = timezone.now()
        self.satellite.save()

        # Call the function
        downloaded_satellites_tle()

        # Ensure download was not called
        mock_download.assert_not_called()

    @patch('skyfield.api.load.download')  # Mock the download function
    def test_downloads_if_empty_lines(self, mock_download):
        # Create a satellite with empty line1
        SatelliteTLE.objects.create(name='SAT2', line1='', line2='')

        # Call the function
        downloaded_satellites_tle()

        # Ensure download was called
        mock_download.assert_called_once()

    # Add more tests as necessary for different scenarios
