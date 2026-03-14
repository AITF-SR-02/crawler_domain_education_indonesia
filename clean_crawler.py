import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from trafilatura import extract
from bs4 import BeautifulSoup
import re
import json

class CleanDataCrawler:
    def __init__(self):
        # Konfigurasi Browser (Headless, User Agent realistis)
        self.browser_config = BrowserConfig(
            headless=True,
            verbose=True,
            # Tambahkan args jika perlu bypass deteksi bot sederhana
            extra_args=["--disable-blink-features=AutomationControlled"]
        )
        
        # Konfigurasi Crawling
        self.crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            # Wait for CSS selector umum untuk konten utama (bisa disesuaikan per situs)
            wait_for="article, main, .content, body", 
            delay_before_return_html=2.0, # Beri waktu 2 detik setelah load untuk JS render
            exclude_external_links=True,
            process_iframes=False # Seringkali iframe adalah iklan
        )

    def clean_html(self, html: str) -> str:
        """
        Membersihkan HTML dari tag navigasi, script, style, dan boilerplate lainnya
        sebelum diekstraksi menjadi teks.
        """
        soup = BeautifulSoup(html, 'lxml')

        # Hapus tag yang tidak diinginkan
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form', 'noscript']):
            tag.decompose()

        # Hapus atribut yang tidak perlu (onclick, onmouseover, dll)
        for tag in soup.find_all(True):
            attrs = dict(tag.attrs)
            for attr in attrs:
                if attr.startswith('on') or attr in ['id', 'class']: # Opsional: hapus class/id jika terlalu kotor
                     # Kita simpan class/id jika diperlukan untuk struktur, tapi bisa dihapus jika ingin polos
                    pass 
        
        return str(soup)

    def extract_main_content(self, html: str, url: str) -> str:
        """
        Menggunakan Trafilatura untuk mengekstrak hanya konten utama (artikel/teks inti).
        """
        # Trafilatura sangat bagus untuk membedakan konten utama vs sidebar/iklan
        text = extract(html, url=url, include_tables=False, include_comments=False)
        return text if text else ""

    def normalize_text(self, text: str) -> str:
        """
        Normalisasi teks: hapus spasi berlebih, karakter aneh, dll.
        """
        if not text:
            return ""
        
        # Hapus spasi berlebih
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Hapus karakter kontrol non-printable
        text = ''.join(char for char in text if char.isprintable() or char in ['\n', '\t'])
        
        return text

    async def crawl_and_process(self, url: str):
        print(f"🕷️  Mulai crawling: {url}")
        
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(url=url, config=self.crawler_config)
            
            if not result.success:
                print(f"❌ Gagal crawling {url}: {result.error_message}")
                return None

            # 1. Bersihkan HTML mentah dari tag sampah
            cleaned_html = self.clean_html(result.html)
            
            # 2. Ekstrak konten utama dengan Trafilatura
            # Jika trafilatura gagal mengembalikan teks, fallback ke text biasa dari crawl4ai
            content_text = self.extract_main_content(cleaned_html, url)
            
            if not content_text and result.markdown:
                # Fallback: Gunakan markdown dari crawl4ai jika trafilatura kosong
                content_text = result.markdown
            
            # 3. Normalisasi
            final_text = self.normalize_text(content_text)
            
            if len(final_text) < 50: # Filter konten terlalu pendek (mungkin gagal ekstrak)
                print(f"⚠️  Konten terlalu pendek untuk {url}, mungkin hanya boilerplate.")
                return None

            print(f"✅ Berhasil memproses {url} (Panjang: {len(final_text)} karakter)")
            
            return {
                "url": url,
                "content": final_text,
                "word_count": len(final_text.split())
            }

async def main():
    crawler = CleanDataCrawler()
    
    # Daftar URL contoh (Ganti dengan target Anda)
    urls = [
        "https://www.bbc.com/news", # Contoh situs berita
        "https://id.wikipedia.org/wiki/Indonesia"
    ]
    
    dataset = []
    
    for url in urls:
        data = await crawler.crawl_and_process(url)
        if data:
            dataset.append(data)
    
    # Simpan sebagai JSONL (format umum untuk training LLM)
    output_file = "dataset_llm.jsonl"
    with open(output_file, "w", encoding="utf-8") as f:
        for item in dataset:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            
    print(f"\n🎉 Selesai! Data disimpan di {output_file}")
    print(f"Total dokumen bersih: {len(dataset)}")

if __name__ == "__main__":
    asyncio.run(main())