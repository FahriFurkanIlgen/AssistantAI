# AI Eval Harness

Regression tests for the grounding + anti-hallucination + citations pipeline.

## Çalıştırma

```powershell
cd backend
.\venv\Scripts\python.exe -m eval.run_eval                  # tüm fixture'lar
.\venv\Scripts\python.exe -m eval.run_eval -v               # cevapları da yazdır
.\venv\Scripts\python.exe -m eval.run_eval --fixtures akdeniz-sifa
```

Exit code `0` = tüm case'ler geçti, `1` = en az bir başarısızlık var.
CI/CD'de bu kod ile prompt regressionlarını yakalayabilirsiniz.

## Yeni fixture ekleme

`eval/fixtures/<business-slug>.json` dosyası oluşturun:

```json
{
  "business_slug": "your-slug",
  "cases": [
    {
      "name": "kısa açıklayıcı isim",
      "message": "Kullanıcının soracağı soru",
      "must_include": ["mutlaka geçmesi gereken substring"],
      "must_not_include": ["asla geçmemeli (anti-halüsinasyon)"],
      "must_include_any": ["bunlardan en az biri"],
      "expect_citation": ["KB doc title substring"],
      "no_citation": false,
      "language": "tr"
    }
  ]
}
```

İlgili business'in DB'de seed'lenmiş olması gerekir (örn:
`python -m scripts.seed_akdenizsifa`).

## Felsefe

- Her case **yeni session** ile çalışır (kontaminasyon yok).
- Tam pipeline'ı test eder: KB pre-retrieve → grounding prompt →
  AI cevap → citation extraction.
- Anti-halüsinasyon case'leri en kritik olanlardır — kasten "tuzak"
  sorular sorun (var olmayan personel, yanlış şehir, off-topic).
- LLM cevabı non-deterministic olduğu için exact-match yerine
  substring / must_include_any kullanın.
