#include <DHT.h>
#include <PMS.h>

// ---------- Pin Configuration ----------
#define DHT_PIN 6
#define DHT_TYPE DHT11

#define MQ2_PIN   A0   // LPG
#define MQ4_PIN   A1   // CH4
#define MQ7_PIN   A2   // CO
#define MQ135_PIN A3   // Air Quality

// ---------- Sensor Objects ----------
DHT dht(DHT_PIN, DHT_TYPE);
PMS pms(Serial3);  // PMS7003 connected to Serial3 (Mega pins: TX3=14, RX3=15)
PMS::DATA pmsData;

void setup() {
  Serial.begin(9600);     // USB Serial Monitor
  Serial3.begin(9600);    // PMS7003 communication
  dht.begin();

  Serial.println("====================================");
  Serial.println("🌍 AIR QUALITY MONITOR (Offline Mode)");
  Serial.println("Sensors: DHT11 + MQ2 + MQ4 + MQ7 + MQ135 + PMS7003 (Serial3)");
  Serial.println("====================================");
  delay(2000);
}

void loop() {
  // ---------- DHT11 ----------
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  // ---------- MQ sensors ----------
  int mq2_adc = analogRead(MQ2_PIN);
  int mq4_adc = analogRead(MQ4_PIN);
  int mq7_adc = analogRead(MQ7_PIN);
  int mq135_adc = analogRead(MQ135_PIN);

  float mq2_volt = mq2_adc * (5.0 / 1023.0);
  float mq4_volt = mq4_adc * (5.0 / 1023.0);
  float mq7_volt = mq7_adc * (5.0 / 1023.0);
  float mq135_volt = mq135_adc * (5.0 / 1023.0);

  // Approximate concentration calculations
  float LPG = ((5.0 - mq2_volt) / mq2_volt) * 200;
  float CH4 = ((5.0 - mq4_volt) / mq4_volt) * 150;
  float CO  = ((5.0 - mq7_volt) / mq7_volt) * 85;
  float AirQ = ((5.0 - mq135_volt) / mq135_volt) * 100;

  // Derived gas approximations from MQ135
  float Benzene = AirQ * 0.4;
  float SO2     = AirQ * 0.2;
  float NH3     = AirQ * 0.15;
  float CO2     = AirQ * 0.25;

  // ---------- PMS7003 ----------
  int pm1 = 0, pm25 = 0, pm10 = 0;
  if (pms.read(pmsData)) {
    pm1  = pmsData.PM_AE_UG_1_0;
    pm25 = pmsData.PM_AE_UG_2_5;
    pm10 = pmsData.PM_AE_UG_10_0;
  }

  // ---------- Calculate AQI ----------
  float gas_aqi = (CO + LPG + CH4 + AirQ) / 4.0;
  float pm_aqi = (pm25 + pm10) / 2.0;
  float overall_aqi = (gas_aqi + pm_aqi) / 2.0;

  // ---------- Display Results ----------
  Serial.println("------------------------------------");
  Serial.print("🌡 Temp: "); Serial.print(temp); Serial.println(" °C");
  Serial.print("💧 Humidity: "); Serial.print(hum); Serial.println(" %\n");

  Serial.print("🧪 LPG: "); Serial.print(LPG); Serial.println(" ppm");
  Serial.print("🔥 CH4: "); Serial.print(CH4); Serial.println(" ppm");
  Serial.print("☠️  CO: "); Serial.print(CO); Serial.println(" ppm");
  Serial.print("🌫 Air Quality (MQ135): "); Serial.println(AirQ);
  Serial.print("🧴 Benzene: "); Serial.print(Benzene); Serial.println(" ppm");
  Serial.print("🌋 SO₂: "); Serial.print(SO2); Serial.println(" ppm");
  Serial.print("💨 NH₃: "); Serial.print(NH3); Serial.println(" ppm");
  Serial.print("🫁 CO₂: "); Serial.print(CO2); Serial.println(" ppm\n");

  Serial.print("🌁 PM1.0: "); Serial.print(pm1); Serial.println(" µg/m³");
  Serial.print("🌁 PM2.5: "); Serial.print(pm25); Serial.println(" µg/m³");
  Serial.print("🌁 PM10: "); Serial.print(pm10); Serial.println(" µg/m³\n");

  Serial.print("✅ Overall AQI: ");
  Serial.println(overall_aqi, 2);

  if (overall_aqi < 50) Serial.println("🟢 Good");
  else if (overall_aqi < 100) Serial.println("🟡 Moderate");
  else if (overall_aqi < 200) Serial.println("🟠 Unhealthy for Sensitive Groups");
  else if (overall_aqi < 300) Serial.println("🔴 Unhealthy");
  else Serial.println("⚫ Hazardous");

  Serial.println("------------------------------------\n");

  delay(10000);  // update every 10 seconds
}
