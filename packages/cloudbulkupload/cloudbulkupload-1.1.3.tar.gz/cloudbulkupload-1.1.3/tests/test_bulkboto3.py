import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import boto3
from dotenv import load_dotenv

from cloudbulkupload import BulkBoto3, StorageTransferPath
try:
    from test_config import get_test_config
except ImportError:
    from tests.test_config import get_test_config

# Load environment variables
load_dotenv()


class TestBulkBoto3(unittest.TestCase):
    """Test suite for BulkBoto3 class with performance testing."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        # Load test configuration
        cls.config = get_test_config()
        cls.config.print_config()
        
        # Load AWS credentials from .env file
        cls.endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:9000")
        cls.access_key = os.getenv("AWS_ACCESS_KEY_ID")
        cls.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        cls.bucket_name = "test-bulkboto3-bucket"
        
        if not cls.access_key or not cls.secret_key:
            raise ValueError("AWS credentials not found in .env file")
        
        # Initialize BulkBoto3 instance
        cls.bulkboto = BulkBoto3(
            endpoint_url=cls.endpoint_url,
            aws_access_key_id=cls.access_key,
            aws_secret_access_key=cls.secret_key,
            max_pool_connections=cls.config.max_threads,
            verbose=cls.config.verbose_tests
        )
        
        # Create test bucket
        cls.bulkboto.create_new_bucket(cls.bucket_name)
        
        # Create temporary test directory
        cls.test_dir = tempfile.mkdtemp(prefix="bulkboto3_test_")
        cls.setup_test_files()

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        # Clean up bucket based on configuration
        if cls.config.should_cleanup("buckets"):
            try:
                print(cls.config.get_cleanup_message("buckets"))
                cls.bulkboto.empty_bucket(cls.bucket_name)
                cls.bulkboto.resource.Bucket(cls.bucket_name).delete()
                print("✅ Bucket cleanup completed")
            except Exception as e:
                print(f"⚠️  Warning: Could not clean up bucket: {e}")
        else:
            print(cls.config.get_cleanup_message("buckets"))
        
        # Clean up local files based on configuration
        if cls.config.should_cleanup("local_files"):
            try:
                print(cls.config.get_cleanup_message("local_files"))
                import shutil
                shutil.rmtree(cls.test_dir, ignore_errors=True)
                print("✅ Local files cleanup completed")
            except Exception as e:
                print(f"⚠️  Warning: Could not clean up local files: {e}")
        else:
            print(cls.config.get_cleanup_message("local_files"))

    @classmethod
    def setup_test_files(cls):
        """Create test files for upload testing."""
        # Create test directory structure
        test_structure = {
            "file1.txt": "This is test file 1",
            "file2.txt": "This is test file 2",
            "subdir1/file3.txt": "This is test file 3 in subdir1",
            "subdir1/file4.txt": "This is test file 4 in subdir1",
            "subdir2/file5.txt": "This is test file 5 in subdir2",
            "subdir2/subdir3/file6.txt": "This is test file 6 in subdir2/subdir3",
        }
        
        for file_path, content in test_structure.items():
            full_path = Path(cls.test_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)

    def setUp(self):
        """Set up before each test."""
        # Ensure bucket is empty before each test
        self.bulkboto.empty_bucket(self.bucket_name)

    def test_connection(self):
        """Test that we can connect to the S3 service."""
        self.assertIsNotNone(self.bulkboto.resource)
        
        # Test that we can list buckets
        buckets = list(self.bulkboto.resource.buckets.all())
        self.assertIsInstance(buckets, list)

    def test_bucket_operations(self):
        """Test bucket creation and deletion."""
        test_bucket = "test-bucket-ops"
        
        # Test bucket creation
        self.bulkboto.create_new_bucket(test_bucket)
        
        # Verify bucket exists
        bucket_exists = any(bucket.name == test_bucket 
                          for bucket in self.bulkboto.resource.buckets.all())
        self.assertTrue(bucket_exists)
        
        # Test bucket emptying
        self.bulkboto.empty_bucket(test_bucket)
        
        # Clean up
        self.bulkboto.resource.Bucket(test_bucket).delete()

    def test_single_file_upload_performance(self):
        """Test single file upload performance."""
        test_file = Path(self.test_dir) / "file1.txt"
        storage_path = "test_single_upload.txt"
        
        # Measure upload time
        start_time = time.time()
        self.bulkboto.upload(
            bucket_name=self.bucket_name,
            upload_paths=StorageTransferPath(
                local_path=str(test_file),
                storage_path=storage_path
            )
        )
        upload_time = time.time() - start_time
        
        # Verify file was uploaded
        exists = self.bulkboto.check_object_exists(
            bucket_name=self.bucket_name,
            object_path=storage_path
        )
        self.assertTrue(exists)
        
        print(f"Single file upload time: {upload_time:.3f} seconds")
        self.assertLess(upload_time, 10.0)  # Should complete within 10 seconds

    def test_multiple_files_upload_performance(self):
        """Test multiple files upload performance."""
        upload_paths = [
            StorageTransferPath(
                local_path=str(Path(self.test_dir) / "file1.txt"),
                storage_path="multi/file1.txt"
            ),
            StorageTransferPath(
                local_path=str(Path(self.test_dir) / "file2.txt"),
                storage_path="multi/file2.txt"
            ),
            StorageTransferPath(
                local_path=str(Path(self.test_dir) / "subdir1/file3.txt"),
                storage_path="multi/subdir1/file3.txt"
            ),
        ]
        
        # Measure upload time
        start_time = time.time()
        self.bulkboto.upload(
            bucket_name=self.bucket_name,
            upload_paths=upload_paths
        )
        upload_time = time.time() - start_time
        
        # Verify files were uploaded
        for path in upload_paths:
            exists = self.bulkboto.check_object_exists(
                bucket_name=self.bucket_name,
                object_path=path.storage_path
            )
            self.assertTrue(exists)
        
        print(f"Multiple files upload time: {upload_time:.3f} seconds")
        self.assertLess(upload_time, 15.0)  # Should complete within 15 seconds

    def test_directory_upload_performance(self):
        """Test directory upload performance with different thread counts."""
        thread_counts = [1, 5, 10, 20]
        results = {}
        
        for n_threads in thread_counts:
            # Measure upload time
            start_time = time.time()
            self.bulkboto.upload_dir_to_storage(
                bucket_name=self.bucket_name,
                local_dir=self.test_dir,
                storage_dir=f"test_dir_{n_threads}",
                n_threads=n_threads
            )
            upload_time = time.time() - start_time
            results[n_threads] = upload_time
            
            # Verify files were uploaded
            objects = self.bulkboto.list_objects(
                bucket_name=self.bucket_name,
                storage_dir=f"test_dir_{n_threads}"
            )
            self.assertGreater(len(objects), 0)
            
            print(f"Directory upload with {n_threads} threads: {upload_time:.3f} seconds")
        
        # Performance analysis
        print("\nPerformance Analysis:")
        for threads, time_taken in results.items():
            print(f"  {threads} threads: {time_taken:.3f}s")
        
        # More threads should generally be faster (up to a point)
        if len(results) > 1:
            single_thread_time = results[1]
            multi_thread_time = min(results[5], results[10], results[20])
            speedup = single_thread_time / multi_thread_time
            print(f"Speedup factor: {speedup:.2f}x")
            
            # Should see some speedup with multiple threads
            self.assertGreater(speedup, 1.0)

    def test_download_performance(self):
        """Test download performance."""
        # First upload some files
        self.bulkboto.upload_dir_to_storage(
            bucket_name=self.bucket_name,
            local_dir=self.test_dir,
            storage_dir="download_test",
            n_threads=10
        )
        
        # Create download directory
        download_dir = tempfile.mkdtemp(prefix="download_test_")
        
        try:
            # Measure download time
            start_time = time.time()
            self.bulkboto.download_dir_from_storage(
                bucket_name=self.bucket_name,
                storage_dir="download_test",
                local_dir=download_dir,
                n_threads=10
            )
            download_time = time.time() - start_time
            
            # Verify files were downloaded
            downloaded_files = list(Path(download_dir).rglob("*"))
            self.assertGreater(len(downloaded_files), 0)
            
            print(f"Directory download time: {download_time:.3f} seconds")
            self.assertLess(download_time, 15.0)
            
        finally:
            import shutil
            shutil.rmtree(download_dir, ignore_errors=True)

    def test_large_file_upload_performance(self):
        """Test large file upload performance."""
        # Create a large test file (1MB)
        large_file = Path(self.test_dir) / "large_file.txt"
        large_content = "A" * 1024 * 1024  # 1MB of data
        large_file.write_text(large_content)
        
        # Measure upload time
        start_time = time.time()
        self.bulkboto.upload(
            bucket_name=self.bucket_name,
            upload_paths=StorageTransferPath(
                local_path=str(large_file),
                storage_path="large_file.txt"
            )
        )
        upload_time = time.time() - start_time
        
        # Calculate upload speed
        file_size_mb = len(large_content) / (1024 * 1024)
        upload_speed = file_size_mb / upload_time
        
        print(f"Large file upload ({file_size_mb:.1f}MB): {upload_time:.3f} seconds")
        print(f"Upload speed: {upload_speed:.2f} MB/s")
        
        # Verify file was uploaded
        exists = self.bulkboto.check_object_exists(
            bucket_name=self.bucket_name,
            object_path="large_file.txt"
        )
        self.assertTrue(exists)

    def test_concurrent_operations(self):
        """Test concurrent upload and download operations."""
        import threading
        
        results = {"upload_time": 0, "download_time": 0}
        
        def upload_operation():
            start_time = time.time()
            self.bulkboto.upload_dir_to_storage(
                bucket_name=self.bucket_name,
                local_dir=self.test_dir,
                storage_dir="concurrent_test",
                n_threads=5
            )
            results["upload_time"] = time.time() - start_time
        
        def download_operation():
            # Wait a bit for upload to start
            time.sleep(0.1)
            download_dir = tempfile.mkdtemp(prefix="concurrent_download_")
            try:
                start_time = time.time()
                self.bulkboto.download_dir_from_storage(
                    bucket_name=self.bucket_name,
                    storage_dir="concurrent_test",
                    local_dir=download_dir,
                    n_threads=5
                )
                results["download_time"] = time.time() - start_time
            finally:
                import shutil
                shutil.rmtree(download_dir, ignore_errors=True)
        
        # Run operations concurrently
        upload_thread = threading.Thread(target=upload_operation)
        download_thread = threading.Thread(target=download_operation)
        
        upload_thread.start()
        download_thread.start()
        
        upload_thread.join()
        download_thread.join()
        
        print(f"Concurrent upload time: {results['upload_time']:.3f} seconds")
        print(f"Concurrent download time: {results['download_time']:.3f} seconds")

    def test_error_handling(self):
        """Test error handling for various scenarios."""
        # Test with non-existent file
        with self.assertRaises(Exception):
            self.bulkboto.upload(
                bucket_name=self.bucket_name,
                upload_paths=StorageTransferPath(
                    local_path="non_existent_file.txt",
                    storage_path="test.txt"
                )
            )
        
        # Test with non-existent bucket
        with self.assertRaises(Exception):
            self.bulkboto.upload(
                bucket_name="non_existent_bucket",
                upload_paths=StorageTransferPath(
                    local_path=str(Path(self.test_dir) / "file1.txt"),
                    storage_path="test.txt"
                )
            )

    def test_object_operations(self):
        """Test object existence checking and listing."""
        # Upload a file first
        test_file = Path(self.test_dir) / "file1.txt"
        self.bulkboto.upload(
            bucket_name=self.bucket_name,
            upload_paths=StorageTransferPath(
                local_path=str(test_file),
                storage_path="test_object.txt"
            )
        )
        
        # Test object existence
        exists = self.bulkboto.check_object_exists(
            bucket_name=self.bucket_name,
            object_path="test_object.txt"
        )
        self.assertTrue(exists)
        
        # Test non-existent object
        not_exists = self.bulkboto.check_object_exists(
            bucket_name=self.bucket_name,
            object_path="non_existent_object.txt"
        )
        self.assertFalse(not_exists)
        
        # Test listing objects
        objects = self.bulkboto.list_objects(
            bucket_name=self.bucket_name
        )
        self.assertIn("test_object.txt", objects)


if __name__ == "__main__":
    unittest.main(verbosity=2)
