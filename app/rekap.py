import pandas as pd
import numpy as np
import locale
import calendar


def get_nama(data: pd.DataFrame):
    nama: pd.api.extensions.ExtensionArray = data[source_kolom_nama].array.dropna(
    )
    return list(set(nama))


def get_logs_by_nama_and_tanggal(data: pd.DataFrame, nama: str, dates: list):
    kolom = [source_kolom_masuk,
             source_kolom_istirahat_masuk, source_kolom_istirahat_keluar, source_kolom_pulang, kolom_tanggal]

    frame = data.loc[data[source_kolom_nama] == nama, kolom]
    frame.rename(columns={
        source_kolom_masuk: target_kolom_masuk,
        source_kolom_istirahat_masuk: target_kolom_scan_istirahat_1,
        source_kolom_istirahat_keluar: target_kolom_scan_istirahat_2,
        source_kolom_pulang: target_kolom_pulang
    }, inplace=True, errors='raise')

    # swap scan isitrahat 2 dan pulang jika tabel pulang kosong
    frame[target_kolom_scan_istirahat_2], frame[target_kolom_pulang] = np.where(
        pd.to_datetime(
            frame[target_kolom_scan_istirahat_2], format="%H:%M")
        > istirahat_threshold, (frame[target_kolom_pulang], frame[target_kolom_scan_istirahat_2]), (frame[target_kolom_scan_istirahat_2], frame[target_kolom_pulang]))

    # null scan istirahat 2 jika scan tidak valid akibat swap diatas
    frame[target_kolom_scan_istirahat_2] = np.where(pd.to_datetime(
        frame[target_kolom_scan_istirahat_2], format="%H:%M") > istirahat_threshold, np.nan, frame[target_kolom_scan_istirahat_2]
    )

    # add status column
    frame.insert(target_default_index, target_kolom_status, np.nan)
    frame[target_kolom_status] = np.where(pd.to_datetime(
        frame[target_kolom_masuk], format="%H:%M") < masuk_threshold, status_tepat_waktu, status_terlambat)

    # add keterangan column
    frame.insert(target_default_index,
                 target_kolom_keterangan, np.nan)

    # Format the 'Date' column without leading zeros
    frame[kolom_tanggal] = pd.to_datetime(
        frame[kolom_tanggal], format="%d/%m/%Y")

    # add missing dates
    missing_dates = pd.date_range(start=dates[0], end=dates[-1], freq="D")
    missing_dates = pd.to_datetime(
        missing_dates, format="%d/%m/%Y")

    frame = frame.set_index(kolom_tanggal)
    frame = frame.reindex(missing_dates, fill_value=np.nan,)
    frame = frame.reset_index(names=kolom_tanggal)

    # convert date format
    local = "id_ID"
    locale.setlocale(locale.LC_ALL, local)
    frame[kolom_tanggal] = pd.to_datetime(
        frame[kolom_tanggal], format="%d/%m/%Y")

    frame[kolom_tanggal] = frame[kolom_tanggal].dt.strftime("%A, %d %B %Y")

    # add no column
    element_count = frame[kolom_tanggal].count()
    element_count = [count+1 for count in range(element_count)]
    frame.insert(target_default_index, target_kolom_no, element_count)

    # find late total time
    time = pd.to_datetime(frame[target_kolom_masuk],
                          format="%H:%M", errors="coerce")
    late_time = (time - masuk_threshold).dt.total_seconds() / 60
    late_time = np.where(late_time <= 0, np.nan, late_time)

    # add late time column
    frame.insert(target_default_index, target_kolom_telat, late_time)
    total_rows_with_total_late_time = len(frame)+2
    new_len = range(total_rows_with_total_late_time)
    frame = frame.reindex(new_len)


    # add pulang cepat column
    pulang_cepat_value = 30
    absen_masuk = ~frame[target_kolom_masuk].isnull()
    tidak_absen_pulang = frame[target_kolom_pulang].isnull()

    pulang_cepat = np.where(
        absen_masuk & tidak_absen_pulang, pulang_cepat_value, np.nan)
    frame.insert(target_default_index, target_kolom_pulang_cepat, pulang_cepat)

    # change status column if pulang cepat
    is_pulang_cepat = ~frame[target_kolom_pulang_cepat].isnull()
    frame[target_kolom_status] = np.where(
        is_pulang_cepat, status_pulang_cepat, frame[target_kolom_status])
 
    # add total late time
    remove_nan = ~np.isnan(late_time)
    late_time = late_time[remove_nan].sum()

    frame.loc[kolom_total_index_rows, target_kolom_telat] = kolom_total
    frame.loc[kolom_total_value_rows, target_kolom_telat] = late_time

    # add total pulang cepat
    remove_nan = ~np.isnan(pulang_cepat)
    total_pulang_cepat = pulang_cepat[remove_nan].sum()

    frame.loc[kolom_total_index_rows, target_kolom_pulang_cepat] = kolom_total
    frame.loc[kolom_total_value_rows,
              target_kolom_pulang_cepat] = total_pulang_cepat



    # reorder column
    frame = frame[target_data_frame_set]

    # print(frame)

    return frame


istirahat_threshold = pd.to_datetime("15:00", format="%H:%M")
masuk_threshold = pd.to_datetime("09:00", format="%H:%M")

kolom_total = "Total"
kolom_total_index_rows = 31
kolom_total_value_rows = 32


# source column
source_kolom_nama = "Nama"
source_kolom_masuk = "Masuk"
source_kolom_istirahat_masuk = "Keluar"
source_kolom_istirahat_keluar = "Masuk.1"
source_kolom_pulang = "Keluar.1"
kolom_tanggal = "Tanggal"

# target column
target_kolom_no = "No"
target_kolom_masuk = "Waktu Masuk"
target_kolom_scan_istirahat_1 = "Scan Istirahat 1"
target_kolom_scan_istirahat_2 = "Scan Istirahat 2"
target_kolom_pulang = "Waktu Pulang"
target_kolom_status = "Status"
target_kolom_keterangan = "Keterangan"
target_kolom_telat = "Telat"
target_kolom_pulang_cepat = "Pulang Cepat"
target_default_index = 0
data_frame_len = 31
target_data_frame_set = [target_kolom_no, kolom_tanggal, target_kolom_masuk,
                         target_kolom_scan_istirahat_1, target_kolom_scan_istirahat_2, target_kolom_pulang, target_kolom_status, target_kolom_keterangan, target_kolom_telat, target_kolom_pulang_cepat]

# status list
status_tepat_waktu = "Datang Tepat Waktu"
status_terlambat = "Datang Terlambat"
status_tidak_hadir = "Tidak Hadir"
status_pulang_cepat = "Pulang Cepat"


def generate_dates_for_month(year, month):
    # Get the number of days in the specified month
    num_days = calendar.monthrange(year, month)[1]

    # Generate an array with dates for the specified month
    dates_array = [f"{month}/{day}/{year}" for day in range(1, num_days + 1)]

    return dates_array


def get_month_year():

    year: int = int(input("Enter the year: "))
    month: int = int(input("Enter the month (1-12): "))

    # Check if the user input is valid
    if month < 1 or month > 12:
        print("Invalid month. Please enter a number between 1 and 12.")
    else:
        # Generate dates for the specified month and year
        dates_for_month = generate_dates_for_month(year, month)
        return dates_for_month


if __name__ == "__main__":

    print("\ntata auto rekap v1.0")
    print("by: zz\n")
    print("cara pakai: ")
    print("1. download data absensi dari fingerspot offlen ges")
    print("2. sheet yang dipakai adalah sheet \" Tidak Normal \"")
    print("3. hapus kolom pertama yang tulisannya \'Perhitungan Tidak Normal \'")
    print("4. hapus kolom \'AM\' dan \'PM\' dan naikkan 2 kolom \'Masuk\' dan 2 kolom \'Keluar\'. pastikan jam sejajar dengan nama dan tanggal!")
    print("5. save file kemudian ikuti instruksi selanjutnya\n")

    logs_path = str(input("source file name (default: logs.xlsx) (fingerspot offline download): "))

    if len(logs_path)== 0:
        logs_path = "logs.xlsx"

    try:
        logs = pd.read_excel(logs_path)
    except:
        print("file not found")
        exit()

    logs_out = str(input("target file name(default: rekap.xlsx): "))
    
    if len(logs_out)== 0:
        logs_out = "rekap.xlsx"


    dates = get_month_year()

    list_nama = get_nama(logs)

    dict_log = {}

    for nama in list_nama:
        print(f"lagi ngerekap {nama} ni bos")
        log = get_logs_by_nama_and_tanggal(logs, nama, dates)
        dict_log[nama] = log
        print("done\n")


    print(f"saving file to {logs_out}\n")
    # write to excel
    with pd.ExcelWriter(logs_out) as writer:
        for nama in dict_log:
            dict_log[nama].to_excel(writer, sheet_name=nama, index=False)
    
    print("done sayang luv u")
