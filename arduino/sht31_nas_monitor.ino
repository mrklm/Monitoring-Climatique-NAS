#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <SHT31.h>

LiquidCrystal_I2C lcd(0x3F, 16, 2); 
SHT31 sht31;

void setup() {
  Serial.begin(9600);
  Wire.begin();
  Wire.setClock(50000); // 50kHz pour la stabilité avec les clones

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Init LCD OK !");
  delay(1000);
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Init SHT31...");

  if (sht31.begin()) {
    lcd.setCursor(0, 1);
    lcd.print("Capteur OK !");
    Serial.println("SHT31 initialise avec succes.");
  } else {
    lcd.setCursor(0, 1);
    lcd.print("Echec init SHT31");
    Serial.println("Erreur: SHT31 non trouve.");
  }
  delay(1500);
  lcd.clear();
}

void loop() {
  sht31.read();
  float temp = sht31.getTemperature();
  float hum = sht31.getHumidity();

  if (isnan(temp) || isnan(hum)) {
    lcd.setCursor(0, 0);
    lcd.print("Erreur lecture !");
    delay(2000);
    return;
  }

  lcd.setCursor(0, 0);
  lcd.print("T: ");
  lcd.print(temp, 1);
  lcd.print(" C      ");

  lcd.setCursor(0, 1);
  lcd.print("H: ");
  lcd.print(hum, 1);
  lcd.print(" %      ");

  Serial.print("DATA,");
  Serial.print(temp, 1);
  Serial.print(",");
  Serial.println(hum, 1);

  delay(2000);
}
