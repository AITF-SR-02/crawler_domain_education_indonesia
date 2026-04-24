"""
Konfigurasi terpusat untuk AITF SR-02 Crawler.
Menggunakan pydantic-settings untuk memuat variabel dari .env file.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Settings (loaded from .env)
# ---------------------------------------------------------------------------

class Settings(BaseSettings):
    """Konfigurasi aplikasi — nilai default bisa di-override lewat .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Path constants (non-env, computed)
    BASE_DIR: ClassVar[Path] = BASE_DIR
    DATA_DIR: ClassVar[Path] = DATA_DIR

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    # Crawler
    MAX_CONCURRENCY: int = 5
    NOTIFY_EVERY: int = 100
    CACHE_MODE: str = "enabled"  # enabled | bypass | disabled

    # Browser
    HEADLESS: bool = True
    PAGE_TIMEOUT: int = 60000  # ms

    # Instance / scaling (optional)
    # Kosong = mode single-instance (output + dedupe di data/)
    INSTANCE_ID: str = ""

    # Search engine discovery
    SEARCH_DELAY: float = 3.0  # detik antar search query (rate limiting)
    MIN_RELEVANCE_SCORE: int = 1  # minimal keyword match untuk simpan konten

    # Discovery sources (PRD v2.0)
    DISCOVERY_ENABLE_SITEMAP: bool = True
    DISCOVERY_ENABLE_SEARCH: bool = True
    SITES_YAML_PATH: str = "sites.yaml"
    KEYWORDS_FILE: str = "keywords.txt"

    # Sitemap watch mode
    SITEMAP_RESCAN_HOURS: float = 6.0
    SITEMAP_MAX_SITEMAPS: int = 200
    SITEMAP_MAX_PAGES_PER_CYCLE: int = 5000

    # Politeness: jitter between requests
    REQUEST_DELAY_MIN: float = 2.0
    REQUEST_DELAY_MAX: float = 5.0

    # Retries (error -> retry with exponential backoff)
    RETRY_MAX_ATTEMPTS: int = 3
    RETRY_BASE_SECONDS: float = 10.0

    # Pagination
    MAX_PAGINATION_PAGES: int = 5

    # Lebih selektif untuk STEM/humaniora: gunakan frasa (>= 2 kata)
    MIN_PHRASE_RELEVANCE_SCORE: int = 1

    # Extraction quality gate (0..1)
    MIN_EXTRACTION_QUALITY: float = 0.70

    # Fuzzy science relevance (RapidFuzz, optional)
    FUZZY_SCIENCE_THRESHOLD: int = 80  # 0..100, semakin tinggi semakin presisi
    FUZZY_SCIENCE_MIN_HITS: int = 2

    # Token counting (Qwen tokenizer via HuggingFace Transformers)
    TOKENIZER_MODEL_ID: str = "Qwen/Qwen2.5-0.5B-Instruct"
    TOKENIZER_TRUST_REMOTE_CODE: bool = False

    # Discovery sharding (optional) — untuk multi-worker tanpa overlap besar
    # Default: 1 shard (tidak di-shard)
    DISCOVERY_SHARD_INDEX: int = 0
    DISCOVERY_SHARD_COUNT: int = 1

    # Optional domain whitelist: if non-empty, only URLs whose netloc endswith
    # one of these values will be enqueued. Useful for focused crawling.
    DOMAIN_WHITELIST: list[str] = []


# ---------------------------------------------------------------------------
# Klasifikasi Level Pendidikan
# ---------------------------------------------------------------------------
CLASSIFICATION_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("SD", re.compile(r"\b(sd|sekolah\s+dasar|tematik|kelas\s+[1-6])\b", re.IGNORECASE)),
    ("SMP", re.compile(r"\b(smp|sekolah\s+menengah\s+pertama|menengah\s+pertama|kelas\s+[7-9])\b", re.IGNORECASE)),
    ("SMA", re.compile(r"\b(sma|smk|sekolah\s+menengah\s+atas|menengah\s+atas|kelas\s+1[0-2])\b", re.IGNORECASE)),
]

# ---------------------------------------------------------------------------
# Target Keywords (Strategi Tim 2) — COMPREHENSIVE
# ---------------------------------------------------------------------------

TOPIK_PEDAGOGI = [
    "metode socrates", "pertanyaan sokratis", "dialog sokratis", 
    "teknik perancah", "scaffolding pembelajaran", "bantuan kognitif guru",
    "pembelajaran berdiferensiasi", "diferensiasi kelas", "gaya belajar siswa",
    "pembelajaran berbasis proyek", "pjbl", "pembelajaran proyek",
    "pembelajaran berbasis masalah", "pbl", "pemecahan masalah siswa",
    "pembelajaran kolaboratif", "belajar kelompok efektif", "diskusi kelompok",
    "pembelajaran berpusat pada siswa", "pendekatan scl",
    "gamifikasi pembelajaran", "pembelajaran berbasis game", "media pembelajaran interaktif"
]

TOPIK_METAKOGNISI = [
    "regulasi diri dalam belajar", "pembelajaran mandiri", "kemandirian belajar",
    "strategi metakognisi", "kesadaran metakognitif", "berpikir tentang berpikir",
    "teori beban kognitif", "kapasitas memori kerja", "kelebihan beban informasi",
    "pengulangan berjarak", "latihan mengingat kembali", "strategi menghafal",
    "teknik pomodoro", "manajemen waktu akademik", "pengaturan jadwal belajar",
    "rentang perhatian siswa", "konsentrasi belajar", "fokus belajar siswa"
]

TOPIK_PSIKOLOGI = [
    "kejenuhan akademik", "kelelahan belajar", "burnout siswa",
    "prokrastinasi akademik", "penundaan tugas akademik", "malas belajar",
    "keterlibatan siswa", "partisipasi belajar", "keaktifan siswa di kelas",
    "pola pikir berkembang", "mindset bertumbuh", "keyakinan kemampuan diri",
    "motivasi intrinsik belajar", "motivasi berprestasi", "dorongan belajar",
    "kecemasan akademik", "stres akademik", "tekanan belajar siswa",
    "pengaruh teman sebaya", "konformitas teman sebaya", "lingkungan pergaulan siswa",
    "pembelajaran sosial emosional", "kecerdasan emosional siswa", "keterampilan sosial anak",
    "perkembangan kognitif siswa", "tahap perkembangan anak"
]

TOPIK_AKADEMIK = [
    "asesmen formatif", "penilaian formatif", "umpan balik guru",
    "kurikulum merdeka", "evaluasi kurikulum merdeka", "profil pelajar pancasila",
    "keterampilan berpikir tingkat tinggi", "soal hots", "berpikir kritis siswa",
    "transisi perguruan tinggi", "kesiapan kuliah", "adaptasi mahasiswa baru",
    "pengambilan keputusan karier", "kematangan karier", "perencanaan masa depan siswa",
    "efektivitas beasiswa", "dampak beasiswa", "motivasi penerima beasiswa"
]

TOPIK_KOMUNIKASI_KONSELING = [
    "wawancara motivasional", "teknik konseling motivasi",
    "komunikasi asertif", "perilaku asertif siswa", "menyampaikan pendapat",
    "mendengarkan aktif", "keterampilan attending", "menyimak empatik",
    "komunikasi empatik", "empati guru", "kedekatan guru dan siswa",
    "validasi emosi", "regulasi emosi siswa", "penerimaan perasaan siswa",
    "konseling realitas", "pendekatan realita", "bimbingan konseling sekolah"
]

TOPIK_PENDIDIKAN_UMUM = [
    "Pendidikan Indonesia", "Sekolah Rakyat", "Sekolah Dasar", "Sekolah Menengah Pertama",
    "Sekolah Menengah Atas", "Sekolah Menengah Kejuruan", "Madrasah",
    "Kurikulum Nasional", "Kurikulum 2013", "Capaian Pembelajaran", "Alur Tujuan Pembelajaran",
    "Modul Ajar", "Silabus", "RPP", "Rencana Pelaksanaan Pembelajaran",
    "Kemampuan Kognitif", "Kognitif Siswa", "Ujian Nasional", "Asesmen Nasional",
    "Matematika", "Fisika", "Kimia", "Biologi", "Sains", "IPA", "Informatika", "Koding",
    "Ekonomi", "Sejarah", "Sosiologi", "Geografi", "IPS", "Ilmu Pengetahuan Sosial",
    "Pendidikan Kewarganegaraan", "PKN", "PPKN", "Sejarah Indonesia", "Bahasa Indonesia", "Bahasa Inggris",
    "Pancasila", "Profil Pelajar Pancasila", "Pendidikan Karakter", "Nasionalisme",
    "Kementerian Pendidikan", "Kemdikbud", "Kemendikbudristek", "Kemdikdasmen", "Kemdiktisaintek",
    "Kemensos Sekolah Rakyat", "Badan Standar Kurikulum dan Asesmen Pendidikan", "BSKAP",
    "Pusat Kurikulum dan Pembelajaran",
    "Soal Mudah SD SMP SMA", "Soal Menengah SD SMP SMA", "Soal Sulit SD SMP SMA",
    "Olimpiade Sains Nasional (OSN) SD SMP SMA", "Latihan Soal", "Bank Soal", "Pembahasan Soal", "Kunci Jawaban",
    "Materi Pelajaran", "Buku Teks", "Bahan Ajar", "Pembelajaran", "Guru Penggerak",
    "Projek Penguatan Profil Pelajar Pancasila",
    "rumus matematika", "aljabar", "kalkulus", "trigonometri", "geometri",
    "konsep fisika", "hukum newton", "termodinamika", "gelombang elektromagnetik",
    "konsep kimia", "ikatan kimia", "reaksi redoks", "stoikiometri",
    "konsep biologi", "sel tumbuhan", "sistem pencernaan", "genetika",
    "konsep sosiologi", "konsep geografi",
    "kalimat efektif", "struktur teks", "teks eksplanasi", "teks prosedur", "analisis cerpen",
    "seni budaya"
]

ALL_PEDAGOGI = TOPIK_PEDAGOGI + TOPIK_METAKOGNISI + TOPIK_PSIKOLOGI + TOPIK_KOMUNIKASI_KONSELING
ALL_PENDIDIKAN = TOPIK_AKADEMIK + TOPIK_PENDIDIKAN_UMUM

TARGET_KEYWORDS: list[str] = ALL_PEDAGOGI + ALL_PENDIDIKAN

# ---------------------------------------------------------------------------
MIN_RELEVANCE_KEYWORDS: int = 4

# ---------------------------------------------------------------------------
# Indonesian science + humaniora vocabulary (untuk fuzzy relevance)
# Semua term di bawah minimal 2 kata (lebih selektif & lebih kontekstual)
# ---------------------------------------------------------------------------
SCIENCE_VOCAB_ID: list[str] = [
    # --- Sains (fisika/kimia/biologi/matematika) ---
    "materi sains",
    "pelajaran ipa",
    "ilmu pengetahuan alam",

    "materi fisika",
    "arus listrik",
    "listrik statis",
    "listrik dinamis",
    "tegangan listrik",
    "hambatan listrik",
    "rangkaian listrik",
    "medan magnet",

    "konsep energi",
    "konsep gaya",
    "konsep gerak",
    "konsep kecepatan",
    "konsep percepatan",
    "konsep massa",
    "konsep gravitasi",
    "konsep tekanan",
    "konsep fluida",
    "gelombang mekanik",
    "frekuensi gelombang",
    "amplitudo gelombang",
    "optik geometri",
    "cahaya tampak",
    "lensa cembung",
    "gelombang bunyi",
    "energi termal",
    "konsep suhu",
    "energi kalor",
    "konsep termodinamika",

    "materi kimia",
    "struktur atom",
    "struktur molekul",
    "unsur kimia",
    "senyawa kimia",
    "reaksi kimia",
    "materi stoikiometri",
    "asam basa",
    "nilai ph",
    "larutan kimia",
    "ikatan kimia",
    "tabel periodik",

    "materi biologi",
    "konsep genetika",
    "molekul dna",
    "struktur sel",
    "sel hewan",
    "sel tumbuhan",
    "jaringan tubuh",
    "organ tubuh",
    "konsep ekologi",
    "teori evolusi",
    "mikroorganisme patogen",
    "bakteri patogen",
    "virus patogen",
    "sistem pencernaan",
    "sistem pernapasan",
    "sistem peredaran darah",

    "materi matematika",
    "materi statistika",
    "materi probabilitas",
    "materi peluang",
    "konsep aljabar",
    "konsep geometri",
    "konsep trigonometri",
    "konsep kalkulus",
    "konsep integral",
    "konsep turunan",
    "konsep limit",
    "konsep logaritma",
    "konsep eksponen",
    "konsep persamaan",
    "konsep fungsi",
    "konsep vektor",
    "konsep matriks",
    "tabel data",
    "grafik fungsi",
    "diagram batang",

    "metode eksperimen",
    "metode percobaan",
    "kegiatan praktikum",
    "ruang laboratorium",
    "metode ilmiah",
    "uji hipotesis",
    "hasil pengamatan",
    "analisis data",

    "olimpiade sains",
    "osn sains",

    # --- Humaniora (IPS/bahasa/seni) ---
    "ilmu pengetahuan sosial",
    "materi ips",

    "ilmu ekonomi",
    "materi ekonomi",
    "konsep permintaan",
    "konsep penawaran",

    "ilmu sejarah",
    "materi sejarah",
    "sejarah indonesia",

    "ilmu sosiologi",
    "materi sosiologi",

    "ilmu geografi",
    "materi geografi",

    "pendidikan kewarganegaraan",
    "pendidikan pancasila",

    "bahasa indonesia",
    "bahasa inggris",
    "kalimat efektif",
    "struktur teks",
    "teks eksplanasi",
    "teks prosedur",
    "analisis cerpen",

    "seni budaya",
]
