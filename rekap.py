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
        frame[target_kolom_masuk], format="%H:%M") < masuk_threshold, tepat_waktu, terlambat)

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

    # reorder column
    frame = frame[target_data_frame_set]

    print(frame)

    return frame


istirahat_threshold = pd.to_datetime("15:00", format="%H:%M")
masuk_threshold = pd.to_datetime("9:00", format="%H:%M")


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
target_default_index = 0
data_frame_len = 31
target_data_frame_set = [target_kolom_no, kolom_tanggal, target_kolom_masuk,
                         target_kolom_scan_istirahat_1, target_kolom_scan_istirahat_2, target_kolom_pulang, target_kolom_status, target_kolom_keterangan]

# status list
tepat_waktu = "Datang Tepat Waktu"
terlambat = "Datang Terlambat"
tidak_hadir = "Tidak Hadir"


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
        print(dates_for_month)

        return dates_for_month


if __name__ == "__main__":
    dates = get_month_year()

    logs = pd.read_excel('./logs.xlsx')
    list_nama = get_nama(logs)

    dict_log = {}

    for nama in list_nama:
        log = get_logs_by_nama_and_tanggal(logs, nama, dates)
        dict_log[nama] = log

    # write to excel
    with pd.ExcelWriter("./rekap.xlsx") as writer:
        for nama in dict_log:
            dict_log[nama].to_excel(writer, sheet_name=nama, index=False)
