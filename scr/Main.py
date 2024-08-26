import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon

class IslandForcast(QWidget):
    def __init__(self):
        super().__init__()
        self.city_input = QLineEdit(self)
        self.city_input.setPlaceholderText("Enter city name...")
        self.search_button = QPushButton()
        
        self.emoji_label = QLabel(self)
        self.temperature_label = QLabel(self)
        self.description_label = QLabel(self)
        
        self.humidity_icon_label = QLabel(self)
        self.humidity_label = QLabel(self)
        
        self.wind_speed_icon_label = QLabel(self)
        self.wind_speed_label = QLabel(self)
        
        self.humidity_icon = QPixmap("images/humidity_icon.png").scaled(30, 30, Qt.KeepAspectRatio)
        self.wind_speed_icon = QPixmap("images/wind_icon.png").scaled(30, 30, Qt.KeepAspectRatio)
        
        self.humidity_icon_label.setPixmap(self.humidity_icon)
        self.wind_speed_icon_label.setPixmap(self.wind_speed_icon)
        
        self.humidity_icon_label.hide()
        self.humidity_label.hide()
        self.wind_speed_icon_label.hide()
        self.wind_speed_label.hide()
        
        self.initUI()

    def initUI(self):
        self.setWindowTitle("JA Weather App")
        self.resize(300, 400)

        self.setWindowIcon(QIcon("images/app_icon.png"))

        search_icon = QIcon("images/search_icon.png")
        self.search_button.setIcon(search_icon)
        self.search_button.setIconSize(QSize(20, 20))

        self.search_button.setObjectName("search_button")
        self.temperature_label.setObjectName("temperature_label")
        self.emoji_label.setObjectName("emoji_label")
        self.description_label.setObjectName("description_label")
        self.city_input.setObjectName("city_input")

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.city_input)
        top_layout.addWidget(self.search_button)

        middle_layout = QVBoxLayout()
        middle_layout.addWidget(self.emoji_label, alignment=Qt.AlignCenter)
        middle_layout.addWidget(self.temperature_label, alignment=Qt.AlignCenter)
        middle_layout.addWidget(self.description_label, alignment=Qt.AlignCenter)

        detail_layout = QHBoxLayout()
        detail_layout.addWidget(self.humidity_icon_label)
        detail_layout.addWidget(self.humidity_label)
        detail_layout.addItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        detail_layout.addWidget(self.wind_speed_icon_label)
        detail_layout.addWidget(self.wind_speed_label)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(middle_layout)
        main_layout.addLayout(detail_layout)

        self.setLayout(main_layout)

        self.setStyleSheet("""
            QLabel, QPushButton, QLineEdit {
                font-family: Roboto;
                font-size: 16px;
            }
            QLineEdit#city_input {
                padding: 8px;
                border: 2px solid #cccccc;
                border-radius: 15px;
                margin-right: 5px;
            }
            QPushButton#search_button {
                padding: 8px;
                border: 2px solid #cccccc;
                border-radius: 15px;
                background-color: #f0f0f0;
            }
            QLabel#temperature_label {
                font-size: 40px;
                font-weight: bold;
            }
            QLabel#description_label {
                font-size: 24px;
            }             
        """)

        self.search_button.clicked.connect(self.get_weather)

    def get_weather(self):
        api_key = "25ee97e5c5e830c6c9ec6e791852f0cc"
        city = self.city_input.text()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data["cod"] == 200:
                self.display_weather(data)

        except requests.exceptions.HTTPError as http_error:
            match response.status_code:
                case 400:
                    self.display_error("Bad request\nPlease check your input")
                case 401:
                    self.display_error("Unauthorized\nInvalid API key")
                case 403:
                    self.display_error("Forbidden\nAccess is denied")
                case 404:
                    self.display_error("Not found\nCity not found")
                case 500:
                    self.display_error("Internal Server Error\nPlease try again later")
                case 502:
                    self.display_error("Bad gateway\nInvalid response from the server")
                case 503:
                    self.display_error("Service Unavailable\nServer is down")
                case 504:
                    self.display_error("Gateway Timeout\nNo response from the server")
                case _:
                    self.display_error(f"HTTP error occurred\n{http_error}")
                    
        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error:\nCheck your internet connection")
        except requests.exceptions.Timeout:   
            self.display_error("Timeout Error\nThe request timed out")
        except requests.exceptions.TooManyRedirects:
            self.display_error("Too many Redirects:\nCheck the URL")
        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Request Error:\n{req_error}")

    def display_error(self, message):
        self.temperature_label.setStyleSheet("font-size: 30px;")
        self.temperature_label.setText(message)
        self.emoji_label.clear()
        self.description_label.clear()
        self.wind_speed_label.clear()
        self.humidity_label.clear()
        self.humidity_icon_label.hide()
        self.wind_speed_icon_label.hide()

    def display_weather(self, data):
        temp_k = data["main"]["temp"]
        temp_c = temp_k - 273.15
        weather_desc = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        self.temperature_label.setText(f"{temp_c:.0f}°C")
        self.description_label.setText(weather_desc.capitalize())
        self.humidity_label.setText(f"{humidity}%\nHumidity")
        self.wind_speed_label.setText(f"{wind_speed} m/s\nWind Speed")

        icon_path = self.get_weather_icon(data["weather"][0]["id"])
        weather_icon = QPixmap(icon_path).scaled(150, 150, Qt.KeepAspectRatio)
        self.emoji_label.setPixmap(weather_icon)

        self.humidity_icon_label.show()
        self.humidity_label.show()
        self.wind_speed_icon_label.show()
        self.wind_speed_label.show()

    @staticmethod
    def get_weather_icon(weather_id):
        if 200 <= weather_id <= 232:
            return "images/thunderstorm_icon.png"
        elif 300 <= weather_id <= 321:
            return "images/drizzle_icon.png"
        elif 500 <= weather_id <= 531:
            return "images/rain_icon.png"
        elif 600 <= weather_id <= 622:
            return "images/snow_icon.png"
        elif 701 <= weather_id <= 781:
            return "images/fog_icon.png"
        elif weather_id == 800:
            return "images/clear_icon.png"
        elif 801 <= weather_id <= 804:
            return "images/cloudy_icon.png"
        else:
            return ""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    island_forcast = IslandForcast()
    island_forcast.show()
    sys.exit(app.exec_())
