import os
import gcsfs
from google.cloud import storage
from watchdog.events import FileSystemEventHandler

class GCSUploaderHandler(FileSystemEventHandler):
    def __init__(self, local_dir, gcs_dir):
        self.local_dir = local_dir
        self.gcs_dir = gcs_dir
        self.fs = gcsfs.GCSFileSystem()

    def on_modified(self, event):
        if not event.is_directory:
            self.upload_file(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self.upload_file(event.src_path)

    def upload_file(self, file_path):
        relative_path = os.path.relpath(file_path, self.local_dir)
        gcs_path = os.path.join(self.gcs_dir, relative_path)
        
        try:
            with open(file_path, "rb") as f:
                with self.fs.open(gcs_path, "wb") as gcs_file:
                    gcs_file.write(f.read())
            print(f"✅ Uploaded: {relative_path} to {gcs_path}")
        except Exception as e:
            print(f"❌ Failed to upload {relative_path}: {e}")


class ModelManager:
    def __init__(self):
        pass
    
    @staticmethod
    def _download_model_from_gcs(bucket_name, gcs_model_path, local_dir):
        try:
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blobs = bucket.list_blobs(prefix=gcs_model_path)
            for blob in blobs:
                # Skip if blob name ends with a slash (directory)
                if blob.name.endswith('/'):
                    print(f"Skipping directory: {blob.name}")
                    continue
                # Determine the local file path
                local_file_path = os.path.join(
                    local_dir, blob.name[len(gcs_model_path)+1:])
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

                # Download the file
                blob.download_to_filename(local_file_path)
                print(f"Downloaded {blob.name} to {local_file_path}")
            print(os.listdir(local_dir))
        except Exception as e:
            print(e)
            
    def get_latest_checkpoint(self, bucket_name, gcs_checkpoint_dir, local_checkpoint_dir):
        """Checks GCS for the latest checkpoint, downloads it locally if found, and returns the local path."""
        try:
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blobs = bucket.list_blobs(prefix=gcs_checkpoint_dir)

            checkpoint_dirs = []
            for blob in blobs:
                # Extract checkpoint directory names (e.g., 'checkpoint-100')
                parts = blob.name.split("/")
                if len(parts) > 1 and parts[-2].startswith("checkpoint-"):
                    checkpoint_dirs.append(parts[-2])

            # Sort by step number (e.g., 'checkpoint-100' -> 100)
            checkpoint_dirs = sorted(set(checkpoint_dirs), key=lambda x: int(x.split('-')[-1]))

            if not checkpoint_dirs:
                print("🚀 No checkpoint found in GCS, starting training from scratch.")
                return None

            latest_checkpoint = f"{gcs_checkpoint_dir}/{checkpoint_dirs[-1]}"
            print(f"✅ Found latest checkpoint: {latest_checkpoint}")
            self._download_model_from_gcs(bucket_name, latest_checkpoint, local_checkpoint_dir)
            return local_checkpoint_dir  # Return local path for training

        except Exception as e:
            print(f"❌ Error checking for checkpoints in GCS: {e}")
            return None

    def get_model(self, gcs_bucket_name, gcs_model_path, local_dir):
        """ 
        Download the model from GCS to the local directory.
        """
        self._download_model_from_gcs(gcs_bucket_name, gcs_model_path, local_dir)
        return 
