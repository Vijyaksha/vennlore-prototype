
### 2.5 National and society platforms

- **J-STAGE for Japan.** JPA's proceedings are `cdjournal=pacjpa` (日本心理学会大会発表論文集, eISSN
  2433-7609), **one volume per convention**, and `&vol=` filters correctly:
  ```
  https://api.jstage.jst.go.jp/searchapi/do?service=3&cdjournal=pacjpa&vol=<N>&start=1&count=200
  ```
  vol 86 → 937, 87 → 1,159, 88 → 1,240, 89 → **1,315**. **The API returns `status WARN_002` on these
  calls while filtering correctly** — WARN_002 must not be read as failure. Verify the filter bites by
  checking that different `vol` values return different totals and that returned records carry the
  requested volume.
- **Higher Logic society sites** (PAA). The programme book sits on S3, linked from a `/final-program`
  nav page: `https://higherlogicdownload.s3.amazonaws.com/<ORG>/<guid>/UploadedFiles/<key>_<name>.pdf`.
- **Korean society file boards** (KPA):
  ```
  https://www.koreanpsychology.or.kr/KPA<year>/notice/data.html     # 역대학술대회 자료집 board
  https://www.koreanpsychology.or.kr/ft_board/download.html?fno=<n>
  ```
  Returns `content-type: application/force-download`, so check the file type. **fno order is not title
  order**: 25787 is the 656-page 초록집 (abstract book), 25788 the 120-page 프로그램북.
- **ANPEd** — the society site is bot-blocked but the proceedings are on a separate, open subdomain:
  ```
  https://anais.anped.org.br/p/<edition>reuniao/trabalhos?page=N     # 30 entries a page
  ```
  Each entry is `<div class="well anais-trabalhos">` with an `<h4 class="anais-trabalho-titulo">` and a
  type label `span.field-content.anais-trabalho-gt`. Editions /38reuniao … /41reuniao.
- **COMIE** — `/memoriaelectronica/` 403s, but the **per-edition path on plain HTTP** does not:
  ```
  http://www.comie.org.mx/congreso/memoriaelectronica/v17/inc/generarListadoPonenciasTematica.php?t=<100..1800>
  ```
  18 area listings, ponencias coded `[C-NNNN]`; the `&p=` parameter is ignored and each area returns its
  full list in one response. **1,250**.
- **Drupal is this field's commonest programme host** (AAR, ANPEd, COMIE, EEA-ESEM, IPSA). Its `?page=N`
  pager is the first thing to test — and the first thing to distrust (§3).

---

