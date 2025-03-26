

# E-paper Weather Display

This project uses a Raspberry Pi to display a weather dashboard on a Waveshare 7.5-inch e-paper display. It fetches weather data from OpenWeatherMap and refreshes the display at set intervals. Minimal energy consumption makes this setup ideal for continuous display without frequent updates.

![Display Photo 1](https://github.com/vbageek14/waveshare_eink_weather_dashboard/blob/master/pictures/RaspberryPi_ePaper_Weather_Display_Front.jpeg)
![Display Photo 2](https://github.com/vbageek14/waveshare_eink_weather_dashboard/blob/master/pictures/RaspberryPi_ePaper_Weather_Display_Back.jpeg)

---

## Table of Contents
- [What’s New](#whats-new-version-20)
- [Parts List](#parts-list)
- [Setup Instructions](#setup-instructions)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Running the Script](#running-the-script)
- [Setting up Automatic Updates (Cron)](#setting-up-automatic-updates-optional)
- [Repository Structure](#files-in-this-repository)
- [Troubleshooting](#troubleshooting)
- [Credit and License](#credit-and-license)

## What’s New (Version 3.0)
- **Added 7-day forecast at the bottom of display**: The forecast shows high and low temperature for that day as well as precipitation probability and weather icon.
- **Added 8-hour forecast on the right side of display**: The forcast shows time, temperature and weather icon.
- **Added date and time in the top right corner**:
- **Added UV index, sunrise and sunset times and corresponding icons**
- **Replaced text with new icons for precipation, wind speed and humidity**
- **Removed trash day reminders functionality**

### Parts List
- **Waveshare 7.5-inch e-Paper HAT**: [Purchased on Amazon](https://a.co/d/cKgyf4m). 
- **Raspberry Pi** (set up on a Pi 4 2GB RAM; any model should work except the Pi Zero without soldered headers).
- **SD card** (at least 8 GB).
- **Power supply** for the Raspberry Pi.
- **5 x 7 inch photo frame**: The one in the image was purchased at Wal-Mart.

## Setup Instructions

### Installation
1. **Clone the Project**:
   Open a terminal and run:
   ```bash
   git clone https://github.com/vbageek14/waveshare_eink_weather_dashboard.git
   cd waveshare_eink_weather_dashboard
   ```
   
2. **Install Python Libraries**:
   ```bash
   pip install pillow requests
   ```

### Configuration
1. **Add Your OpenWeatherMap API Key**:
   Sign up on [OpenWeatherMap](https://home.openweathermap.org/users/sign_up) for an API key, then open `weather.py` and add your API key where it says `API_KEY = 'XXXXXXXX'`.

2. **Customize Your Settings**:
   Edit the following user-defined settings at the top of `weather.py`:
   - `API_KEY`: Your OpenWeatherMap API key.
   - `LOCATION`: Name of the location to display (e.g., `New Orleans`).
   - `LATITUDE` and `LONGITUDE`: Coordinates for weather updates (use [Google Maps](https://maps.google.com) to find these).
   - `UNITS`: Choose `'imperial'` (Fahrenheit) or `'metric'` (Celsius). If you select 'imperial', make sure to update °C to °F in the code and MPH to M/S.
   - `CSV_OPTION`: Set this to `True` if you’d like to save a daily log of weather data in `records.csv`.
   - 
> **Note**: If you are not using a 7.5 inch Version 2 display, you will want to replace 'epd7in5_V2.py' in the 'lib' folder with the appropriate version from [Waveshare's e-Paper library](https://github.com/waveshare/e-Paper/tree/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd). Adjustments will be required for other screen sizes.

## Running the Script
1. **To Run Manually**:
   From the `e_paper_weather_display` directory, run:
   ```bash
   python weather.py
   ```
   This will fetch the weather data and update the display immediately.

## Setting up Automatic Updates (Optional)
You can set up a scheduled update every 15 minutes using `crontab`. This will make sure your display updates automatically.

In the terminal, type:
```bash
crontab -e
```
Then, add the following line at the end of the file:
```bash
*/15 * * * * /usr/bin/python /home/pi/waveshare_eink_weather_dashboard/weather.py >> /home/pi/waveshare_eink_weather_dashboard/weather_display.log 2>&1
```
- This command updates the display every 15 minutes.
- Be sure to replace `/home/pi/e_paper_weather_display/` with the path where the project is stored, if different.

If you would like to set restrictions for when to run the update, you can do the following:
```bash
*/15 6-23 * * * /usr/bin/python /home/pi/waveshare_eink_weather_dashboard/weather.py >> /home/pi/waveshare_eink_weather_dashboard/weather_display.log 2>&1
```
- This command stops the updates from 12am until 7am.

## Files in This Repository
- **weather.py**: Main script file that fetches weather data and updates the display.
- **lib/**: Contains display drivers for the Waveshare e-paper display.
- **font/** and **pic/**: Folders with fonts and images used by the display.
- **pictures/**: Sample images of the display in action.
- **records.csv**: Optional log file for weather data if `CSV_OPTION` is enabled.

## Troubleshooting
- Make sure the **API_KEY** is correct and has permissions for OpenWeatherMap’s One Call API.
- Confirm that required Python libraries (`pillow` and `requests`) are installed.
- Double-check any custom paths used in `crontab` if the automatic updates aren’t working as expected.

## Credit and License
- This project is based on the original work by [James Steele Howard](https://github.com/AbnormalDistributions). Icon designs by [Erik Flowers](https://erikflowers.github.io/weather-icons/), with some modifications, and additional icons from [Flaticon](https://www.flaticon.com/free-icons/).
- **Weather Icons**: Licensed under [SIL OFL 1.1](http://scripts.sil.org/OFL).
- **Code**: Licensed under [MIT License](http://opensource.org/licenses/mit-license.html).
- **Documentation**: Licensed under [CC BY 3.0](http://creativecommons.org/licenses/by/3.0).
