import numpy as np
from struct import unpack
from datetime import datetime,timedelta
import os
import re
from matplotlib import pyplot as plt
import netCDF4 as nc
from typing import Optional, Tuple

def etim_to_datetime(etim):
    """Konversi tuple waktu Sataid menjadi objek datetime Python."""
    tahun = int(str(etim[0]) + str(etim[1]))
    bulan = etim[2]
    hari = etim[3]
    jam = etim[4]
    menit = etim[5]

    dt = datetime(tahun, bulan, hari, jam, menit)
    if menit > 0:
        dt = dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    return dt

def read_sataid(fname):
    """Membaca file biner Sataid dan mengembalikan objek SataidArray."""
    def _calibration(data, cord, eint, cal):
        """Menerapkan kalibrasi dan menghasilkan koordinat."""
        lats = np.linspace(cord[4], cord[0], eint[1])
        lons = np.linspace(cord[1], cord[3], eint[0])
        calibrated_data = cal[data.astype(np.int64) - 1]
        return lats, lons, calibrated_data

    # Menggunakan 'with' memastikan file selalu ditutup, bahkan jika terjadi error.
    with open(fname, 'rb') as fi:
        recl = unpack('I', fi.read(4))
        chan = unpack('c'*8, fi.read(8))
        sate = unpack('c'*8, fi.read(8))
        fi.read(4*1) # skip
        ftim = unpack('I'*8, fi.read(4*8))
        etim = unpack('I'*8, fi.read(4*8))
        calb = unpack('I'*1, fi.read(4*1))
        fint = unpack('I'*2, fi.read(4*2))
        eres = unpack('f'*2, fi.read(4*2))
        eint = unpack('I'*2, fi.read(4*2))
        nrec = unpack('I'*2, fi.read(4*2))
        cord = unpack('f'*8, fi.read(4*8))
        ncal = unpack('I'*3, fi.read(4*3))
        fi.read(1*24) # skip
        asat = unpack('f'*6, fi.read(4*6))
        fi.read(1*32) # skip
        vers = unpack('c'*4, fi.read(1*4))
        fi.read(4*1) # recl

        nbyt = unpack('I'*1, fi.read(4*1))
        cal = np.array(unpack('f'*int(nbyt[0]/4-2), fi.read(4*int(nbyt[0]/4-2))))
        fi.read(4*1) # nbyt

        data_raw = []
        if nrec[1] == 2: # 2 Byte data
            for _ in range(eint[1]):
                nbyt = unpack('I'*1, fi.read(4*1))
                line = unpack('H'*(eint[0]), fi.read(eint[0]*2))
                data_raw.append(line[0:eint[0]])
                fi.read(nbyt[0]-eint[0]*2-8) # skip padding
                fi.read(4*1) # nbyt
        elif nrec[1] == 1: # 1 Byte data
            for _ in range(eint[1]):
                nbyt = unpack('I'*1, fi.read(4*1))
                line = unpack('B'*((nbyt[0]-8)), fi.read(((nbyt[0]-8))))
                data_raw.append(line[0:eint[0]])
                fi.read(4*1) # nbyt

    data_raw = np.asarray(data_raw)
    lats, lons, data = _calibration(data_raw, cord, eint, cal)

    # --- Konversi ke Celsius dan atur unit data ---
    channel_name_raw = b"".join(chan).decode(errors='ignore')
    channel_name = re.match(r'^[A-Za-z]+', channel_name_raw).group(0) if re.match(r'^[A-Za-z]+', channel_name_raw) else ''
    
    units = 'unknown'
    try:
        idx = SataidArray.ShortName.index(channel_name)
        if 0 <= idx <= 6:
            units = 'Reflectance'
        elif 7 <= idx <= 15:
            data = data - 273.15  # Konversi ke Celsius
            units = '°C'
    except ValueError:
        pass # Channel tidak ada di daftar ShortName, unit tetap 'unknown'

    return SataidArray(
        lats=lats, lons=lons, data=data, sate=sate, chan=chan, etim=etim,
        fint=fint, asat=asat, vers=vers, eint=eint, cord=cord, eres=eres, fname=fname,
        units=units
    )

class SataidArray:
    """
    Struktur sederhana agar data bisa diakses dan diplot seperti xarray/netcdf.
    Mendukung crop/subset data dengan fungsi .sel().
    """
    ShortName = ['V1', 'V2', 'VS', 'N1', 'N2', 'N3', 'I4', 'WV', 'W2', 'W3', 'MI', 'O3', 'IR', 'L2', 'I2', 'CO']

    def __init__(self,
                 lats: np.ndarray,
                 lons: np.ndarray,
                 data: np.ndarray,
                 sate: tuple,
                 chan: tuple,
                 etim: tuple,
                 fint: Optional[tuple] = None,
                 asat: Optional[tuple] = None,
                 vers: Optional[tuple] = None,
                 eint: Optional[tuple] = None,
                 cord: Optional[tuple] = None,
                 eres: Optional[tuple] = None,
                 fname: Optional[str] = None,
                 units: Optional[str] = None):
        self.lat = lats
        self.lon = lons
        self.data = data
        self.sate = sate
        self.chan = chan
        self.etim = etim
        self.fint = fint
        self.asat = asat
        self.vers = vers
        self.eint = eint
        self.cord = cord
        self.eres = eres
        self.fname = fname
        self.units = units

    @property
    def satellite_name(self) -> str:
        """Mengembalikan nama satelit yang sudah dibersihkan (misalnya, 'Himawari-9')."""
        if not self.sate:
            return ""
        name = b"".join(self.sate).decode(errors='replace').strip()
        return 'Himawari-9' if name == 'Himawa-9' else name

    @property
    def channel_name(self) -> str:
        """Mengembalikan nama dasar channel (misalnya, 'IR' dari 'IR_')."""
        if not self.chan:
            return ""
        raw_name = b"".join(self.chan).decode(errors='ignore')
        match = re.match(r'^[A-Za-z]+', raw_name)
        return match.group(0) if match else ''

    def _get_description_string(self):
        nadir_coord = f"{self.asat[3]:.6f}, {self.asat[4]:.6f}" if self.asat is not None else ""
        altitude = f"{self.asat[5]:.2f} km" if self.asat is not None else ""
        time_str = etim_to_datetime(self.etim).strftime("%Y-%m-%d %H:%M UTC") if self.etim is not None else ""
        dimension = f"{self.data.shape[1]}x{self.data.shape[0]}"
        resolution = f"{self.eres[0]}" if self.eres is not None else ""
        version = b"".join(self.vers).decode(errors='replace') if self.vers is not None else ""
        # Use subset lats/lons for coordinate range
        lats = self.lat
        lons = self.lon
        coord_range = (
            f"lat : {lats.min():.6f} - {lats.max():.6f}\n"
            f"lon : {lons.min():.6f} - {lons.max():.6f}"
        )
        desc = (
            "=== Data Description ===\n"
            f"Time: {time_str}\n"
            f"Channel: {self.channel_name}\n"
            f"Dimension: {dimension}\n"
            f"Resolution: {resolution}\n"
            f"Units: {self.units}\n"
            f"Sataid Version: {version}\n"
            f"Coordinate Range:\n{coord_range}\n\n"
            "=== Satellite Description ===\n"
            f"Satellite: {self.satellite_name}\n"
            f"Nadir Coordinate: {nadir_coord}\n"
            f"Altitude: {altitude}\n\n"
        )
        return desc

    def description(self):
        """Mencetak deskripsi data yang terformat."""
        print(self._get_description_string())

    def _create_plot(self, cartopy=False, coastline_resolution='10m', coastline_color='blue', cmap=None):
        """
        Metode internal untuk membuat figure plot.

        Args:
            cartopy (bool, optional): Jika True, akan merender plot menggunakan Cartopy dengan
                                fitur peta (garis pantai, perbatasan). Memerlukan paket 'cartopy'.
            coastline_resolution (str): Resolusi garis pantai untuk Cartopy ('10m', '50m', '110m').
            coastline_color (str): Warna garis pantai untuk plot Cartopy.
            cmap (str, optional): Nama colormap Matplotlib yang akan digunakan. Jika None,
                                  default akan dipilih berdasarkan unit data.
        """
        # 1. Siapkan metadata untuk judul dan properti plot
        
        # Data untuk plot sudah dalam unit yang benar (misal, Celsius)
        plot_data = self.data
        
        # Gunakan cmap yang diberikan pengguna, atau tentukan default jika tidak ada.
        plot_cmap = cmap
        
        # Tentukan properti plot (cmap, label, vmin/vmax)
        if self.units == 'Reflectance':
            colorbar_label = 'Reflectance'
            if plot_cmap is None: plot_cmap = 'gray'
            vmin, vmax = 0, 1.1
        elif self.units == '°C':
            colorbar_label = 'Brightness Temperature (°C)'
            if plot_cmap is None: plot_cmap = 'gray_r'
            vmin, vmax = -80, 60 # Range umum untuk suhu puncak awan dalam Celsius
        else:
            colorbar_label = f'Value ({self.units})' if self.units else 'Value'
            if plot_cmap is None: plot_cmap = 'gray'
            vmin, vmax = None, None

        time_str = etim_to_datetime(self.etim).strftime('%Y-%m-%d %H:%M UTC') if self.etim is not None else ""
        left_title = f"{self.satellite_name} {self.channel_name}"
        right_title = time_str

        # 2. Buat plot berdasarkan pilihan (Cartopy atau standar)
        if cartopy:
            try:
                import cartopy.crs as ccrs
                import cartopy.feature as cfeature
            except ImportError:
                print("\nError: Paket 'cartopy' diperlukan untuk plot peta.")
                print("Silakan instal menggunakan perintah: pip install cartopy matplotlib")
                return

            fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
            img = ax.imshow(
                plot_data,
                extent=(self.lon.min(), self.lon.max(), self.lat.min(), self.lat.max()),
                origin='upper', cmap=plot_cmap, vmin=vmin, vmax=vmax,
                interpolation='none', transform=ccrs.PlateCarree()
            )
            ax.coastlines(resolution=coastline_resolution, color=coastline_color, linewidth=0.8)
            ax.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor=coastline_color)
            gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
            gl.top_labels = False
            gl.right_labels = False
            gl.xlabel_style = {'size': 9}
            gl.ylabel_style = {'size': 9}

            # Menyesuaikan judul agar rata kiri dan kanan, seperti plot standar
            #fig.suptitle(left_title, x=0.125, y=0.79, ha='left', fontsize=12, fontweight='bold')
            ax.set_title(right_title, loc='right', fontsize=10, fontweight='bold')
            ax.set_title(left_title, loc='left', fontsize=10, fontweight='bold')
            # Menyesuaikan colorbar agar ukurannya proporsional
            cbar = fig.colorbar(img, ax=ax, orientation='vertical', pad=0.01, shrink=0.7)
            # Mengatur ukuran font untuk label utama colorbar
            cbar.set_label(colorbar_label, size=9)
            # Mengatur ukuran font untuk angka (tick labels) pada colorbar
            cbar.ax.tick_params(labelsize=8)
            if self.units == '°C':
                cbar.ax.invert_yaxis()
        else:
            # Plot default tanpa Cartopy
            fig, ax = plt.subplots(figsize=(10, 6))
            img = ax.imshow(plot_data, cmap=plot_cmap, extent=(self.lon.min(), self.lon.max(), self.lat.min(), self.lat.max()), aspect='auto', vmin=vmin, vmax=vmax)
            cbar = fig.colorbar(img, ax=ax, pad=0.01)
            cbar.set_label(colorbar_label, size=9)
            cbar.ax.tick_params(labelsize=8)
            if self.units == '°C':
                cbar.ax.invert_yaxis()
            #fig.suptitle(left_title, x=0.125, y=0.915, ha='left', fontsize=12, fontweight='bold')
            ax.set_title(right_title, loc='right', fontsize=10, fontweight='bold')
            ax.set_title(left_title, loc='left', fontsize=10, fontweight='bold')
            ax.set_xlabel('Longitude', fontsize=9)
            ax.set_ylabel('Latitude', fontsize=9)

        return fig

    def plot(self, cartopy=False, coastline_resolution='10m', coastline_color='blue', cmap=None):
        """
        Memvisualisasikan data Sataid secara interaktif.

        Args:
            cartopy (bool, optional): Jika True, akan merender plot menggunakan Cartopy.
            coastline_resolution (str): Resolusi garis pantai untuk Cartopy ('10m', '50m', '110m').
            coastline_color (str): Warna garis pantai untuk plot Cartopy.
            cmap (str, optional): Nama colormap Matplotlib yang akan digunakan.
        """
        fig = self._create_plot(cartopy=cartopy, coastline_resolution=coastline_resolution, coastline_color=coastline_color, cmap=cmap)
        if fig:
            plt.show()

    def savefig(self, output_file=None, cartopy=False, coastline_resolution='10m', coastline_color='blue', cmap=None):
        """
        Menyimpan visualisasi data Sataid ke sebuah file.

        Args:
            output_file (str, optional): Path untuk menyimpan file gambar. Jika None, nama file
                                         akan dibuat dari nama file input.
            cartopy (bool, optional): Jika True, akan merender plot menggunakan Cartopy.
            coastline_resolution (str): Resolusi garis pantai untuk Cartopy.
            coastline_color (str): Warna garis pantai untuk plot Cartopy.
            cmap (str, optional): Nama colormap Matplotlib yang akan digunakan.
        """
        fig = self._create_plot(cartopy=cartopy, coastline_resolution=coastline_resolution, coastline_color=coastline_color, cmap=cmap)
        if not fig:
            return # Jangan lakukan apa-apa jika plot gagal dibuat

        filename_to_save = output_file
        if filename_to_save is None and self.fname:
            filename_to_save = os.path.basename(self.fname) + '.png'

        if filename_to_save:
            print(f"Menyimpan plot ke: {filename_to_save}")
            # Menggunakan bbox_inches='tight' untuk memastikan tidak ada yang terpotong
            fig.savefig(filename_to_save, bbox_inches='tight', dpi=300)
            plt.close(fig)  # Tutup figure untuk menghemat memori

    def sel(self, latitude=None, longitude=None, method=None):
        """
        Memilih data berdasarkan koordinat.

        Dapat digunakan untuk dua tujuan:
        1. Ekstraksi Titik: Berikan lat & lon sebagai angka untuk mendapatkan nilai tunggal.
           - `sat.sel(latitude=-17, longitude=115)`
           - `sat.sel(latitude=-17, longitude=115, method='linear')`
           - `sat.sel(latitude=-17, longitude=115, method='cubic')`
        2. Ekstraksi Wilayah: Berikan lat & lon sebagai slice untuk mendapatkan SataidArray baru.
           - `sat.sel(latitude=slice(-10, 0), longitude=slice(110, 120))`

        Args:
            latitude (float or slice): Koordinat lintang atau rentang lintang.
            longitude (float or slice): Koordinat bujur atau rentang bujur.
            method (str, optional): Metode untuk ekstraksi titik ('nearest', 'linear', 'cubic').
                                    Default adalah 'nearest'. Memerlukan `scipy` untuk 'linear' dan 'cubic'.
        """
        # --- 1. Logika Ekstraksi Titik ---
        if isinstance(latitude, (int, float)) and isinstance(longitude, (int, float)):
            # Default ke 'nearest' jika method tidak disediakan
            if method is None:
                method = 'nearest'

            if method == 'nearest':
                lat_idx = np.abs(self.lat - latitude).argmin()
                lon_idx = np.abs(self.lon - longitude).argmin()
                return self.data[lat_idx, lon_idx]
            elif method in ['linear', 'cubic']:
                try:
                    from scipy.interpolate import RectBivariateSpline
                except ImportError:
                    print(f"\nError: Paket 'scipy' diperlukan untuk method='{method}'.")
                    print("Silakan instal menggunakan perintah: pip install scipy")
                    return None

                lats_interp, data_interp = (self.lat, self.data)
                # RectBivariateSpline memerlukan koordinat yang meningkat secara monoton.
                if lats_interp[0] > lats_interp[-1]:
                    lats_interp = lats_interp[::-1]
                    data_interp = data_interp[::-1, :]

                k = 3 if method == 'cubic' else 1
                interpolator = RectBivariateSpline(lats_interp, self.lon, data_interp, kx=k, ky=k)
                return interpolator(latitude, longitude)[0, 0]
            else:
                raise NotImplementedError(f"Method '{method}' tidak didukung untuk ekstraksi titik.")

        # --- 2. Logika Ekstraksi Wilayah (Slicing) ---
        lat_idx = slice(None)
        lon_idx = slice(None)
        if latitude is not None:
            if not isinstance(latitude, slice):
                raise TypeError("Untuk ekstraksi wilayah, 'latitude' harus berupa objek slice.")
            lat_min, lat_max = latitude.start, latitude.stop
            lat_idx = (self.lat >= min(lat_min, lat_max)) & (self.lat <= max(lat_min, lat_max))
        if longitude is not None:
            if not isinstance(longitude, slice):
                raise TypeError("Untuk ekstraksi wilayah, 'longitude' harus berupa objek slice.")
            lon_min, lon_max = longitude.start, longitude.stop
            lon_idx = (self.lon >= min(lon_min, lon_max)) & (self.lon <= max(lon_min, lon_max))
        data_subset = self.data[np.ix_(lat_idx, lon_idx)]
        lats_subset = self.lat[lat_idx]
        lons_subset = self.lon[lon_idx]
        # Pass all metadata for consistency
        return SataidArray(
            lats_subset, lons_subset, data_subset,
            sate=self.sate, chan=self.chan, etim=self.etim,
            fint=self.fint, asat=self.asat, vers=self.vers, eint=self.eint, cord=self.cord,
            eres=self.eres, fname=self.fname, units=self.units
        )

    def to_netcdf(self, output_filename=None):
        """
        Mengonversi dan menyimpan data SataidArray ke dalam format file NetCDF.
        Nama variabel data akan disesuaikan dengan nama channel.
        """
        if output_filename is None:
            if self.fname:
                output_filename = os.path.basename(self.fname) + '.nc'

        print(f"Menyimpan data ke: {output_filename}")
        with nc.Dataset(output_filename, 'w', format='NETCDF4') as ds:
            # --- Atribut Global ---
            ds.description = self._get_description_string()
            ds.author = "Sepriando"

            # --- Dimensi ---
            ds.createDimension('lat', self.data.shape[0])
            ds.createDimension('lon', self.data.shape[1])

            # --- Variabel Koordinat ---
            latitudes = ds.createVariable('lat', 'f4', ('lat',))
            longitudes = ds.createVariable('lon', 'f4', ('lon',))
            latitudes.units = "degrees_north"
            longitudes.units = "degrees_east"
            latitudes[:] = self.lat
            longitudes[:] = self.lon

            # --- Variabel Data ---
            # Menggunakan nama channel sebagai nama variabel, sesuai permintaan
            data_var = ds.createVariable(self.channel_name, 'f4', ('lat', 'lon',))
            data_var.long_name = f"Data from Sataid channel {self.channel_name}"
            if self.units:
                data_var.units = self.units
            data_var[:, :] = self.data

    def to_geotiff(self, output_filename=None):
        """
        Mengonversi dan menyimpan data SataidArray ke dalam format file GeoTIFF.
        Memerlukan paket 'rasterio'. Jika tidak terinstal, akan memberikan instruksi.
        """
        try:
            import rasterio
            from rasterio.transform import from_bounds
        except ImportError:
            print("\nError: Paket 'rasterio' diperlukan untuk konversi ke GeoTIFF.")
            print("Silakan instal menggunakan perintah: pip install rasterio")
            return

        if output_filename is None:
            if self.fname:
                output_filename = os.path.basename(self.fname) + '.tif'

        print(f"Menyimpan data ke: {output_filename}")

        left, right = self.lon.min(), self.lon.max()
        bottom, top = self.lat.min(), self.lat.max()
        height, width = self.data.shape
        transform = from_bounds(left, bottom, right, top, width, height)

        with rasterio.open(
            output_filename,
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=1,
            dtype=str(self.data.dtype),
            crs='EPSG:4326', # WGS84 standard lat/lon
            transform=transform
        ) as dst:
            dst.write(self.data, 1)

    def to_xarray(self):
        """
        Konversi objek SataidArray ke xarray.DataArray untuk analisis lebih lanjut.
        Memerlukan paket 'xarray'.

        Returns:
            xarray.DataArray: Objek DataArray yang berisi data dan metadata.
        """
        try:
            import xarray as xr
        except ImportError:
            print("\nError: Paket 'xarray' diperlukan untuk konversi ini.")
            print("Silakan instal menggunakan perintah: pip install xarray")
            return None

        # xarray memerlukan koordinat yang meningkat secara monoton.
        lats_xr, data_xr = (self.lat, self.data)
        if lats_xr[0] > lats_xr[-1]:
            lats_xr = lats_xr[::-1]
            data_xr = data_xr[::-1, :]

        coords = {'lat': ('lat', lats_xr), 'lon': ('lon', self.lon)}
        
        attrs = {
            'satellite': self.satellite_name,
            'channel': self.channel_name,
            'units': self.units,
            'long_name': f'Data from Sataid channel {self.channel_name}'
        }

        return xr.DataArray(data=data_xr, dims=('lat', 'lon'), coords=coords, name=self.channel_name, attrs=attrs)


if __name__ == '__main__':
    # Blok ini hanya akan berjalan jika skrip dieksekusi secara langsung
    # Ini memungkinkan skrip untuk diimpor sebagai modul tanpa menjalankan kode contoh.
    fname = '/Users/sic/Documents/sataid/data/IR20240908.Z0000'

    # Contoh penggunaan:
    sat = read_sataid(fname)
    
    # 1. Tampilkan deskripsi
    sat.description()

    # 2. Menampilkan plot sederhana (perilaku default)
    print("\nMenampilkan plot sederhana...")
    sat.plot()

    # 3. Menampilkan plot dengan peta Cartopy
    print("\nMenampilkan plot dengan peta Cartopy...")
    sat.plot(cartopy=True) # Akan menggunakan cmap default ('gray_r')

    # 3a. Menampilkan plot dengan cmap kustom ('jet')
    print("\nMenampilkan plot dengan cmap kustom ('jet')...")
    sat.plot(cartopy=True, cmap='jet')

    # 4. Menyimpan plot ke file
    print("\nMenyimpan plot dengan nama default...")
    sat.savefig(cartopy=True)

    # 5. Ekstrak nilai pada titik tertentu
    print("\nMengekstrak nilai pada titik (-17, 115)...")
    point_lat, point_lon = -17, 115
    
    # Metode 'nearest' (default)
    val_nearest = sat.sel(latitude=point_lat, longitude=point_lon)
    print(f"Nilai (nearest) pada ({point_lat}, {point_lon}) adalah: {val_nearest:.2f} {sat.units}")

    # Metode 'linear' (memerlukan scipy)
    val_linear = sat.sel(latitude=point_lat, longitude=point_lon, method='linear')
    if val_linear is not None:
        print(f"Nilai (linear)  pada ({point_lat}, {point_lon}) adalah: {val_linear:.2f} {sat.units}")

    # 6. Memotong data untuk wilayah tertentu dan menyimpannya
    print("\nMemotong data untuk wilayah Indonesia...")
    # Gunakan slice untuk menentukan rentang lintang dan bujur
    indonesia_box = sat.sel(latitude=slice(6, -11), longitude=slice(95, 141))
    indonesia_box.description()
    # Simpan plot dari data yang sudah dipotong
    indonesia_box.savefig(output_file='indonesia_box.png', cartopy=True)

    # 7. Konversi ke xarray dan gunakan fiturnya
    print("\nMengonversi ke xarray.DataArray...")
    xr_data = sat.to_xarray()
    if xr_data is not None:
        print(xr_data)
        # Contoh komputasi dengan xarray: hitung suhu rata-rata di sepanjang garis bujur
        mean_temp_by_lon = xr_data.mean(dim='lat')
        print("\nSuhu rata-rata per bujur (dihitung dengan xarray, 5 nilai pertama):")
        print(mean_temp_by_lon.isel(lon=slice(0, 5)).to_pandas())

        # Contoh lain: temukan suhu minimum di seluruh area
        min_temp = xr_data.min()
        print(f"\nSuhu minimum di seluruh area: {min_temp.item():.2f} {xr_data.units}")

    # 8. Contoh konversi ke format lain (opsional, bisa di-uncomment jika ingin dijalankan)
    # print("\nMengonversi ke NetCDF..."); sat.to_netcdf()
    # print("\nMengonversi ke GeoTIFF..."); sat.to_geotiff()