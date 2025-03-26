import os
import sys
import csv
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import requests

# Automatically add the 'lib' directory relative to the script's location
script_dir = os.path.dirname(os.path.abspath(__file__))
lib_path = "/home/[host_name]/e_paper_weather_display/e-Paper/RaspberryPi_JetsonNano/python/lib" # Update path
sys.path.append(lib_path)

# Import Waveshare e-Paper library for Raspberry Pi
from waveshare_epd import epd7in5_V2
epd = epd7in5_V2.EPD()

# User-defined configuration for the weather API and display
API_KEY = "XXXXXXXXXXXXX"  # Your API key for openweathermap.com
LOCATION = "XXXXXXX"  # Name of location
LATITUDE = "XXXXXXX"  # Latitude
LONGITUDE = "XXXXXXX"  # Longitude
UNITS = "metric"  # imperial or metric
CSV_OPTION = True # if csv_option == True, a weather data will be appended to 'record.csv'

BASE_URL = f'https://api.openweathermap.org/data/3.0/onecall'
FONT_DIR = os.path.join(os.path.dirname(__file__), 'font')
PIC_DIR = os.path.join(os.path.dirname(__file__), 'pic')
ICON_DIR = os.path.join(PIC_DIR, 'icon')

# Initialize e-paper display
epd = epd7in5_V2.EPD()
epd.init()
epd.Clear()

# Logging configuration for both file and console
LOG_FILE = 'weather_display.log'
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Use RotatingFileHandler for log rotation (1MB file size, 3 backups)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)  # 1MB file size, 3 backups
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logger.addHandler(file_handler)

# Stream handler for logging to console
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logger.addHandler(console_handler)

# Log script start
logger.info("Weather display script started.")

# Load fonts with specific sizes for displaying weather information
font18 = ImageFont.truetype(os.path.join(FONT_DIR, 'Font.ttc'), 18)
font22 = ImageFont.truetype(os.path.join(FONT_DIR, 'Font.ttc'), 22)
font24 = ImageFont.truetype(os.path.join(FONT_DIR, 'Font.ttc'), 24)
font30 = ImageFont.truetype(os.path.join(FONT_DIR, 'Font.ttc'), 30)
font35 = ImageFont.truetype(os.path.join(FONT_DIR, 'Font.ttc'), 35)
font80 = ImageFont.truetype(os.path.join(FONT_DIR, 'Font.ttc'), 80)
COLORS = {'black': 'rgb(0,0,0)', 'white': 'rgb(255,255,255)', 'grey': 'rgb(235,235,235)'}

def fetch_weather_data():
    """Fetches weather data from the OpenWeatherMap API."""
    url = f"{BASE_URL}?lat={LATITUDE}&lon={LONGITUDE}&units={UNITS}&appid={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an exception for HTTP errors
        logging.info("Weather data fetched successfully.")
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch weather data: {e}")
        raise

def process_weather_data(data):
    """Processes fetched weather data."""
    try:
        current = data['current'] # Current weather data
        daily = data['daily'][:8] # Forecast for the next 8 days
        hourly = data['hourly'][1:9] # Hourly forecast for the next 8 hours

        # Today's weather data
        today_data = {
            "temp_current": current['temp'],
            "feels_like": current['feels_like'],
            "humidity": current['humidity'],
            "wind": current['wind_speed'],
            "report": current['weather'][0]['description'].title(),
            "icon_code": current['weather'][0]['icon'],
            "temp_max": daily[0]['temp']['max'],  
            "temp_min": daily[0]['temp']['min'], 
            "precip_percent": daily[0]['pop'] * 100,  
            "uvi": current['uvi'],
            "sunrise": convert_utc_to_est(current['sunrise']),
            "sunset": convert_utc_to_est(current['sunset']),
            "icon_code": current['weather'][0]['icon'],
            "pressure": current['pressure']
        }

        # Forecast data for the next 7 days
        forecast_data = []
        
        for day in daily[1:]:  # Skip today's data, start from the next day
            forecast_data.append({
                "day": datetime.utcfromtimestamp(day['dt']).strftime('%a'),
                "temp_max": day['temp']['max'],
                "temp_min": day['temp']['min'],
                "description": day['weather'][0]['description'],
                "precip_percent": day['pop'] * 100,
                "icon_code": day['weather'][0]['icon'],
            })

        # Hourly forecast (for the next 8 hours)
        hourly_data = []
        
        for hour in hourly:
            hourly_data.append({
                "time": convert_utc_to_est(hour['dt']),
                "temp": hour['temp'],
                "icon_code": hour['weather'][0]['icon'],
            })

        logging.info("Weather data processed successfully.")
        return today_data, forecast_data, hourly_data

    except KeyError as e:
        logging.error(f"Error processing weather data: {e}")
        raise

def is_daylight_saving_time(date):
    """Determines if a given date is within Daylight Saving Time (DST) for EST."""
    year = date.year
    
    # Find the second Sunday in March (DST start)
    march_start = datetime(year, 3, 1)
    second_sunday_march = march_start + timedelta(days=(6 - march_start.weekday() + 7) % 7)
    
    # Find the first Sunday in November (DST end)
    november_start = datetime(year, 11, 1)
    first_sunday_november = november_start + timedelta(days=(6 - november_start.weekday()) % 7)
    
    return second_sunday_march <= date < first_sunday_november

def convert_utc_to_est(utc_timestamp):
    """Converts a UTC timestamp to EST time considering DST."""
    # Ensure utc_timestamp is an integer
    if isinstance(utc_timestamp, str):
        try:
            utc_timestamp = int(utc_timestamp)
        except ValueError:
            raise ValueError(f"Invalid UTC timestamp format: {utc_timestamp}")
            
    utc_time = datetime.utcfromtimestamp(utc_timestamp)
    offset = -4 if is_daylight_saving_time(utc_time) else -5
    est_time = utc_time + timedelta(hours=offset)
    
    return est_time.strftime('%I:%M %p')

def save_to_csv(today_data):
    """Saves weather data to a CSV file for historical record."""
    if not CSV_OPTION:
        return
    try:
        with open('records.csv', 'a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d %H:%M'),
                LOCATION,
                today_data["temp_current"],
                today_data["feels_like"],
                today_data["temp_max"],
                today_data["temp_min"],
                today_data["humidity"],
                today_data["precip_percent"],
                today_data["wind"],
                today_data["sunrise"],
                today_data["sunset"],
                today_data["uvi"],
                today_data["pressure"]
            ])
        logging.info("Weather data appended to CSV.")
    except IOError as e:
        logging.error(f"Failed to save data to CSV: {e}")

def generate_display_image(today_data, forecast_data, hourly_data):
    """Generates an image for display on the e-paper screen."""
    try:
        # Create a blank canvas (7.5-inch screen size is 800x480 pixels for this model)
        template = Image.new('1', (epd.width, epd.height), 255)
        draw = ImageDraw.Draw(template)

        # Set icon size for weather icons
        icon_size = (35, 35)

        # Extract the sunrise and sunset times
        sunrise_time = today_data['sunrise']
        sunset_time = today_data['sunset']

        # Get the current date and time for the top-right corner of the screen
        now = datetime.now()
        date_time_str = now.strftime("%m/%d/%Y %I:%M %p")

        # Add the current date and time to the top-right corner
        draw.text((epd.width - 330, 10), date_time_str, font=font30, fill=COLORS['black'])

        # Add the weather icon and temperature for today
        icon_path = os.path.join(ICON_DIR, f"{today_data['icon_code']}.png")
        icon_image = Image.open(icon_path) if os.path.exists(icon_path) else None
        if icon_image:
            template.paste(icon_image, (40, 15))

        # Add today's temperature and "Feels Like" temperature
        draw.text((250, 40), f"{today_data['temp_current']:.0f}°C", font=font80, fill=COLORS['black'])
        draw.text((250, 130), f"Feels Like: {today_data['feels_like']:.0f}°C", font=font30, fill=COLORS['black'])

        # Add weather description (e.g., "clear sky")
        draw.text((250, 180), f"{today_data['report']}", font=font18, fill=COLORS['black'])
        
        # Add today's max/min temperatures
        min_temp_icon = Image.open(os.path.join(ICON_DIR, 'low_temp_icon.png'))
        min_temp_icon = min_temp_icon.resize(icon_size)
        template.paste(min_temp_icon, (40, 280))
        
        max_temp_icon = Image.open(os.path.join(ICON_DIR, 'high_temp_icon.png'))
        max_temp_icon = max_temp_icon.resize(icon_size)
        template.paste(max_temp_icon, (40, 230))

        draw.text((80, 230), f"{today_data['temp_max']:.0f}°C", font=font22, fill=COLORS['black'])
        draw.text((80, 280), f"{today_data['temp_min']:.0f}°C", font=font22, fill=COLORS['black'])

        # Add current wind and humidity data
        wind_icon = Image.open(os.path.join(ICON_DIR, 'wind_icon.png'))
        wind_icon = wind_icon.resize(icon_size)
        template.paste(wind_icon, (200, 280))
        
        humidity_icon = Image.open(os.path.join(ICON_DIR, 'humidity_icon.png'))
        humidity_icon = humidity_icon.resize(icon_size)
        template.paste(humidity_icon, (200, 230))
        
        draw.text((240, 230), f"{today_data['humidity']}%", font=font22, fill=COLORS['black'])
        draw.text((240, 280), f"{today_data['wind']:.1f} M/S", font=font22, fill=COLORS['black'])

        # Add today's precipitation data
        precip_icon = Image.open(os.path.join(ICON_DIR, 'precipitation_icon.png'))
        precip_icon = precip_icon.resize(icon_size)
        template.paste(precip_icon, (200, 330))
        draw.text((240, 330), f" {today_data['precip_percent']:.0f}%", font=font22, fill=COLORS['black'])

        # Add current UV index (UVI)
        uvi_icon = Image.open(os.path.join(ICON_DIR, 'uv-protection.png'))
        uvi_icon = uvi_icon.resize(icon_size)
        template.paste(uvi_icon, (40, 330))
        draw.text((80, 330), f"{today_data['uvi']:.0f}", font=font22, fill=COLORS['black'])

        # Add today's sunrise and sunset times
        sunrise_icon = Image.open(os.path.join(ICON_DIR, 'sunrise_icon.png'))
        sunrise_icon = sunrise_icon.resize(icon_size)
        template.paste(sunrise_icon, (360, 230))
        
        sunset_icon = Image.open(os.path.join(ICON_DIR, 'sunset_icon.png'))
        sunset_icon = sunset_icon.resize(icon_size)
        template.paste(sunset_icon, (360, 280))
        
        draw.text((400, 230), f"{sunrise_time}", font=font24, fill=COLORS['black'])
        draw.text((400, 280), f"{sunset_time}", font=font24, fill=COLORS['black'])

        # 8-day forecast at the bottom of the screen
        y_offset = 380  # Starting position for the forecast at the bottom of the screen
        vertical_space = 30  # Add extra space between the day and the high temperature
        forecast_x_offset = 40  # Shift the forecast right, adjust for better positioning
        forecast_spacing = 105  # Increase space between each day's forecast for clarity
        icon_size = (40, 40) # Resize icons for forecast to avoid overlapping

        # Loop through each day in the forecast and display the data
        for i, day in enumerate(forecast_data):
            icon_path = os.path.join(ICON_DIR, f"{day['icon_code']}.png")
            icon_image = Image.open(icon_path) if os.path.exists(icon_path) else None
            
            if icon_image:
                 # Resize the icon for forecast to the smaller size
                 icon_image = icon_image.resize(icon_size)
                 icon_x = (forecast_x_offset + 45) + (i * forecast_spacing)
                 template.paste(icon_image, (icon_x, y_offset))

            # Display the day of the week, temperatures (max & min), and precipitation
            day_x = forecast_x_offset + (i * forecast_spacing)
            draw.text((day_x, y_offset + 5), f"{day['day']}", font=font22, fill=COLORS['black'])
            draw.text((day_x, y_offset + 5 + vertical_space), f"High: {day['temp_max']:.0f}°C", font=font18, fill=COLORS['black'])
            draw.text((day_x, y_offset + 5 + vertical_space + 20), f"Low: {day['temp_min']:.0f}°C", font=font18, fill=COLORS['black'])
            draw.text((day_x, y_offset + 5 + vertical_space + 40), f"{day['precip_percent']:.0f}%", font=font18, fill=COLORS['black'])

        # Add the hourly forecast to the right side of the screen
        hourly_x_offset = 600  # Starting X position for hourly data
        hourly_y_offset = 85  # Starting Y position for hourly data

        # Loop through the hourly data and display the icon and temperature for each hour
        for i, hour in enumerate(hourly_data):
            icon_path = os.path.join(ICON_DIR, f"{hour['icon_code']}.png")
            icon_image = Image.open(icon_path) if os.path.exists(icon_path) else None
            vertical_spacing = 35 # Vertical spacing between hourly forecast entries
            if icon_image:
                icon_image = icon_image.resize(icon_size)
                template.paste(icon_image, (hourly_x_offset, (hourly_y_offset - 5) + (i * vertical_spacing)))
            
            # Display the hour and corresponding temperature
            draw.text((hourly_x_offset + 45, hourly_y_offset + (i * vertical_spacing)), f"{hour['time']} {hour['temp']:.0f}°C", font=font18, fill=COLORS['black'])
        
        logging.info("Display image generated successfully.")
        return template
    except Exception as e:
        logging.error(f"Error generating display image: {e}")
        raise
        
def display_image(image):
    """Displays the image on the e-paper screen."
    try:
        # Create a new image object to paste the generated template
        h_image = Image.new('1', (epd.width, epd.height), 255)
        h_image.paste(image, (0, 0))
        epd.display(epd.getbuffer(h_image))
        logging.info("Image displayed on e-paper successfully.")
    except Exception as e:
        logging.error(f"Failed to display image: {e}")
        raise

def main():
    """Main function to run the weather display script."""
    try:
        # Fetch weather data from API
        data = fetch_weather_data()
        
        # Process the fetched data into usable formats
        today_data, forecast_data, hourly_data  = process_weather_data(data)

        # Save the current weather data to CSV for record-keeping
        save_to_csv(today_data)
        
        # Generate the display image using the processed data
        image = generate_display_image(today_data, forecast_data, hourly_data)
        display_image(image)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
