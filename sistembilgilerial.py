import sys
import uuid, re # ip adresi ve mac adresi bulmak için gerekli modül
from PyQt5 import QtWidgets # PyQt5 modülü
from PyQt5.QtChart import QChartView, QChart, QPieSeries #pasta grafik oluşturmak için gerekli modül
from PyQt5.QtCore import QTimer # timer modülü
import psutil
from pynvml import *  #ekran kartı bulmak için gerekli modül
import subprocess # wifi ağları bulmak için gerekli modül
import platform,socket,psutil,logging # Sistem bilgileri
from PyQt5.QtWidgets import QLabel #label modülü

#Pencere sınıfı
class Pencere(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer() #timer nesnesi oluşturduk
        self.init_ui()
    def init_ui(self):
        self.timer.start(1000) #timer çalıştırdık

        self.ozellikler = self.getSystemInfo() # sistem bilgilerini sözlük halinde aldık

        # boş pasta grafiklerimizi oluşturduk
        self.PastaGrafik_islemci = QPieSeries()
        self.PastaGrafik_ram = QPieSeries()
        self.PastaGrafik_hdd = QPieSeries()

        self.timer.timeout.connect(self.Loop) # her saniye click adlı metodu çağırır

        # Chartları oluşturduk
        chart = QChart()
        chart.legend().hide()
        chart.addSeries(self.PastaGrafik_islemci)
        chart.createDefaultAxes()
        chart.setTitle("CPU Kullanımı") #Chart isimleri verdik
        chartview = QChartView(chart)

        chart2 = QChart()
        chart2.legend().hide()
        chart2.addSeries(self.PastaGrafik_ram)
        chart2.createDefaultAxes()
        chart2.setTitle("RAM Kullanımı")
        chartview2 = QChartView(chart2)

        chart3 = QChart()
        chart3.legend().hide()
        chart3.addSeries(self.PastaGrafik_hdd)
        chart3.createDefaultAxes()
        chart3.setTitle("Hard Disk Kullanımı")
        chartview3 = QChartView(chart3)

        # Düzenli bir görünüm için v_box oluşturduk. Grafikleri Vbox'a koyduk
        # Bu sayede grafikler alt alta göründü.
        v_box = QtWidgets.QVBoxLayout()
        v_box.addWidget(chartview)
        v_box.addWidget(chartview2)
        v_box.addWidget(chartview3)

        # h box oluşturup grafiklerin bulunduğu v boxı oluşturduğumuz h boxa koyduk
        h_box = QtWidgets.QHBoxLayout()
        h_box.addLayout(v_box)

        # Sistem bilgilerinin yazılacağı labeller için ikinci bir vbox oluşturduk
        v_box2 = QtWidgets.QVBoxLayout()

        # Sistem bilgilerinin bulunduğu 'ozellikler' isimli sözlüğümüzde gezerek
        # sözlüğün key'ini ve Value'sunu labellere yazdırıp oluşturudğumuz 2. vboxa koyduk
        for key,value in self.ozellikler.items():
            label = QLabel(key + " : " + str(value))
            v_box2.addWidget(label)
        h_box.addLayout(v_box2)  # 2. vbox'ımızı hbox'ımıza koyduk

        # Pencereye Hbox layoutumuzu atadık
        self.setLayout(h_box)

        #Pencere boyut ayarlaması ve gösterilmesi
        self.setGeometry(100, 100, 600, 800)
        self.show()

    # Sistem bilgilerini bulup sözlük halinde dönen fonksiyonumuz
    def getSystemInfo(self):
        try:
            nvmlInit()
            info = {} #boş sözlük oluşturduk

            info['İşletim sistemi'] = platform.system()
            info['platform-release'] = platform.release()
            info['platform-version'] = platform.version()
            info['architecture'] = platform.machine()
            info['bilgisayar adı'] = socket.gethostname()
            info['ip-address'] = socket.gethostbyname(socket.gethostname())
            info['mac-address'] = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
            info['İşlemci bilgileri'] = platform.processor()
            info['RAM'] = str(round(psutil.virtual_memory().total / (1024.0 ** 3))) + " GB"
            hdd = psutil.disk_usage('/')
            info['hard-drive total'] = str(hdd.total / (2 ** 30))
            info['hard-drive used'] = str(hdd.used / (2 ** 30))
            info['hard-drive free'] = str(hdd.free / (2 ** 30))
            handle = nvmlDeviceGetHandleByIndex(0)
            info['Ekran Kartı'] = str(nvmlDeviceGetName(handle))
            """
            meta_data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'])
            data = meta_data.decode('utf-8', errors="backslashreplace")
            data = data.split('\n')
            names = []
            for i in data:
                if "All User Profile" in i:
                    i = i.split(":")
                    i = i[1]
                    i = i[1:-1]
                    names.append(i)
            info['Wi-Fi Ağı'] = names[0]
            """
            return info # oluşturduğumuz sözlüğümüzü döndük
        except Exception as e:
            logging.exception(e)

    # Her saniye çalışan fonksiyonumuz
    def Loop(self):
        # Grafiklerimizi temizledik
        self.PastaGrafik_ram.clear()
        self.PastaGrafik_islemci.clear()
        self.PastaGrafik_hdd.clear()

        # İşlemci kullanımı ve ram kullanımını bulduk
        self.islemci_kullanimi = psutil.cpu_percent(0)
        self.ram_kullanimi = psutil.virtual_memory()[2]

        # İşlemci kullanımını 1. grafiğimize ekledik
        self.PastaGrafik_islemci.append("işlemci Kullanımı",self.islemci_kullanimi*3.6)
        self.PastaGrafik_islemci.append("Boşta",(100-self.islemci_kullanimi)*3.6)

        # Ram kullanımını 2. grafiğimize ekledik
        self.PastaGrafik_ram.append("Ram Kullanımı", self.ram_kullanimi*3.6)
        self.PastaGrafik_ram.append("Boşta", (100-self.ram_kullanimi)*3.6)

        # Hard disk kullanımını 3. grafiğimize ekledik
        self.kullanilan = self.ozellikler['hard-drive used']
        self.bosta = self.ozellikler['hard-drive free']
        self.PastaGrafik_hdd.append("Kullanılan", float(self.kullanilan))
        self.PastaGrafik_hdd.append("Boşta", float(self.bosta))


#Pencere nesnesi oluşturma ve yürütme
app = QtWidgets.QApplication(sys.argv)
pencere = Pencere()
sys.exit(app.exec_())
