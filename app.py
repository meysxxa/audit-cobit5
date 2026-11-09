%%writefile app.py
import streamlit as st
import json
from datetime import datetime, date
import pandas as pd

# ============================================================
# KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(
    page_title="Audit COBIT 5 - PT Nusantara Logistik Digital",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# KONSTANTA
# ============================================================
SKALA = {1: "Sangat Buruk", 2: "Buruk", 3: "Cukup", 4: "Baik", 5: "Sangat Baik"}
SKALA_DESKRIPSI = {
    1: "Proses tidak ada atau tidak dilaksanakan",
    2: "Proses dilakukan tidak teratur dan tanpa dokumentasi",
    3: "Proses terdefinisi tetapi penerapan belum konsisten",
    4: "Proses diterapkan konsisten, terdokumentasi, dan dipantau",
    5: "Proses terukur, dioptimalkan, dan terus ditingkatkan",
}
INTERPRETASI = [
    (1.00, 1.80, "Sangat Buruk"),
    (1.81, 2.60, "Buruk"),
    (2.61, 3.40, "Cukup"),
    (3.41, 4.20, "Baik"),
    (4.21, 5.00, "Sangat Baik"),
]

def kategori_dari_skor(skor):
    for low, high, kat in INTERPRETASI:
        if low <= skor <= high:
            return kat
    return "Tidak diketahui"

# ============================================================
# DATA KUISIONER COBIT 5 (5 domain × 5 butir × 5 indikator)
# ============================================================
KUISIONER = {
    "EDM": {
        "nama": "Evaluate, Direct and Monitor",
        "deskripsi": "Tata kelola TI: evaluasi, pengarahan, dan pemantauan oleh manajemen puncak",
        "butir": [
            {"kode": "EDM01", "judul": "Menetapkan dan memelihara kerangka tata kelola",
             "pertanyaan": "Apakah perusahaan memiliki kerangka tata kelola TI yang jelas dan dijalankan oleh manajemen?",
             "indikator": [
                 "1.1 Apakah kerangka/kebijakan tata kelola TI tertulis dan disahkan oleh manajemen puncak?",
                 "1.2 Apakah peran dan tanggung jawab tata kelola TI (mis. komite pengarah TI) ditetapkan dengan jelas?",
                 "1.3 Apakah kerangka tata kelola TI selaras dengan tujuan dan strategi bisnis perusahaan?",
                 "1.4 Apakah kerangka tata kelola TI disosialisasikan dan dijalankan oleh seluruh unit terkait?",
                 "1.5 Apakah kerangka tata kelola TI ditinjau dan diperbarui secara berkala?"]},
            {"kode": "EDM02", "judul": "Memastikan realisasi manfaat",
             "pertanyaan": "Apakah investasi TI dinilai manfaatnya terhadap tujuan bisnis perusahaan?",
             "indikator": [
                 "2.1 Apakah manfaat yang diharapkan dari setiap investasi TI ditetapkan sejak tahap perencanaan?",
                 "2.2 Apakah tersedia kriteria atau metode baku untuk menilai manfaat investasi TI (mis. biaya-manfaat, ROI)?",
                 "2.3 Apakah portofolio investasi TI diprioritaskan berdasarkan kontribusinya terhadap tujuan bisnis?",
                 "2.4 Apakah realisasi manfaat investasi TI dipantau dan dilaporkan kepada manajemen secara rutin?",
                 "2.5 Apakah hasil penilaian manfaat digunakan sebagai dasar keputusan investasi berikutnya?"]},
            {"kode": "EDM03", "judul": "Memastikan optimalisasi risiko",
             "pertanyaan": "Apakah selera risiko (risk appetite) terkait TI sudah ditetapkan dan dipantau?",
             "indikator": [
                 "3.1 Apakah selera risiko (risk appetite) dan toleransi risiko TI ditetapkan secara tertulis?",
                 "3.2 Apakah manajemen puncak menyetujui batas risiko TI yang dapat diterima perusahaan?",
                 "3.3 Apakah risiko TI utama (mis. gangguan aplikasi pelacakan, kebocoran data pelanggan) teridentifikasi dan terdaftar?",
                 "3.4 Apakah eksposur risiko TI dipantau terhadap batas yang telah ditetapkan?",
                 "3.5 Apakah risiko yang melampaui batas disekalasi dan ditindaklanjuti oleh manajemen?"]},
            {"kode": "EDM04", "judul": "Memastikan optimalisasi sumber daya",
             "pertanyaan": "Apakah sumber daya TI (SDM, aplikasi, infrastruktur, anggaran) cukup dan digunakan secara efisien?",
             "indikator": [
                 "4.1 Apakah kebutuhan SDM, aplikasi, infrastruktur, dan anggaran TI direncanakan secara tertulis?",
                 "4.2 Apakah kapasitas dan kompetensi sumber daya TI dievaluasi terhadap kebutuhan bisnis?",
                 "4.3 Apakah alokasi anggaran TI disetujui dan sesuai dengan prioritas bisnis?",
                 "4.4 Apakah penggunaan sumber daya TI dipantau untuk memastikan efisiensi (mis. pemanfaatan server)?",
                 "4.5 Apakah ketidaksesuaian atau pemborosan sumber daya TI ditindaklanjuti dengan perbaikan?"]},
            {"kode": "EDM05", "judul": "Memastikan transparansi kepada pemangku kepentingan",
             "pertanyaan": "Apakah laporan kinerja dan risiko TI disampaikan kepada pemangku kepentingan secara transparan?",
             "indikator": [
                 "5.1 Apakah pemangku kepentingan TI (manajemen, pelanggan, mitra) teridentifikasi beserta kebutuhan informasinya?",
                 "5.2 Apakah tersedia format dan jadwal baku pelaporan kinerja dan risiko TI?",
                 "5.3 Apakah laporan TI memuat informasi yang akurat, lengkap, dan mudah dipahami?",
                 "5.4 Apakah laporan diverifikasi dan disetujui sebelum disampaikan kepada pemangku kepentingan?",
                 "5.5 Apakah tanggapan pemangku kepentingan atas laporan TI ditindaklanjuti?"]},
        ],
    },
    "APO": {
        "nama": "Align, Plan and Organise",
        "deskripsi": "Penyelarasan strategi, perencanaan, dan pengorganisasian TI",
        "butir": [
            {"kode": "APO01", "judul": "Mengelola kerangka manajemen TI",
             "pertanyaan": "Apakah kebijakan, struktur organisasi, serta peran dan tanggung jawab TI sudah terdefinisi?",
             "indikator": [
                 "6.1 Apakah kebijakan TI tertulis, disahkan, dan tersedia bagi seluruh karyawan?",
                 "6.2 Apakah struktur organisasi TI (mis. bagian aplikasi, infrastruktur, keamanan) terdefinisi secara formal?",
                 "6.3 Apakah peran dan tanggung jawab setiap jabatan TI tercantum dalam uraian tugas?",
                 "6.4 Apakah pemisahan tugas pada fungsi TI yang kritis (mis. pengembang dan operator) diterapkan?",
                 "6.5 Apakah kebijakan dan struktur TI ditinjau berkala serta dipahami seluruh unit?"]},
            {"kode": "APO02", "judul": "Mengelola strategi",
             "pertanyaan": "Apakah rencana strategis TI selaras dengan strategi bisnis perusahaan?",
             "indikator": [
                 "7.1 Apakah rencana strategis TI tertulis dan disahkan oleh manajemen?",
                 "7.2 Apakah rencana strategis TI memetakan tujuan bisnis ke tujuan TI?",
                 "7.3 Apakah rencana strategis TI memuat peta jalan (roadmap) inisiatif, jadwal, dan anggaran?",
                 "7.4 Apakah pencapaian rencana strategis TI dipantau secara berkala?",
                 "7.5 Apakah rencana strategis TI ditinjau ulang ketika strategi bisnis atau teknologi berubah?"]},
            {"kode": "APO03", "judul": "Mengelola sumber daya manusia",
             "pertanyaan": "Apakah SDM TI memiliki kompetensi memadai dan mendapat pelatihan yang terencana?",
             "indikator": [
                 "8.1 Apakah kebutuhan jumlah dan kompetensi SDM TI dipetakan secara tertulis?",
                 "8.2 Apakah rekrutmen dan penempatan SDM TI mengacu pada kompetensi yang dibutuhkan?",
                 "8.3 Apakah rencana pelatihan TI tahunan tersedia dan dijalankan?",
                 "8.4 Apakah kinerja dan kompetensi SDM TI dievaluasi secara berkala?",
                 "8.5 Apakah risiko ketergantungan pada individu tertentu dikelola (mis. dokumentasi, pengganti, serah terima)?"]},
            {"kode": "APO04", "judul": "Mengelola risiko",
             "pertanyaan": "Apakah perusahaan mengidentifikasi, menilai, dan menangani risiko TI secara sistematis?",
             "indikator": [
                 "9.1 Apakah ada prosedur tertulis untuk mengidentifikasi risiko TI?",
                 "9.2 Apakah risiko dinilai berdasarkan kemungkinan dan dampak dengan kriteria yang baku?",
                 "9.3 Apakah daftar risiko (risk register) TI dibuat dan diperbarui secara berkala?",
                 "9.4 Apakah setiap risiko memiliki rencana penanganan, penanggung jawab, dan tenggat waktu?",
                 "9.5 Apakah efektivitas penanganan risiko dipantau dan dilaporkan?"]},
            {"kode": "APO05", "judul": "Mengelola keamanan",
             "pertanyaan": "Apakah sistem manajemen keamanan informasi (kebijakan, akses, klasifikasi data) sudah diterapkan?",
             "indikator": [
                 "10.1 Apakah kebijakan keamanan informasi tertulis, disahkan, dan disosialisasikan?",
                 "10.2 Apakah data diklasifikasikan berdasarkan tingkat kerahasiaannya (mis. data pelanggan dan alamat kiriman)?",
                 "10.3 Apakah pengelolaan hak akses diatur secara formal (pemberian, perubahan, pencabutan)?",
                 "10.4 Apakah ada program kesadaran keamanan informasi bagi karyawan?",
                 "10.5 Apakah penerapan keamanan informasi diaudit atau ditinjau berkala dan temuannya diperbaiki?"]},
        ],
    },
    "BAI": {
        "nama": "Build, Acquire and Implement",
        "deskripsi": "Pembangunan, pengadaan, dan implementasi solusi TI",
        "butir": [
            {"kode": "BAI01", "judul": "Mengelola program dan proyek",
             "pertanyaan": "Apakah proyek TI direncanakan, dikendalikan, dan dievaluasi pascaimplementasi?",
             "indikator": [
                 "11.1 Apakah setiap proyek TI memiliki rencana tertulis (lingkup, jadwal, anggaran, penanggung jawab)?",
                 "11.2 Apakah proyek TI disetujui secara formal sebelum dimulai?",
                 "11.3 Apakah kemajuan, biaya, dan risiko proyek dipantau secara berkala?",
                 "11.4 Apakah perubahan lingkup, jadwal, atau anggaran proyek dikendalikan dan disetujui?",
                 "11.5 Apakah evaluasi pascaimplementasi dilakukan dan pembelajaranannya didokumentasikan?"]},
            {"kode": "BAI02", "judul": "Mengelola definisi kebutuhan",
             "pertanyaan": "Apakah kebutuhan bisnis dan pengguna didefinisikan dan disetujui sebelum solusi dibangun?",
             "indikator": [
                 "12.1 Apakah kebutuhan bisnis dan pengguna dikumpulkan melalui cara yang terstruktur (mis. wawancara, workshop)?",
                 "12.2 Apakah kebutuhan didokumentasikan dengan jelas (fungsional dan nonfungsional)?",
                 "12.3 Apakah kebutuhan divalidasi oleh pengguna atau pemilik proses?",
                 "12.4 Apakah kebutuhan disetujui secara tertulis sebelum pembangunan dimulai?",
                 "12.5 Apakah perubahan kebutuhan dikelola dan dapat ditelusuri ke solusi yang dihasilkan?"]},
            {"kode": "BAI03", "judul": "Mengelola identifikasi dan pembangunan solusi",
             "pertanyaan": "Apakah pembangunan atau pengadaan aplikasi melalui desain, pengujian, dan persetujuan?",
             "indikator": [
                 "13.1 Apakah ada metodologi atau standar pengembangan/pengadaan aplikasi yang baku?",
                 "13.2 Apakah desain solusi didokumentasikan dan ditinjau sebelum dibangun?",
                 "13.3 Apakah pengadaan dari pihak ketiga melalui evaluasi dan seleksi yang terdokumentasi?",
                 "13.4 Apakah pengujian (unit, integrasi, penerimaan pengguna) dilakukan dan hasilnya didokumentasikan?",
                 "13.5 Apakah persetujuan tertulis diperoleh sebelum solusi dioperasikan (go-live)?"]},
            {"kode": "BAI04", "judul": "Mengelola perubahan",
             "pertanyaan": "Apakah perubahan sistem dikendalikan melalui permintaan, persetujuan, dan dokumentasi?",
             "indikator": [
                 "14.1 Apakah ada prosedur permintaan perubahan (change request) yang tertulis?",
                 "14.2 Apakah setiap perubahan dinilai dampak dan risikonya sebelum disetujui?",
                 "14.3 Apakah perubahan disetujui oleh pihak yang berwenang sebelum dilaksanakan?",
                 "14.4 Apakah perubahan diuji dan memiliki rencana pemulihan (rollback)?",
                 "14.5 Apakah seluruh perubahan dicatat dan dokumentasi sistem diperbarui?"]},
            {"kode": "BAI05", "judul": "Mengelola konfigurasi",
             "pertanyaan": "Apakah aset dan konfigurasi TI (server, aplikasi, jaringan) tercatat dan dijaga akurat?",
             "indikator": [
                 "15.1 Apakah tersedia inventaris aset TI (server, aplikasi, perangkat jaringan, lisensi) yang lengkap?",
                 "15.2 Apakah setiap aset memiliki atribut konfigurasi yang tercatat (mis. versi, lokasi, pemilik)?",
                 "15.3 Apakah inventaris diperbarui ketika ada penambahan, perubahan, atau penghapusan aset?",
                 "15.4 Apakah inventaris diverifikasi secara berkala terhadap kondisi nyata?",
                 "15.5 Apakah pencatatan konfigurasi terhubung dengan proses perubahan dan penanganan insiden?"]},
        ],
    },
    "DSS": {
        "nama": "Deliver, Service and Support",
        "deskripsi": "Penyampaian layanan, operasional, dan dukungan TI",
        "butir": [
            {"kode": "DSS01", "judul": "Mengelola operasi",
             "pertanyaan": "Apakah operasional TI harian (jadwal, pemantauan sistem, pencadangan) dijalankan sesuai prosedur?",
             "indikator": [
                 "16.1 Apakah prosedur operasional TI harian tertulis (SOP)?",
                 "16.2 Apakah jadwal operasional (mis. pemrosesan data, pemeliharaan) ditetapkan dan dijalankan?",
                 "16.3 Apakah kinerja dan ketersediaan sistem (server, aplikasi pelacakan) dipantau?",
                 "16.4 Apakah pencadangan (backup) dilakukan sesuai jadwal dan hasil pemulihannya diuji?",
                 "16.5 Apakah penyimpangan operasional dicatat dan ditindaklanjuti?"]},
            {"kode": "DSS02", "judul": "Mengelola permintaan layanan dan insiden",
             "pertanyaan": "Apakah insiden dan permintaan layanan dicatat, diprioritaskan, dan diselesaikan sesuai target waktu?",
             "indikator": [
                 "17.1 Apakah ada prosedur baku pencatatan insiden dan permintaan layanan?",
                 "17.2 Apakah tersedia sarana pencatatan (mis. helpdesk atau sistem tiket) yang digunakan?",
                 "17.3 Apakah insiden diklasifikasikan dan diprioritaskan berdasarkan dampaknya?",
                 "17.4 Apakah target waktu penyelesaian (SLA) ditetapkan dan dipantau?",
                 "17.5 Apakah insiden ditutup dengan konfirmasi pengguna dan tren insiden dianalisis?"]},
            {"kode": "DSS03", "judul": "Mengelola masalah",
             "pertanyaan": "Apakah akar masalah dari insiden berulang dianalisis dan diperbaiki permanen?",
             "indikator": [
                 "18.1 Apakah ada prosedur pengelolaan masalah (problem management) yang tertulis?",
                 "18.2 Apakah insiden berulang diidentifikasi dan dikelompokkan?",
                 "18.3 Apakah analisis akar masalah dilakukan dengan metode yang jelas?",
                 "18.4 Apakah solusi permanen diterapkan dan dicatat, bukan hanya perbaikan sementara?",
                 "18.5 Apakah basis pengetahuan (known error) dikelola dan dimanfaatkan untuk pencegahan?"]},
            {"kode": "DSS04", "judul": "Mengelola keberlangsungan",
             "pertanyaan": "Apakah rencana kelangsungan bisnis dan pemulihan bencana (BCP/DRP) tersedia dan pernah diuji?",
             "indikator": [
                 "19.1 Apakah rencana kelangsungan bisnis (BCP) tertulis dan disahkan?",
                 "19.2 Apakah rencana pemulihan bencana (DRP) tersedia untuk sistem yang kritis?",
                 "19.3 Apakah proses dan sistem kritis beserta target waktu pemulihannya (RTO/RPO) ditetapkan?",
                 "19.4 Apakah BCP/DRP diuji secara berkala dan hasilnya didokumentasikan?",
                 "19.5 Apakah rencana diperbarui berdasarkan hasil pengujian atau perubahan sistem?"]},
            {"kode": "DSS05", "judul": "Mengelola layanan keamanan",
             "pertanyaan": "Apakah kontrol keamanan (hak akses, antivirus, firewall, pemantauan) berjalan efektif?",
             "indikator": [
                 "20.1 Apakah hak akses pengguna diberikan sesuai kebutuhan tugas (prinsip least privilege)?",
                 "20.2 Apakah hak akses ditinjau berkala dan dicabut ketika tidak lagi diperlukan?",
                 "20.3 Apakah perlindungan jaringan dan perangkat (firewall, antivirus, pembaruan keamanan) aktif dan terkini?",
                 "20.4 Apakah log akses dan aktivitas sistem dipantau?",
                 "20.5 Apakah kerentanan dan insiden keamanan dievaluasi (mis. uji penetrasi) dan ditindaklanjuti?"]},
        ],
    },
    "MEA": {
        "nama": "Monitor, Evaluate and Assess",
        "deskripsi": "Pemantauan kinerja, pengendalian internal, dan kepatuhan",
        "butir": [
            {"kode": "MEA01", "judul": "Menetapkan pendekatan pemantauan",
             "pertanyaan": "Apakah indikator kinerja TI (KPI) sudah ditetapkan dan disepakati?",
             "indikator": [
                 "21.1 Apakah indikator kinerja TI (KPI) telah ditetapkan secara tertulis?",
                 "21.2 Apakah KPI selaras dengan tujuan bisnis dan tujuan TI?",
                 "21.3 Apakah setiap KPI memiliki definisi, target, dan cara pengukuran yang jelas?",
                 "21.4 Apakah KPI disepakati oleh pemangku kepentingan?",
                 "21.5 Apakah KPI ditinjau dan disesuaikan secara berkala?"]},
            {"kode": "MEA02", "judul": "Menganalisis dan melaporkan kinerja",
             "pertanyaan": "Apakah kinerja TI dianalisis dan dilaporkan secara berkala?",
             "indikator": [
                 "22.1 Apakah data kinerja TI dikumpulkan secara berkala sesuai KPI?",
                 "22.2 Apakah keakuratan data kinerja divalidasi?",
                 "22.3 Apakah kinerja TI dianalisis terhadap target yang ditetapkan?",
                 "22.4 Apakah laporan kinerja disampaikan kepada manajemen sesuai jadwal?",
                 "22.5 Apakah laporan memuat rekomendasi yang ditindaklanjuti?"]},
            {"kode": "MEA03", "judul": "Memantau pengendalian internal",
             "pertanyaan": "Apakah pengendalian internal TI dipantau dan dievaluasi efektivitasnya?",
             "indikator": [
                 "23.1 Apakah pengendalian internal TI teridentifikasi dan terdokumentasi?",
                 "23.2 Apakah ada jadwal pemantauan atau penilaian pengendalian internal TI?",
                 "23.3 Apakah pemantauan dilakukan oleh pihak yang kompeten dan independen?",
                 "23.4 Apakah hasil pemantauan pengendalian didokumentasikan?",
                 "23.5 Apakah efektivitas pengendalian dievaluasi dan hasilnya dipakai untuk perbaikan?"]},
            {"kode": "MEA04", "judul": "Mengidentifikasi dan melaporkan kelemahan kontrol",
             "pertanyaan": "Apakah temuan kelemahan kontrol dilaporkan dan ditindaklanjuti sampai tuntas?",
             "indikator": [
                 "24.1 Apakah kelemahan kontrol dari audit, pemantauan, atau insiden dicatat?",
                 "24.2 Apakah kelemahan dinilai dan diklasifikasikan berdasarkan tingkat keparahannya?",
                 "24.3 Apakah kelemahan dilaporkan kepada manajemen yang berwenang?",
                 "24.4 Apakah rencana tindak lanjut memiliki penanggung jawab dan tenggat waktu?",
                 "24.5 Apakah status tindak lanjut dipantau sampai tuntas dan diverifikasi?"]},
            {"kode": "MEA05", "judul": "Mengidentifikasi persyaratan kepatuhan eksternal",
             "pertanyaan": "Apakah perusahaan memahami dan mematuhi regulasi terkait TI (mis. UU PDP, UU ITE)?",
             "indikator": [
                 "25.1 Apakah tersedia daftar regulasi terkait TI (mis. UU PDP, UU ITE)?",
                 "25.2 Apakah ada penanggung jawab yang memantau persyaratan kepatuhan?",
                 "25.3 Apakah persyaratan regulasi diterjemahkan ke dalam kebijakan dan prosedur internal?",
                 "25.4 Apakah tingkat kepatuhan dinilai dan dilaporkan secara berkala?",
                 "25.5 Apakah perubahan regulasi dipantau dan ditindaklanjuti?"]},
        ],
    },
}

# ============================================================
# SESSION STATE
# ============================================================
if "jawaban" not in st.session_state:
    st.session_state.jawaban = {}
if "bukti" not in st.session_state:
    st.session_state.bukti = {}
if "identitas" not in st.session_state:
    st.session_state.identitas = {}
if "temuan" not in st.session_state:
    st.session_state.temuan = [{"temuan": "", "rekomendasi": ""} for _ in range(4)]
if "halaman" not in st.session_state:
    st.session_state.halaman = "Identitas"

# ============================================================
# FUNGSI PERHITUNGAN
# ============================================================
def hitung_skor_butir(kode, jumlah=5):
    nilai = [st.session_state.jawaban.get((kode, i)) for i in range(jumlah)]
    nilai = [v for v in nilai if v is not None]
    if not nilai:
        return None
    return round(sum(nilai) / len(nilai), 2)

def hitung_rekap():
    hasil = {}
    for dk, dd in KUISIONER.items():
        total = 0.0
        detail = []
        for butir in dd["butir"]:
            skor = hitung_skor_butir(butir["kode"], len(butir["indikator"]))
            detail.append({"kode": butir["kode"], "skor": skor})
            if skor is not None:
                total += skor
        rata2 = total / len(dd["butir"]) if dd["butir"] else 0
        hasil[dk] = {
            "nama": dd["nama"],
            "total": round(total, 2),
            "rata2": round(rata2, 2),
            "kategori": kategori_dari_skor(rata2),
            "gap": round(5 - rata2, 2),
            "detail": detail,
        }
    total_semua = sum(v["total"] for v in hasil.values())
    jumlah_butir = sum(len(v["butir"]) for v in KUISIONER.values())
    rata2_semua = total_semua / jumlah_butir if jumlah_butir else 0
    hasil["_total"] = {
        "total": round(total_semua, 2),
        "rata2": round(rata2_semua, 2),
        "kategori": kategori_dari_skor(rata2_semua),
        "gap": round(5 - rata2_semua, 2),
    }
    return hasil

def jumlah_terisi():
    return len(st.session_state.jawaban)

def total_indikator():
    return sum(len(b["indikator"]) for d in KUISIONER.values() for b in d["butir"])

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.title("📋 Audit COBIT 5")
    st.caption("PT Nusantara Logistik Digital")
    st.divider()
    halaman = st.radio(
        "Navigasi",
        ["Identitas", "Pengisian Form", "Rekapitulasi", "Temuan & Rekomendasi", "Ekspor"],
        index=["Identitas", "Pengisian Form", "Rekapitulasi", "Temuan & Rekomendasi", "Ekspor"].index(st.session_state.halaman),
    )
    st.session_state.halaman = halaman
    st.divider()
    progress = jumlah_terisi() / total_indikator() if total_indikator() else 0
    st.metric("Progress Pengisian", f"{jumlah_terisi()}/{total_indikator()}")
    st.progress(progress)
    st.caption(f"✅ {progress*100:.1f}% indikator terisi")
    st.divider()
    st.caption("**Skala Penilaian:**")
    for k, v in SKALA.items():
        st.caption(f"{k} = {v}")

# ============================================================
# HALAMAN: IDENTITAS
# ============================================================
if st.session_state.halaman == "Identitas":
    st.title("📋 Form Audit Sistem Informasi")
    st.subheader("Berbasis Kerangka Kerja COBIT 5")
    st.info("**Objek Audit:** PT Nusantara Logistik Digital (perusahaan fiktif jasa pengiriman barang berbasis aplikasi)")
    st.header("A. Identitas Audit")
    c1, c2 = st.columns(2)
    with c1:
        nama_perusahaan = st.text_input("Nama Perusahaan", value=st.session_state.identitas.get("nama_perusahaan", "PT Nusantara Logistik Digital"))
        nama_auditor = st.text_input("Nama Auditor / Jabatan", value=st.session_state.identitas.get("nama_auditor", "Auditor Internal"))
        tanggal_audit = st.date_input("Tanggal Audit", value=date(2026, 10, 25))
    with c2:
        sistem_diaudit = st.text_input("Sistem yang Diaudit", value=st.session_state.identitas.get("sistem_diaudit", "Aplikasi pemesanan, pelacakan kiriman, dan sistem pergudangan"))
        nama_auditee = st.text_input("Nama Auditee / Jabatan", value=st.session_state.identitas.get("nama_auditee", "Kepala Divisi Teknologi Informasi"))
        ruang_lingkup = st.text_input("Ruang Lingkup", value=st.session_state.identitas.get("ruang_lingkup", "5 domain COBIT 5 (EDM, APO, BAI, DSS, MEA), 25 butir audit"))
    st.session_state.identitas = {
        "nama_perusahaan": nama_perusahaan,
        "sistem_diaudit": sistem_diaudit,
        "ruang_lingkup": ruang_lingkup,
        "nama_auditor": nama_auditor,
        "nama_auditee": nama_auditee,
        "tanggal_audit": str(tanggal_audit),
    }
    st.divider()
    st.header("B. Petunjuk Pengisian")
    st.markdown("""
    1. Form terdiri dari **5 domain COBIT 5**. Setiap domain berisi **5 butir audit**, dan setiap butir dinilai melalui **5 indikator audit** (total **125 indikator**).
    2. Setiap indikator dinilai pada skala **1 sampai 5**.
    3. **Skor butir** = rata-rata dari 5 indikatornya.
    4. Isi kolom **Bukti audit / catatan** dengan dokumen, hasil wawancara, atau observasi.
    5. **Skor domain** = jumlah skor 5 butir (maksimum 25).
    """)
    st.header("Skala Penilaian")
    skala_df = pd.DataFrame([{"Skor": k, "Kategori": v, "Penjelasan": SKALA_DESKRIPSI[k]} for k, v in SKALA.items()])
    st.dataframe(skala_df, use_container_width=True, hide_index=True)
    st.divider()
    if st.button("➡️ Mulai Pengisian Form", type="primary", use_container_width=True):
        st.session_state.halaman = "Pengisian Form"
        st.rerun()

# ============================================================
# HALAMAN: PENGISIAN FORM
# ============================================================
elif st.session_state.halaman == "Pengisian Form":
    st.title("📝 Pengisian Form Audit COBIT 5")
    st.caption("Pilih skor 1-5 untuk setiap indikator dan isi bukti audit/catatan.")
    tabs = st.tabs([f"{dk} · {dd['nama']}" for dk, dd in KUISIONER.items()])
    for tab, (dk, dd) in zip(tabs, KUISIONER.items()):
        with tab:
            st.subheader(f"{dk} — {dd['nama']}")
            st.caption(f"*{dd['deskripsi']}*")
            st.divider()
            for butir in dd["butir"]:
                kode = butir["kode"]
                with st.expander(f"**{kode}** · {butir['judul']}", expanded=True):
                    st.markdown(f"**Pertanyaan:** {butir['pertanyaan']}")
                    st.markdown("---")
                    for idx, ind in enumerate(butir["indikator"]):
                        key = (kode, idx)
                        current = st.session_state.jawaban.get(key)
                        cols = st.columns([5, 1, 1, 1, 1, 1])
                        with cols[0]:
                            st.markdown(f"<div style='padding-top:8px'>{ind}</div>", unsafe_allow_html=True)
                        for j, skor in enumerate([1, 2, 3, 4, 5]):
                            with cols[j + 1]:
                                btn_type = "primary" if current == skor else "secondary"
                                if st.button(str(skor), key=f"btn_{kode}_{idx}_{skor}", type=btn_type,
                                             help=f"{SKALA[skor]}: {SKALA_DESKRIPSI[skor]}", use_container_width=True):
                                    st.session_state.jawaban[key] = skor
                                    st.rerun()
                    st.markdown("**Bukti audit / catatan:**")
                    st.session_state.bukti[kode] = st.text_area(
                        "bukti", value=st.session_state.bukti.get(kode, ""),
                        placeholder="Tulis dokumen, hasil wawancara, atau observasi...",
                        key=f"bukti_{kode}", label_visibility="collapsed", height=80,
                    )
                    skor_butir = hitung_skor_butir(kode)
                    if skor_butir is not None:
                        st.success(f"**Skor Butir:** {skor_butir} — {kategori_dari_skor(skor_butir)}")
                    else:
                        st.warning("Skor butir: belum ada indikator yang dinilai.")
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ Kembali ke Identitas", use_container_width=True):
            st.session_state.halaman = "Identitas"
            st.rerun()
    with c2:
        if st.button("➡️ Lihat Rekapitulasi", type="primary", use_container_width=True):
            st.session_state.halaman = "Rekapitulasi"
            st.rerun()

# ============================================================
# HALAMAN: REKAPITULASI
# ============================================================
elif st.session_state.halaman == "Rekapitulasi":
    st.title("📊 Lembar Rekapitulasi Hasil Audit")

    terisi = jumlah_terisi()
    total = total_indikator()
    if terisi < total:
        st.warning(f"⚠️ Baru {terisi}/{total} indikator yang terisi. Skor mungkin belum final.")

    hasil = hitung_rekap()

    st.subheader("Rekap per Domain")
    rekap_df = pd.DataFrame([
        {
            "Domain": dk,
            "Nama Domain": hasil[dk]["nama"],
            "Total Skor (maks 25)": hasil[dk]["total"],
            "Rata-rata": hasil[dk]["rata2"],
            "Kategori": hasil[dk]["kategori"],
            "Gap terhadap 5": hasil[dk]["gap"],
        }
        for dk in ["EDM", "APO", "BAI", "DSS", "MEA"]
    ])
    st.dataframe(rekap_df, use_container_width=True, hide_index=True)

    t = hasil["_total"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Skor", f"{t['total']} / 125")
    c2.metric("Rata-rata", t["rata2"])
    c3.metric("Kategori", t["kategori"])
    c4.metric("Gap terhadap 5", t["gap"])

    st.subheader("Grafik Rata-rata per Domain")
    chart_df = pd.DataFrame({
        "Domain": ["EDM", "APO", "BAI", "DSS", "MEA"],
        "Rata-rata": [hasil[dk]["rata2"] for dk in ["EDM", "APO", "BAI", "DSS", "MEA"]],
    }).set_index("Domain")
    st.bar_chart(chart_df)

    st.subheader("Detail Skor per Butir")
    for dk in ["EDM", "APO", "BAI", "DSS", "MEA"]:
        with st.expander(f"**{dk} — {hasil[dk]['nama']}**", expanded=False):
            detail_df = pd.DataFrame([
                {"Kode": d["kode"], "Skor Butir": d["skor"] if d["skor"] is not None else "—"}
                for d in hasil[dk]["detail"]
            ])
            st.dataframe(detail_df, use_container_width=True, hide_index=True)

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ Kembali ke Form", use_container_width=True):
            st.session_state.halaman = "Pengisian Form"
            st.rerun()
    with c2:
        if st.button("➡️ Temuan & Rekomendasi", type="primary", use_container_width=True):
            st.session_state.halaman = "Temuan & Rekomendasi"
            st.rerun()

# ============================================================
# HALAMAN: TEMUAN & REKOMENDASI
# ============================================================
elif st.session_state.halaman == "Temuan & Rekomendasi":
    st.title("📌 Temuan Utama dan Rekomendasi")
    st.caption("Isi temuan utama dan rekomendasi berdasarkan hasil audit.")

    for i in range(4):
        st.markdown(f"### Temuan #{i+1}")
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.temuan[i]["temuan"] = st.text_area(
                "Temuan",
                value=st.session_state.temuan[i]["temuan"],
                key=f"temuan_{i}",
                placeholder="Uraikan temuan...",
                height=80,
            )
        with c2:
            st.session_state.temuan[i]["rekomendasi"] = st.text_area(
                "Rekomendasi",
                value=st.session_state.temuan[i]["rekomendasi"],
                key=f"rekom_{i}",
                placeholder="Uraikan rekomendasi...",
                height=80,
            )

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ Kembali ke Rekapitulasi", use_container_width=True):
            st.session_state.halaman = "Rekapitulasi"
            st.rerun()
    with c2:
        if st.button("➡️ Ekspor Hasil", type="primary", use_container_width=True):
            st.session_state.halaman = "Ekspor"
            st.rerun()

# ============================================================
# HALAMAN: EKSPOR
# ============================================================
elif st.session_state.halaman == "Ekspor":
    st.title("💾 Ekspor Hasil Audit")

    hasil = hitung_rekap()
    idn = st.session_state.identitas

    data_json = {
        "identitas": idn,
        "jawaban": {f"{k[0]}|{k[1]}": v for k, v in st.session_state.jawaban.items()},
        "bukti": st.session_state.bukti,
        "rekap": hasil,
        "temuan": st.session_state.temuan,
        "timestamp": datetime.now().isoformat(),
    }

    def buat_laporan_md():
        lines = []
        lines.append("# LAPORAN AUDIT SISTEM INFORMASI COBIT 5\n")
        lines.append("## A. Identitas Audit\n")
        lines.append(f"- **Nama Perusahaan:** {idn.get('nama_perusahaan', '-')}")
        lines.append(f"- **Sistem yang diaudit:** {idn.get('sistem_diaudit', '-')}")
        lines.append(f"- **Ruang Lingkup:** {idn.get('ruang_lingkup', '-')}")
        lines.append(f"- **Nama Auditor:** {idn.get('nama_auditor', '-')}")
        lines.append(f"- **Nama Auditee:** {idn.get('nama_auditee', '-')}")
        lines.append(f"- **Tanggal Audit:** {idn.get('tanggal_audit', '-')}\n")

        lines.append("## B. Rekapitulasi Hasil Audit\n")
        lines.append("| Domain | Nama Domain | Total Skor | Rata-rata | Kategori | Gap terhadap 5 |")
        lines.append("|--------|-------------|-----------|-----------|----------|----------------|")
        for dk in ["EDM", "APO", "BAI", "DSS", "MEA"]:
            d = hasil[dk]
            lines.append(f"| {dk} | {d['nama']} | {d['total']} | {d['rata2']} | {d['kategori']} | {d['gap']} |")
        t = hasil["_total"]
        lines.append(f"| **TOTAL** | — | **{t['total']}** | **{t['rata2']}** | **{t['kategori']}** | **{t['gap']}** |\n")

        lines.append("## C. Detail Skor per Butir dan Bukti\n")
        for dk in ["EDM", "APO", "BAI", "DSS", "MEA"]:
            lines.append(f"### {dk} — {hasil[dk]['nama']}\n")
            for butir, d in zip(KUISIONER[dk]["butir"], hasil[dk]["detail"]):
                lines.append(f"#### {butir['kode']} · {butir['judul']}")
                lines.append(f"*{butir['pertanyaan']}*\n")
                for i, ind in enumerate(butir["indikator"]):
                    skor_ind = st.session_state.jawaban.get((butir["kode"], i), "—")
                    lines.append(f"- {ind} → **Skor: {skor_ind}**")
                lines.append(f"\n**Skor Butir:** {d['skor'] if d['skor'] is not None else '—'}")
                b = st.session_state.bukti.get(butir["kode"], "")
                lines.append(f"**Bukti audit/catatan:** {b if b else '-'}\n")

        lines.append("## D. Temuan Utama dan Rekomendasi\n")
        lines.append("| No | Temuan | Rekomendasi |")
        lines.append("|----|--------|-------------|")
        for i, tw in enumerate(st.session_state.temuan, 1):
            lines.append(f"| {i} | {tw['temuan'] or '-'} | {tw['rekomendasi'] or '-'} |")

        lines.append("\n## E. Pengesahan\n")
        lines.append(f"**Auditor:** {idn.get('nama_auditor', '-')}\n")
        lines.append(f"**Auditee:** {idn.get('nama_auditee', '-')}")
        return "\n".join(lines)

    laporan_md = buat_laporan_md()

    st.subheader("Ringkasan")
    t = hasil["_total"]
    st.success(
        f"**Hasil Akhir:** Total skor {t['total']}/125 · "
        f"Rata-rata {t['rata2']} ({t['kategori']}) · Gap {t['gap']}"
    )
    st.info(f"Indikator terisi: **{jumlah_terisi()}/{total_indikator()}**")

    st.subheader("Unduh Hasil")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            "📥 Unduh JSON",
            data=json.dumps(data_json, ensure_ascii=False, indent=2),
            file_name=f"hasil_audit_cobit5_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
        )
    with c2:
        st.download_button(
            "📄 Unduh Laporan Markdown",
            data=laporan_md,
            file_name=f"laporan_audit_cobit5_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with c3:
        rekap_csv = pd.DataFrame([
            {
                "Domain": dk,
                "Nama Domain": hasil[dk]["nama"],
                "Total Skor": hasil[dk]["total"],
                "Rata-rata": hasil[dk]["rata2"],
                "Kategori": hasil[dk]["kategori"],
                "Gap": hasil[dk]["gap"],
            }
            for dk in ["EDM", "APO", "BAI", "DSS", "MEA"]
        ]).to_csv(index=False)
        st.download_button(
            "📊 Unduh Rekap CSV",
            data=rekap_csv,
            file_name=f"rekap_audit_cobit5_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.divider()
    with st.expander("👁️ Pratinjau Laporan Markdown", expanded=False):
        st.markdown(laporan_md)

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ Kembali ke Temuan", use_container_width=True):
            st.session_state.halaman = "Temuan & Rekomendasi"
            st.rerun()
    with c2:
        if st.button("🔄 Reset Semua Data", type="secondary", use_container_width=True):
            for key in ["jawaban", "bukti", "identitas", "temuan"]:
                st.session_state[key] = (
                    {} if key != "temuan" else [{"temuan": "", "rekomendasi": ""} for _ in range(4)]
                )
            st.success("Data telah direset.")
            st.rerun()

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption("© 2026 · Form Audit Sistem Informasi Berbasis COBIT 5 · PT Nusantara Logistik Digital (fiktif)")