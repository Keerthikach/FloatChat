from pathlib import Path
from tqdm import tqdm
from ingest.extract import extract_metadata
from ingest.db_postgres import save_to_postgres_batch
from ingest.db_chroma import save_to_chroma_batch, model

def main():
    data_dir = Path("./dataa")
    files = list(data_dir.glob("*.nc"))

    all_records = []
    all_ids, all_vectors, all_metadatas = [], [], []

    for idx, file in enumerate(tqdm(files, desc="Ingesting ARGO files")):
        try:
            entry_id = f"entry-{idx+1:05d}"
            metadata = extract_metadata(file, entry_id)

            vector = model.encode(str(metadata)).tolist()

            # Postgres
            all_records.append((
                entry_id,
                metadata["float_id"],
                metadata["profile_time"],
                metadata["lat"],
                metadata["lon"],
                metadata["variables"],
                metadata["depth_range"],
                metadata["source_file"]
            ))

            # Chroma
            all_ids.append(entry_id)
            all_vectors.append(vector)
            all_metadatas.append(metadata)

        except Exception as e:
            print(f"❌ Error processing {file}: {e}")

    print(f"✅ Processed {len(all_records)} profiles")

    # Save in bulk
    save_to_postgres_batch(all_records)
    save_to_chroma_batch(all_ids, all_vectors, all_metadatas)

    print("🎉 Ingestion complete! Data saved to Postgres + Chroma.")

if __name__ == "__main__":
    main()
