import os
import json
import csv
import hashlib
import sys
from typing import List, Dict, Any
from utils.preprocess import clean_text, chunk_text

# Increase CSV field size limit
csv.field_size_limit(sys.maxsize)

class CSVPreprocessor:
    def __init__(self, input_csv: str, output_path: str = "data/chunks.json"):
        self.input_csv = input_csv
        self.output_path = output_path
        self.processed_chunks = []
        self.content_hashes = set()
        
    def is_duplicate_chunk(self, content: str) -> bool:
        """Check if chunk content is duplicate"""
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        if content_hash in self.content_hashes:
            return True
        self.content_hashes.add(content_hash)
        return False
    
    def process_csv(self, min_content_length: int = 50) -> List[Dict[str, Any]]:
        """Process CSV file and create chunks"""
        chunks = []
        
        if not os.path.exists(self.input_csv):
            print(f"[!] CSV file not found: {self.input_csv}")
            return chunks
        
        print(f"[+] Reading CSV file: {self.input_csv}")
        
        try:
            with open(self.input_csv, "r", encoding="utf-8", errors='ignore') as csvfile:
                reader = csv.DictReader(csvfile)
                
                total_rows = 0
                processed_rows = 0
                skipped_rows = 0
                
                for row_idx, row in enumerate(reader):
                    total_rows += 1
                    
                    try:
                        # Extract data from CSV columns
                        topic = (row.get('Topic') or row.get('title') or row.get('Title') or '').strip()
                        url = (row.get('URL') or row.get('url') or row.get('Url') or '').strip()
                        content = (row.get('Content') or row.get('content') or row.get('text') or '').strip()
                        
                        # Skip if no content
                        if not content or len(content) < min_content_length:
                            skipped_rows += 1
                            continue
                        
                        # Truncate very long content to prevent memory issues
                        if len(content) > 50000:  # 50KB limit per document
                            content = content[:50000] + "... [Content truncated]"
                        
                        # Clean the content
                        cleaned_content = clean_text(content)
                        
                        if len(cleaned_content) < min_content_length:
                            skipped_rows += 1
                            continue
                        
                        # Create chunks using your existing function (without max_length parameter)
                        try:
                            text_chunks = chunk_text(cleaned_content)  # Using default parameters
                        except Exception as chunk_error:
                            print(f"[!] Chunking error for row {row_idx}: {chunk_error}")
                            skipped_rows += 1
                            continue
                        
                        row_chunks_added = 0
                        
                        for chunk_idx, chunk in enumerate(text_chunks):
                            # Skip empty or duplicate chunks
                            if not chunk.strip() or len(chunk.strip()) < 20:
                                continue
                                
                            if self.is_duplicate_chunk(chunk):
                                continue
                            
                            chunk_data = {
                                "id": f"doc_{row_idx}_chunk_{chunk_idx}",
                                "title": topic or f"RBI Document {row_idx}",
                                "url": url,
                                "chunk_index": chunk_idx,
                                "content": chunk.strip(),
                                "source_row": row_idx,
                                "content_length": len(chunk),
                                "original_content_length": len(content)
                            }
                            
                            chunks.append(chunk_data)
                            row_chunks_added += 1
                        
                        if row_chunks_added > 0:
                            processed_rows += 1
                            if processed_rows % 50 == 0:  # Progress update
                                print(f"[✓] Processed {processed_rows}/{total_rows} rows, {len(chunks)} chunks created")
                        else:
                            skipped_rows += 1
                        
                    except Exception as e:
                        print(f"[!] Error processing row {row_idx}: {str(e)}")
                        skipped_rows += 1
                        continue
                
                print(f"\n[✓] Processing Summary:")
                print(f"    Total rows: {total_rows}")
                print(f"    Processed rows: {processed_rows}")
                print(f"    Skipped rows: {skipped_rows}")
                print(f"    Total chunks created: {len(chunks)}")
                
        except Exception as e:
            print(f"[!] Error reading CSV file: {e}")
            return []
        
        return chunks
    
    def save_chunks(self, chunks: List[Dict[str, Any]]):
        """Save chunks to JSON file"""
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        try:
            with open(self.output_path, "w", encoding="utf-8") as f:
                json.dump(chunks, f, indent=2, ensure_ascii=False)
            
            print(f"[✓] Saved {len(chunks)} chunks to {self.output_path}")
            
            # Save summary statistics
            summary_path = self.output_path.replace('.json', '_summary.json')
            summary = {
                "total_chunks": len(chunks),
                "unique_documents": len(set(chunk['source_row'] for chunk in chunks)),
                "average_chunk_length": sum(chunk['content_length'] for chunk in chunks) / len(chunks) if chunks else 0,
                "unique_topics": len(set(chunk['title'] for chunk in chunks)),
                "max_chunk_length": max(chunk['content_length'] for chunk in chunks) if chunks else 0,
                "min_chunk_length": min(chunk['content_length'] for chunk in chunks) if chunks else 0
            }
            
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            print(f"[✓] Summary saved to {summary_path}")
            
        except Exception as e:
            print(f"[!] Error saving chunks: {e}")
    
    def run(self, min_content_length: int = 50):
        """Run the complete preprocessing pipeline"""
        print(f"[+] Starting CSV preprocessing...")
        print(f"    Input CSV: {self.input_csv}")
        print(f"    Output JSON: {self.output_path}")
        print(f"    Min content length: {min_content_length}")
        
        chunks = self.process_csv(min_content_length)
        
        if chunks:
            self.save_chunks(chunks)
            return chunks
        else:
            print("[!] No chunks were created")
            return []

# Simple function version (exactly matching your original structure)
def preprocess_csv():
    chunks = []
    INPUT_CSV = "rbi_complete_data.csv"  # Change this to your CSV filename
    OUTPUT_PATH = "data/chunks.json"
    
    if not os.path.exists(INPUT_CSV):
        print(f"[!] CSV file not found: {INPUT_CSV}")
        return
    
    try:
        # Set CSV field size limit
        csv.field_size_limit(sys.maxsize)
        
        with open(INPUT_CSV, "r", encoding="utf-8", errors='ignore') as csvfile:
            reader = csv.DictReader(csvfile)
            
            processed_count = 0
            
            for row_idx, row in enumerate(reader):
                try:
                    # Extract data from CSV columns
                    topic = row.get('Topic', '').strip()
                    url = row.get('URL', '').strip()
                    content = row.get('Content', '').strip()
                    
                    if not content or len(content) < 50:
                        print(f"[!] Skipping row {row_idx}: Content too short or empty")
                        continue
                    
                    # Limit very long content
                    if len(content) > 50000:
                        content = content[:50000] + "... [Content truncated]"
                    
                    # Clean the content
                    cleaned_content = clean_text(content)
                    
                    if len(cleaned_content) < 50:
                        print(f"[!] Skipping row {row_idx}: Cleaned content too short")
                        continue
                    
                    # Create chunks using your existing function
                    text_chunks = chunk_text(cleaned_content)  # No extra parameters
                    
                    for chunk_idx, chunk in enumerate(text_chunks):
                        if chunk.strip() and len(chunk.strip()) > 20:  # Only meaningful chunks
                            chunks.append({
                                "id": f"doc_{row_idx}_chunk_{chunk_idx}",
                                "title": topic or f"RBI Document {row_idx}",
                                "url": url,
                                "chunk_index": chunk_idx,
                                "content": chunk.strip(),
                                "source_row": row_idx
                            })
                    
                    processed_count += 1
                    if processed_count % 50 == 0:
                        print(f"[+] Processed {processed_count} documents, {len(chunks)} chunks created")
                    
                except Exception as e:
                    print(f"[!] Error in row {row_idx}: {str(e)}")
                    continue
        
        # Save chunks to JSON
        os.makedirs("data", exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        
        print(f"[✓] Preprocessed {len(chunks)} chunks from {processed_count} documents saved to {OUTPUT_PATH}")
        
    except Exception as e:
        print(f"[!] Error processing CSV: {e}")

# Test your chunk_text function
def test_chunk_function():
    """Test to see what parameters your chunk_text function accepts"""
    try:
        from utils.preprocess import chunk_text
        
        test_text = "This is a test text to see how the chunk_text function works. It should split this text into appropriate chunks."
        
        # Test with no parameters
        chunks = chunk_text(test_text)
        print(f"[✓] chunk_text() works with default parameters")
        print(f"    Created {len(chunks)} chunks")
        print(f"    First chunk: {chunks[0][:50]}..." if chunks else "    No chunks created")
        
        # Try to see what parameters it accepts by checking the function signature
        import inspect
        sig = inspect.signature(chunk_text)
        print(f"[+] chunk_text function parameters: {list(sig.parameters.keys())}")
        
        return True
        
    except Exception as e:
        print(f"[!] Error testing chunk_text function: {e}")
        return False

# Main execution
if __name__ == "__main__":
    # First, test your chunk_text function
    print("[+] Testing chunk_text function...")
    if test_chunk_function():
        print("\n[+] Starting CSV processing...")
        
        # Option 1: Simple function (recommended)
        preprocess_csv()
        
        # Option 2: Class-based approach
        # INPUT_CSV = "rbi_data.csv"
        # OUTPUT_PATH = "data/chunks.json"
        # processor = CSVPreprocessor(INPUT_CSV, OUTPUT_PATH)
        # chunks = processor.run(min_content_length=50)
        
    else:
        print("[!] Please check your chunk_text function implementation")
