const turf = require('@turf/turf');
const fs = require('fs');

// --- 1. DATA KOORDINAT STASIUN (Sama seperti sebelumnya) ---
const jalurBekasi = [
    { nama: "Jati Mulya", koordinat: [107.018307, -6.262964] },
    { nama: "Bekasi Barat", koordinat: [106.994399, -6.254471] },
    { nama: "Cikunir 2", koordinat: [106.976230, -6.248559] },
    { nama: "Cikunir 1", koordinat: [106.959798, -6.255401] },
    { nama: "Jatibening Baru", koordinat: [106.946296, -6.256830] },
    { nama: "Halim", koordinat: [106.899925, -6.248720] },
    { nama: "Cawang", koordinat: [106.874119, -6.249003] },
    { nama: "Ciliwung", koordinat: [106.865541, -6.243775] },
    { nama: "Cikoko", koordinat: [106.858286, -6.243528] },
    { nama: "Pancoran", koordinat: [106.839081, -6.242318] },
    { nama: "Kuningan", koordinat: [106.832683, -6.223643] },
    { nama: "Rasuna Said", koordinat: [106.830674, -6.216180] },
    { nama: "Setiabudi", koordinat: [106.827656, -6.208157] },
    { nama: "Dukuh Atas", koordinat: [106.822929, -6.204308] }
];

const jalurCibubur = [
    { nama: "Harjamukti", koordinat: [106.895651, -6.373895] },
    { nama: "Ciracas", koordinat: [106.886681, -6.326928] },
    { nama: "Kampung Rambutan", koordinat: [106.883756, -6.302154] },
    { nama: "TMII", koordinat: [106.881601, -6.295560] },
    { nama: "Cawang", koordinat: [106.874119, -6.249003] }
];

// --- 2. PROSES PENGGABUNGAN REL (MERGING) ---
console.log("Membaca dan menggabungkan rel dari export.geojson...");
const dataPetaMentah = JSON.parse(fs.readFileSync('export.geojson', 'utf8'));

// Menggabungkan semua fitur LineString menjadi satu MultiLineString besar
let combined = turf.combine(dataPetaMentah);
// Ubah MultiLineString menjadi satu LineString panjang (jika memungkinkan)
let garisUtama = turf.lineString(turf.flatten(combined).features.reduce((acc, feat) => {
    return acc.concat(feat.geometry.coordinates);
}, []));

// --- 3. FUNGSI PEMOTONG (SLICER) ---
function potongRute(daftarStasiun, kodeJalur) {
    let hasilSegmen = [];
    for (let i = 0; i < daftarStasiun.length - 1; i++) {
        let stasiunAwal = turf.point(daftarStasiun[i].koordinat);
        let stasiunAkhir = turf.point(daftarStasiun[i+1].koordinat);
        let namaRute = `${daftarStasiun[i].nama} - ${daftarStasiun[i+1].nama}`;

        try {
            // Gunakan lineSlice dengan garisUtama yang sudah digabung
            let potongan = turf.lineSlice(stasiunAwal, stasiunAkhir, garisUtama);
            potongan.properties = {
                id: `${kodeJalur}-${i + 1}`,
                nama_segmen: namaRute,
                stasiun_awal: daftarStasiun[i].nama,
                stasiun_akhir: daftarStasiun[i+1].nama
            };
            hasilSegmen.push(potongan);
            console.log(`[SUKSES] Memotong: ${namaRute}`);
        } catch (error) {
            console.error(`[GAGAL] Memotong: ${namaRute}`);
        }
    }
    return hasilSegmen;
}

// --- 4. JALANKAN DAN SIMPAN ---
let segmenBekasi = potongRute(jalurBekasi, "BKS");
let segmenCibubur = potongRute(jalurCibubur, "CBB");

const semuaSegmen = {
    type: "FeatureCollection",
    features: [...segmenBekasi, ...segmenCibubur]
};

fs.writeFileSync('rute_lrt_siap_pakai.geojson', JSON.stringify(semuaSegmen, null, 2));
console.log("\n🎉 SELESAI! Silakan buka kembali file 'rute_lrt_siap_pakai.geojson' di geojson.io");