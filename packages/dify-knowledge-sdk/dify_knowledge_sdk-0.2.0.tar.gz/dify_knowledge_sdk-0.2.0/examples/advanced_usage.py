"""
Advanced usage examples for the Dify SDK.

This example shows more complex scenarios including file uploads,
custom processing rules, error handling, and batch operations.
"""

import time
from pathlib import Path

from dify_knowledge_sdk import DifyDatasetClient
from dify_knowledge_sdk.exceptions import DifyAPIError


class AdvancedDifyManager:
    """Advanced Dify knowledge base manager with utility methods."""

    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai"):
        self.client = DifyDatasetClient(api_key=api_key, base_url=base_url)

    def create_dataset_with_custom_rules(self, name: str, description: str = None):
        """Create a dataset with custom processing rules."""
        try:
            dataset = self.client.create_dataset(name=name, description=description, permission="only_me")
            print(f"✅ Created dataset: {dataset.name}")
            return dataset
        except DifyAPIError as e:
            print(f"❌ Failed to create dataset: {e}")
            return None

    def upload_document_with_custom_processing(self, dataset_id: str, file_path: str, custom_separator: str = "###", max_tokens: int = 500):
        """Upload a document with custom processing rules."""
        # Custom processing rules
        process_rule_config = {
            "rules": {
                "pre_processing_rules": [{"id": "remove_extra_spaces", "enabled": True}, {"id": "remove_urls_emails", "enabled": True}],
                "segmentation": {"separator": custom_separator, "max_tokens": max_tokens},
            }
        }

        try:
            doc_response = self.client.create_document_by_file(
                dataset_id=dataset_id,
                file_path=file_path,
                indexing_technique="high_quality",
                process_rule_mode="custom",
                process_rule_config=process_rule_config,
            )
            print(f"✅ Uploaded document: {doc_response.document.name}")
            return doc_response
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            return None
        except DifyAPIError as e:
            print(f"❌ Failed to upload document: {e}")
            return None

    def monitor_indexing_progress(self, dataset_id: str, batch_id: str, max_attempts: int = 30):
        """Monitor document indexing progress with polling."""

        print("📊 Monitoring indexing progress...")
        for _attempt in range(max_attempts):
            try:
                status = self.client.get_document_indexing_status(dataset_id, batch_id)
                if status.data:
                    info = status.data[0]
                    progress = f"{info.completed_segments}/{info.total_segments}"
                    print(f"Status: {info.indexing_status} | Progress: {progress}")

                    if info.indexing_status in ["completed", "error"]:
                        return info.indexing_status == "completed"

                    time.sleep(2)  # Wait 2 seconds before next check
                else:
                    print("❌ No indexing status data found")
                    return False
            except DifyAPIError as e:
                print(f"❌ Error checking status: {e}")
                return False

        print("⏰ Indexing monitoring timed out")
        return False

    def batch_create_segments(self, dataset_id: str, document_id: str, text_chunks: list):
        """Create multiple segments from text chunks."""
        segments_data = []
        for i, chunk in enumerate(text_chunks):
            segments_data.append({"content": chunk, "answer": f"Answer for chunk {i + 1}", "keywords": [f"keyword{i + 1}", "batch"]})

        try:
            response = self.client.create_segments(dataset_id, document_id, segments_data)
            print(f"✅ Created {len(response.data)} segments in batch")
            return response
        except DifyAPIError as e:
            print(f"❌ Failed to create segments: {e}")
            return None

    def setup_metadata_schema(self, dataset_id: str):
        """Set up a complete metadata schema for a dataset."""
        metadata_fields = [
            {"type": "string", "name": "category"},
            {"type": "string", "name": "author"},
            {"type": "number", "name": "priority"},
            {"type": "time", "name": "last_updated"},
        ]

        created_fields = []
        for field in metadata_fields:
            try:
                created_field = self.client.create_metadata_field(dataset_id=dataset_id, field_type=field["type"], name=field["name"])
                created_fields.append(created_field)
                print(f"✅ Created metadata field: {created_field.name}")
            except DifyAPIError as e:
                print(f"❌ Failed to create field {field['name']}: {e}")

        return created_fields

    def bulk_update_document_metadata(self, dataset_id: str, documents_metadata: list):
        """Update metadata for multiple documents at once."""
        try:
            self.client.update_document_metadata(dataset_id, documents_metadata)
            print(f"✅ Updated metadata for {len(documents_metadata)} documents")
            return True
        except DifyAPIError as e:
            print(f"❌ Failed to update metadata: {e}")
            return False

    def cleanup_dataset(self, dataset_id: str):
        """Clean up a dataset by deleting all documents and the dataset itself."""
        try:
            # List and delete all documents
            documents = self.client.list_documents(dataset_id)
            for doc in documents.data:
                try:
                    self.client.delete_document(dataset_id, doc.get("id"))
                    print(f"🗑️ Deleted document: {doc.get('name', 'Unknown')}")
                except DifyAPIError as e:
                    print(f"❌ Failed to delete document {doc.get('id')}: {e}")

            # Delete the dataset
            self.client.delete_dataset(dataset_id)
            print(f"🗑️ Deleted dataset: {dataset_id}")
            return True
        except DifyAPIError as e:
            print(f"❌ Failed to cleanup dataset: {e}")
            return False

    def close(self):
        """Close the client connection."""
        self.client.close()


def main():
    """Demonstrate advanced usage scenarios."""
    api_key = "YOUR_API_KEY_HERE"  # Replace with your actual API key
    base_url = "https://api.dify.ai"  # Default Dify API URL
    manager = AdvancedDifyManager(api_key=api_key, base_url=base_url)

    try:
        # Scenario 1: Create dataset with comprehensive setup
        print("🚀 Scenario 1: Creating dataset with metadata schema")
        timestamp = int(time.time())
        dataset = manager.create_dataset_with_custom_rules(name=f"Advanced Test Dataset {timestamp}", description="Dataset created with advanced SDK features")

        if not dataset:
            return

        dataset_id = dataset.id

        # Set up metadata schema
        metadata_fields = manager.setup_metadata_schema(dataset_id)

        # Scenario 2: Upload document with custom processing
        print("\n📁 Scenario 2: Document upload with custom processing")

        # Create a sample text file for demonstration
        sample_file = Path("sample_document.txt")
        sample_content = """
        Chapter 1: Introduction
        ###
        This is the introduction to our technical documentation.
        It covers the basic concepts and setup procedures.
        ###
        Chapter 2: Advanced Features
        ###
        This chapter explores advanced features and configuration options.
        Users can customize the system according to their needs.
        ###
        Chapter 3: Best Practices
        ###
        Here we outline the recommended best practices for optimal performance.
        Following these guidelines will ensure system reliability.
        """

        sample_file.write_text(sample_content.strip())

        doc_response = manager.upload_document_with_custom_processing(
            dataset_id=dataset_id, file_path=str(sample_file), custom_separator="###", max_tokens=300
        )

        # Clean up sample file
        sample_file.unlink()

        if not doc_response:
            return

        document_id = doc_response.document.id
        batch_id = doc_response.batch

        # Monitor indexing progress
        print("\n⏳ Scenario 3: Monitoring indexing progress")
        success = manager.monitor_indexing_progress(dataset_id, batch_id)
        if success:
            print("✅ Document indexing completed successfully")

        # Scenario 4: Batch operations
        print("\n📦 Scenario 4: Batch segment creation")
        text_chunks = [
            "This is the first text chunk for batch processing.",
            "Here's the second chunk with different content.",
            "The third chunk contains additional information.",
            "Finally, the fourth chunk completes our batch.",
        ]

        manager.batch_create_segments(dataset_id, document_id, text_chunks)

        # Scenario 5: Bulk metadata updates
        print("\n🏷️ Scenario 5: Bulk metadata updates")
        if metadata_fields:
            documents_metadata = [
                {
                    "document_id": document_id,
                    "metadata_list": [
                        {
                            "id": metadata_fields[0].id,  # category
                            "value": "technical-documentation",
                            "name": "category",
                        },
                        {
                            "id": metadata_fields[1].id,  # author
                            "value": "SDK Team",
                            "name": "author",
                        },
                    ],
                }
            ]

            manager.bulk_update_document_metadata(dataset_id, documents_metadata)

        # Scenario 6: Comprehensive dataset analysis
        print("\n📊 Scenario 6: Dataset analysis")
        datasets = manager.client.list_datasets()
        documents = manager.client.list_documents(dataset_id)
        segments = manager.client.list_segments(dataset_id, document_id)
        metadata_list = manager.client.list_metadata_fields(dataset_id)

        print("📈 Dataset Statistics:")
        print(f"  - Total datasets: {datasets.total}")
        print(f"  - Documents in current dataset: {documents.total}")
        print(f"  - Segments in current document: {len(segments.data)}")
        print(f"  - Metadata fields: {len(metadata_list.doc_metadata)}")

        print("\n🎉 All advanced scenarios completed successfully!")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        manager.close()


if __name__ == "__main__":
    main()
