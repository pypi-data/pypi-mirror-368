import unittest


import mmif_docloc_baapb 
from unittest.mock import patch

CORRECT_FILE_LOC = "wgbh/NJN_Network/cpb-aacip-75-84zgn33s.mp4"


class TestDocloc(unittest.TestCase):
    def test_resolve(self):
        with patch('mmif_docloc_baapb.requests.get') as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.status_code = 200
            mock_get.return_value.text = CORRECT_FILE_LOC

            result = mmif_docloc_baapb.resolve("baapb://cpb-aacip-75-84zgn33s.video")
        self.assertEqual(result, CORRECT_FILE_LOC)
    
    def test_plugged_in(self):
        import mmif
        self.assertGreater(mmif.__version__, '1.0.1')  # 1.0.2 or higher is required for `docloc` plugin support
        from mmif.serialize import annotation
        self.assertTrue('baapb' in annotation.discovered_docloc_plugins.keys())
        
    def test_integration(self):
        from mmif import Document
        with patch('mmif_docloc_baapb.requests.get') as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.status_code = 200
            mock_get.return_value.text = CORRECT_FILE_LOC
            
            new_doc = Document()
            new_doc.id = "d1"
            new_doc.location = 'baapb://cpb-aacip-75-84zgn33s.video'
            round_trip = new_doc.location_path()
            
        self.assertEqual(round_trip, CORRECT_FILE_LOC)


if __name__ == '__main__':
    unittest.main()