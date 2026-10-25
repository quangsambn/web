#!/usr/bin/env python3
"""Báo Cáo Hàng Ngày SamDQ - đọc, lưu và tổng hợp báo cáo ngày của chuyên viên KH Priority.

Cách dùng:
  python3 tong_hop.py doc  [--nam 2026] < bao_cao.txt         # tách tin nhắn -> JSON
  python3 tong_hop.py ngay --ngay 2026-10-07 < bao_cao.txt    # in lại 1 tin nhắn ngày đúng mẫu
  python3 tong_hop.py luu  --file data/bao-cao.json < bao_cao.txt   # thêm/ghi đè vào file dữ liệu
  python3 tong_hop.py tuan  --ngay 2026-10-07 [--file F | < bao_cao.txt]
  python3 tong_hop.py thang --thang 2026-10   [--file F | < bao_cao.txt] [--chi-tieu chi_tieu.json]

Đầu vào dạng văn bản có thể chứa nhiều tin nhắn liên tiếp, mỗi tin bắt đầu bằng
dòng "... xin báo cáo kết quả hoạt động N d/m".
"""
import argparse, datetime as dt, json, re, sys

TEN_MAC_DINH = "ĐINH QUANG SÂM"
CHI_TIEU = [  # (khóa, nhãn, đơn vị hiển thị, là số nguyên)
    ("khMoi", "KH mới", "", True),
    ("hdKkh", "HĐ KKH", "tỷ", False),
    ("hdCkh", "HĐ CKH", "tỷ", False),
    ("thuNo", "Thu nợ", "tỷ", False),
    ("theMoi", "Thẻ mới", "Thẻ", True),
    ("bhnt", "BHNT", "Triệu", False),
    ("pnt", "PNT", "Triệu", False),
    ("tkSoDep", "TK số đẹp", "Triệu", False),
    ("ttqt", "TTQT, MBNT", "Triệu", False),
    ("phiDv", "Phí DV khác", "Triệu", False),
]
THU = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]

HEADER = re.compile(r"^(.*?)\s*xin\s+báo\s+cáo.*?\bN(?:gày)?\.?\s*(\d{1,2})\s*[/\-.]\s*(\d{1,2})(?:\s*[/\-.]\s*(\d{2,4}))?", re.I)
SO = re.compile(r"-?\d+(?:[.,]\d+)*")


def so(s):
    """Đọc số kiểu Việt Nam: 1,5 = 1.5; 1.250 = 1250; 1.250,5 = 1250.5."""
    t = str(s).strip().replace(" ", "")
    if "." in t and "," in t:
        t = t.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"-?\d{1,3}(\.\d{3})+", t) or re.fullmatch(r"-?\d{1,3}(,\d{3}){2,}", t):
        t = t.replace(".", "").replace(",", "")
    else:
        t = t.replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return 0.0


def fmt(n):
    n = round(n, 3)
    s = (f"{n:.3f}").rstrip("0").rstrip(".")
    nguyen, _, le = s.partition(".")
    am = nguyen.startswith("-")
    nguyen = nguyen.lstrip("-")
    nhom = f"{int(nguyen):,}".replace(",", ".")
    return ("-" if am else "") + nhom + ("," + le if le else "")


def khoa_cua(nhan):
    k = nhan.lower()
    if "kkh" in k: return "hdKkh"
    if "ckh" in k: return "hdCkh"
    if re.search(r"kh\s*mới", k): return "khMoi"
    if re.search(r"thu\s*nợ", k): return "thuNo"
    if "thẻ" in k: return "theMoi"
    if "bhnt" in k: return "bhnt"
    if re.search(r"\bpnt\b", k): return "pnt"
    if re.search(r"số\s*đẹp", k): return "tkSoDep"
    if "ttqt" in k or "mbnt" in k: return "ttqt"
    if "phí" in k: return "phiDv"
    return None


def doc_van_ban(text, nam=None):
    """Tách văn bản thành danh sách báo cáo ngày."""
    nam = nam or dt.date.today().year
    ds, cur, khac = [], None, None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        h = HEADER.match(line)
        if h:
            y = int(h.group(4)) if h.group(4) else nam
            if y < 100: y += 2000
            cur = {"date": dt.date(y, int(h.group(3)), int(h.group(2))).isoformat(), "ten": h.group(1).strip()}
            cur.update({k: 0 for k, *_ in CHI_TIEU})
            cur["khac"] = ""
            ds.append(cur)
            khac = None
            continue
        if cur is None:
            continue
        body = re.sub(r"^[-–•*+]\s*", "", line)
        nhan, co_hai_cham, gia_tri = body.partition(":")
        if re.search(r"công\s*việc", nhan, re.I):
            khac = [gia_tri.strip()] if gia_tri.strip() else []
            cur["khac"] = "\n".join(khac)
            continue
        k = khoa_cua(nhan)
        if k:
            m = SO.search(gia_tri if co_hai_cham else body)
            v = so(m.group(0)) if m else 0.0
            cur[k] = round(v) if dict((a, d) for a, _, _, d in CHI_TIEU)[k] else v
            continue
        if khac is not None:
            khac.append(line)
            cur["khac"] = "\n".join(khac)
    return ds


def tin_nhan_ngay(e, ten=TEN_MAC_DINH):
    d = dt.date.fromisoformat(e["date"])
    dong = [f"{ten} xin báo cáo kết quả hoạt động N {d.day}/{d.month}"]
    for k, nhan, dv, _ in CHI_TIEU:
        dong.append(f"- {nhan}: {fmt(so(e.get(k, 0)))}" + (f" {dv}" if dv else ""))
    dong.append("- Công việc khác: " + (e.get("khac") or "").strip())
    return "\n".join(dong)


def tong_hop(entries, bat_dau, ket_thuc, tieu_de, ten=TEN_MAC_DINH, chi_tieu=None):
    trong_ky = sorted((e for e in entries if bat_dau.isoformat() <= e["date"] <= ket_thuc.isoformat()), key=lambda e: e["date"])
    tong = {k: sum(so(e.get(k, 0)) for e in trong_ky) for k, *_ in CHI_TIEU}
    dong = [f"{ten} xin báo cáo kết quả hoạt động {tieu_de} ({len(trong_ky)} ngày có báo cáo)"]
    for k, nhan, dv, _ in CHI_TIEU:
        s = f"- {nhan}: {fmt(tong[k])}" + (f" {dv}" if dv else "")
        tg = so((chi_tieu or {}).get(k, 0))
        if tg > 0:
            s += f" / KH {fmt(tg)} ({round(tong[k] / tg * 100)}%)"
        dong.append(s)
    khac = [e for e in trong_ky if (e.get("khac") or "").strip()]
    dong.append("- Công việc khác:" + "".join(
        f"\n  + {dt.date.fromisoformat(e['date']).day}/{dt.date.fromisoformat(e['date']).month}: " + re.sub(r"\n+", "; ", e["khac"].strip())
        for e in khac))
    # bảng chi tiết dạng markdown
    bang = ["| Ngày | " + " | ".join(n for _, n, _, _ in CHI_TIEU) + " |", "|---" * (len(CHI_TIEU) + 1) + "|"]
    for e in trong_ky:
        d = dt.date.fromisoformat(e["date"])
        bang.append(f"| {THU[d.weekday()]} {d.day}/{d.month} | " + " | ".join(fmt(so(e.get(k, 0))) for k, *_ in CHI_TIEU) + " |")
    bang.append("| **Tổng** | " + " | ".join(f"**{fmt(tong[k])}**" for k, *_ in CHI_TIEU) + " |")
    return "\n".join(dong), "\n".join(bang), tong


def nap_du_lieu(args):
    if getattr(args, "file", None):
        try:
            with open(args.file, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        days = data.get("days", data)
        return [dict(v, date=k) for k, v in days.items()], data.get("profile", {})
    return doc_van_ban(sys.stdin.read(), args.nam), {}


def main():
    p = argparse.ArgumentParser(description="Báo Cáo Hàng Ngày SamDQ")
    sub = p.add_subparsers(dest="lenh", required=True)
    for ten in ("doc", "ngay", "luu", "tuan", "thang"):
        s = sub.add_parser(ten)
        s.add_argument("--nam", type=int, help="Năm cho tin nhắn chỉ ghi ngày/tháng (mặc định năm nay)")
        s.add_argument("--file", help="File dữ liệu JSON (định dạng sao lưu của ứng dụng web)")
        s.add_argument("--ten", help="Họ tên in đầu tin nhắn")
        if ten in ("ngay", "tuan"):
            s.add_argument("--ngay", help="YYYY-MM-DD (mặc định hôm nay)")
        if ten == "thang":
            s.add_argument("--thang", help="YYYY-MM (mặc định tháng này)")
            s.add_argument("--chi-tieu", help="File JSON chỉ tiêu tháng, ví dụ {\"hdKkh\": 10}")
    a = p.parse_args()

    if a.lenh == "doc":
        print(json.dumps(doc_van_ban(sys.stdin.read(), a.nam), ensure_ascii=False, indent=2))
        return
    if a.lenh == "luu":
        if not a.file:
            sys.exit("Cần --file để lưu")
        moi = doc_van_ban(sys.stdin.read(), a.nam)
        try:
            with open(a.file, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {"app": "so-ket-qua-priority", "version": 1, "profile": {"name": TEN_MAC_DINH, "targets": {}}, "days": {}}
        for e in moi:
            e = dict(e); e.pop("ten", None)
            data.setdefault("days", {})[e["date"]] = e
        with open(a.file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")
        print(f"Đã lưu {len(moi)} ngày: " + ", ".join(e["date"] for e in moi))
        return

    entries, profile = nap_du_lieu(a)
    ten = a.ten or profile.get("name") or next((e.get("ten") for e in entries if e.get("ten")), None) or TEN_MAC_DINH
    if a.lenh == "ngay":
        ngay = a.ngay or (entries[-1]["date"] if entries else dt.date.today().isoformat())
        e = next((x for x in entries if x["date"] == ngay), None)
        if not e:
            sys.exit(f"Không có báo cáo ngày {ngay}")
        print(tin_nhan_ngay(e, ten))
        return
    if a.lenh == "tuan":
        g = dt.date.fromisoformat(a.ngay) if a.ngay else dt.date.today()
        bd = g - dt.timedelta(days=g.weekday()); kt = bd + dt.timedelta(days=6)
        tieu_de = f"tuần {bd.day:02d}/{bd.month:02d} – {kt.day:02d}/{kt.month:02d}/{kt.year}"
        ct = None
    else:
        y, m = map(int, (a.thang or dt.date.today().strftime("%Y-%m")).split("-"))
        bd = dt.date(y, m, 1); kt = (dt.date(y + (m == 12), m % 12 + 1, 1) - dt.timedelta(days=1))
        tieu_de = f"tháng {m}/{y}"
        ct = profile.get("targets")
        if a.chi_tieu:
            with open(a.chi_tieu, encoding="utf-8") as f:
                ct = json.load(f)
    tin, bang, _ = tong_hop(entries, bd, kt, tieu_de, ten, ct)
    print(tin)
    print()
    print(bang)


if __name__ == "__main__":
    main()
