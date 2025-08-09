"""
Dify Knowledge Base SDK Example

This example demonstrates how to use the Dify SDK to manage knowledge bases (datasets),
documents, segments, and metadata through the API.
"""

import time

from dify_knowledge_sdk import DifyDatasetClient
from dify_knowledge_sdk.exceptions import DifyAPIError, DifyAuthenticationError


def main():
    # Initialize the client with your API key
    # You can get your API key from the Dify knowledge base API page
    api_key = "YOUR_API_KEY_HERE"  # Replace with your actual API key
    base_url = "https://api.dify.ai"  # Default Dify API URL

    client = DifyDatasetClient(api_key=api_key, base_url=base_url)

    try:
        # Example 1: Create a new dataset (knowledge base)
        print("Creating a new dataset...")
        timestamp = int(time.time())
        dataset = client.create_dataset(
            name=f"Test Dataset {timestamp}",
            permission="only_me",
            description="A test dataset created with the SDK"
        )
        print(f"Created dataset: {dataset.name} (ID: {dataset.id})")
        dataset_id = dataset.id

        # Example 2: List all datasets
        print("\nListing datasets...")
        datasets = client.list_datasets(page=1, limit=10)
        print(f"Found {datasets.total} datasets")
        for ds in datasets.data[:3]:  # Show first 3
            print(f"  - {ds.get('name', 'Unknown')} (ID: {ds.get('id', 'Unknown')})")

        # Example 3: Create a document from text
        print("\nCreating document from text...")
        doc_response = client.create_document_by_text(
            dataset_id=dataset_id,
            name="Sample Text Document",
            text="This is a sample document created using the Dify SDK. It contains some text that will be indexed and made searchable.",
            indexing_technique="high_quality"
        )
        print(f"Created document: {doc_response.document.name} (ID: {doc_response.document.id})")
        document_id = doc_response.document.id
        batch_id = doc_response.batch

        # Example 4: Wait for indexing to complete
        print("\nWaiting for document indexing to complete...")
        max_attempts = 30
        for attempt in range(max_attempts):
            status = client.get_document_indexing_status(dataset_id, batch_id)
            if status.data:
                indexing_info = status.data[0]
                print(f"Indexing status: {indexing_info.indexing_status} (Attempt {attempt + 1}/{max_attempts})")
                if indexing_info.indexing_status == "completed":
                    print(f"✅ Indexing completed! Progress: {indexing_info.completed_segments}/{indexing_info.total_segments} segments")
                    break
                elif indexing_info.indexing_status in ["error", "paused"]:
                    print(f"❌ Indexing failed with status: {indexing_info.indexing_status}")
                    if indexing_info.error:
                        print(f"Error: {indexing_info.error}")
                    break
                time.sleep(2)  # Wait 2 seconds before next check
            else:
                print("No indexing status data available")
                break

        # Example 5: List documents in the dataset
        print("\nListing documents...")
        documents = client.list_documents(dataset_id)
        print(f"Found {documents.total} documents")
        for doc in documents.data[:3]:  # Show first 3
            print(f"  - {doc.get('name', 'Unknown')} (Status: {doc.get('indexing_status', 'Unknown')})")

        # Example 6: Create segments for the document
        print("\nCreating segments...")
        segments_data = [
            {
                "content": "This is the first segment of the document.",
                "answer": "First segment answer",
                "keywords": ["first", "segment"]
            },
            {
                "content": "This is the second segment with different content.",
                "answer": "Second segment answer",
                "keywords": ["second", "content"]
            }
        ]
        segments_response = client.create_segments(dataset_id, document_id, segments_data)
        print(f"Created {len(segments_response.data)} segments")

        # Example 7: List segments
        print("\nListing segments...")
        segments = client.list_segments(dataset_id, document_id)
        for segment in segments.data[:2]:  # Show first 2
            print(f"  - Segment {segment.position}: {segment.content[:50]}...")

        # Example 8: Create metadata field
        print("\nCreating metadata field...")
        metadata_field = client.create_metadata_field(
            dataset_id=dataset_id,
            field_type="string",
            name="category"
        )
        print(f"Created metadata field: {metadata_field.name} (Type: {metadata_field.type})")

        # Example 9: List metadata fields
        print("\nListing metadata fields...")
        metadata_list = client.list_metadata_fields(dataset_id)
        print(f"Built-in fields enabled: {metadata_list.built_in_field_enabled}")
        for field in metadata_list.doc_metadata:
            print(f"  - {field.name} ({field.type}) - Used {field.use_count or 0} times")

        # Example 10: Update document metadata
        print("\nUpdating document metadata...")
        metadata_operations = [
            {
                "document_id": document_id,
                "metadata_list": [
                    {
                        "id": metadata_field.id,
                        "value": "technical-docs",
                        "name": "category"
                    }
                ]
            }
        ]
        client.update_document_metadata(dataset_id, metadata_operations)
        print("Document metadata updated successfully")

        # Example 11: Update document text
        print("\nUpdating document...")
        updated_doc = client.update_document_by_text(
            dataset_id=dataset_id,
            document_id=document_id,
            name="Updated Sample Document",
            text="This is the updated content of the document with additional information."
        )
        print(f"Updated document: {updated_doc.document.name}")

        print("\n✅ All examples completed successfully!")

    except DifyAuthenticationError:
        print("❌ Authentication failed. Please check your API key.")
    except DifyAPIError as e:
        print(f"❌ API error: {e}")
        if hasattr(e, 'status_code'):
            print(f"Status code: {e.status_code}")
        if hasattr(e, 'error_code'):
            print(f"Error code: {e.error_code}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        # Clean up: close the client
        client.close()


if __name__ == "__main__":
    main()
