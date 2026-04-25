import os
from pathlib import Path
from huggingface_hub import HfApi, create_repo

# ─────────────────────────────────────────────────────────────────
# 1. KONFIGURASI REPO
# ─────────────────────────────────────────────────────────────────
# Ganti dengan nama repo tujuan lo (misal: "IlhamRafiqin/SekolahRakyat-Dataset")
REPO_ID = "AITF-SR-02/sibi_extracted_md_siswa_only" 

# Folder atau file lokal yang mau di-push
LOCAL_PATH = r"data/raw/dataset_raw.jsonl"

# ─────────────────────────────────────────────────────────────────
# 2. UTILS (Adopsi dari kode lo)
# ─────────────────────────────────────────────────────────────────

def _strip_quotes(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value

def load_dotenv_if_present(dotenv_path: str | os.PathLike = ".env") -> None:
    path = Path(dotenv_path)
    if not path.exists() or not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), _strip_quotes(value))

def resolve_hf_token() -> str | None:
    return os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")

import json

def deduplicate_dataset(local_path: str) -> str:
    print("🧹 Memulai deduplikasi berdasarkan URL...")
    seen_urls = set()
    total_records = 0
    unique_records = 0
    
    # Tentukan output folder berdasarkan apakah input berupa file atau folder
    if os.path.isfile(local_path):
        base_dir = os.path.dirname(local_path)
        files_to_process = [os.path.basename(local_path)]
    else:
        base_dir = local_path
        files_to_process = [f for f in os.listdir(local_path) if f.endswith(".json") or f.endswith(".jsonl")]
        
    dedup_dir = os.path.join(base_dir, "_deduplicated")
    os.makedirs(dedup_dir, exist_ok=True)
    
    for filename in files_to_process:
        file_path = os.path.join(base_dir, filename)
        out_path = os.path.join(dedup_dir, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            if not content:
                continue
                
            records = []
            if filename.endswith(".jsonl") or ('\n' in content and not content.startswith('[')):
                # Parse sebagai JSONL
                for line in content.splitlines():
                    if not line.strip(): continue
                    try:
                        records.append(json.loads(line))
                    except:
                        pass
            else:
                # Parse sebagai JSON array
                try:
                    records = json.loads(content)
                    if not isinstance(records, list):
                        records = [records]
                except:
                    pass
            
            # Proses deduplikasi
            unique_data = []
            for rec in records:
                total_records += 1
                url = rec.get("url")
                
                # Jika tidak ada URL, tetap kita simpan
                if not url:
                    unique_data.append(rec)
                    unique_records += 1
                # Jika URL belum pernah dilihat, simpan dan catat
                elif url not in seen_urls:
                    seen_urls.add(url)
                    unique_data.append(rec)
                    unique_records += 1
                    
            # Tulis ke folder deduplikasi
            with open(out_path, 'w', encoding='utf-8') as f:
                if filename.endswith(".jsonl") or ('\n' in content and not content.startswith('[')):
                    for rec in unique_data:
                        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                else:
                    json.dump(unique_data, f, ensure_ascii=False, indent=2)
                    
            print(f"  - {filename}: {len(unique_data)} unik dari {len(records)} total data")
            
        except Exception as e:
            print(f"❌ Gagal memproses {filename}: {e}")
            
    print(f"✨ Selesai! Total data: {total_records} | Unik: {unique_records} | Duplikat dihapus: {total_records - unique_records}")
    return dedup_dir


# ─────────────────────────────────────────────────────────────────
# 3. PUSH ENGINE
# ─────────────────────────────────────────────────────────────────

def push_data_to_hf(repo_id: str, local_dir: str, token: str | None):
    api = HfApi(token=token)
    
    print(f"🚀 Memulai proses push ke: {repo_id}")
    print(f"📁 Local folder awal: {os.path.abspath(local_dir)}")
    
    if not token:
        print("❌ Error: Token HF tidak ditemukan! Isi .env dulu atau set environment variable.")
        return

    try:
        # 1. Jalankan proses deduplikasi dulu
        dedup_dir = deduplicate_dataset(local_dir)

        # 2. Cek/Buat Repo kalau belum ada
        print(f"\n🔍 Mengecek repository {repo_id}...")
        create_repo(repo_id=repo_id, token=token, repo_type="dataset", exist_ok=True)
        
        # 3. Upload Folder hasil deduplikasi
        print(f"📤 Mengunggah file ke Hugging Face Hub... (Mohon tunggu)")
        
        api.upload_folder(
            folder_path=dedup_dir,
            repo_id=repo_id,
            repo_type="dataset",
            # commit message
            commit_message="Add Deduplicated Dataset v1 (Unique URLs)",
            token=token
        )
        
        print(f"✅ BERHASIL! Data lo sudah mendarat di: https://huggingface.co/datasets/{repo_id}")

    except Exception as e:
        print(f"❌ Error saat push data: {str(e)}")

if __name__ == "__main__":
    # Load token dari .env
    load_dotenv_if_present(".env")
    
    # Eksekusi
    push_data_to_hf(REPO_ID, LOCAL_PATH, token=resolve_hf_token())