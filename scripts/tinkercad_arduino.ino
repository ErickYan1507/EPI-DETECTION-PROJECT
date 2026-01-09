/*
 * EPI Detection System - Arduino TinkerCAD Controller v2.0
 *
 * Enhanced hardware interface for the Python EPI Detection Application.
 * Features:
 * - PIR motion detection with LED/buzzer feedback
 * - Serial communication with compliance level commands
 * - Real-time EPI detection data integration (helmet, vest, glasses)
 * - Adaptive alert system based on detection confidence
 * - Multi-sensor support (temperature, humidity, motion)
 *
 * Communication Protocol:
 * ========================
 * Arduino to Host:
 *   - "MOTION_DETECTED\n"
 *   - "SENSOR_DATA:temp=25.5,humidity=60\n"
 * 
 * Host to Arduino (Compliance Level):
 *   - "C<level>\n" (e.g., "C85\n" for 85% compliance)
 *
 * Host to Arduino (Detection Data):
 *   - "DETECT:helmet=1,vest=0,glasses=1,confidence=92\n"
 */

// ==================== PIN DEFINITIONS ====================
const int PIR_PIN = 2;           // PIR motion sensor input
const int RED_LED_PIN = 3;       // Alert LED (danger)
const int GREEN_LED_PIN = 4;     // Safe LED (compliant)
const int BUZZER_PIN = 5;        // Audio alarm
const int TEMP_SENSOR_PIN = A0;  // Temperature sensor (analog)
const int HUMIDITY_PIN = A1;     // Humidity sensor (analog)

// ==================== THRESHOLDS ====================
const int HIGH_COMPLIANCE_THRESHOLD = 80;    // Green LED threshold
const int MEDIUM_COMPLIANCE_THRESHOLD = 60;  // Yellow threshold
const int HIGH_CONFIDENCE_THRESHOLD = 85;    // High detection confidence
const int MOTION_DEBOUNCE_TIME = 300;        // Motion debounce (ms)

// ==================== GLOBAL VARIABLES ====================
int lastMotionState = LOW;
String serialBuffer = "";
unsigned long lastMotionTime = 0;
unsigned long lastSensorUpdate = 0;
const unsigned long SENSOR_UPDATE_INTERVAL = 5000; // 5 seconds

// EPI Detection state
struct DetectionState {
  bool helmet_detected;
  bool vest_detected;
  bool glasses_detected;
  int confidence;
  unsigned long lastUpdate;
} currentDetection = {false, false, false, 0, 0};

void setup() {
  // Configure pins
  pinMode(PIR_PIN, INPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(TEMP_SENSOR_PIN, INPUT);
  pinMode(HUMIDITY_PIN, INPUT);

  // Start serial at 9600 baud (standard for Arduino)
  Serial.begin(9600);
  serialBuffer.reserve(128);

  // Initialize system - all systems green
  setSystemStatus(100, true);
  
  Serial.println("[STARTUP] EPI Detection Arduino Controller v2.0");
  Serial.println("[INFO] System ready - waiting for commands");
  delay(500);
}

void loop() {
  // === MOTION DETECTION ===
  checkMotion();

  // === SERIAL COMMUNICATION ===
  processSerialData();

  // === SENSOR UPDATE ===
  if (millis() - lastSensorUpdate >= SENSOR_UPDATE_INTERVAL) {
    readAndSendSensorData();
    lastSensorUpdate = millis();
  }

  delay(50); // Small delay to prevent overwhelming the loop
}

/**
 * Check for motion events with debouncing
 */
void checkMotion() {
  int motionState = digitalRead(PIR_PIN);
  
  if (motionState == HIGH && lastMotionState == LOW) {
    unsigned long currentTime = millis();
    
    if (currentTime - lastMotionTime > MOTION_DEBOUNCE_TIME) {
      Serial.println("[MOTION] Motion detected!");
      
      // Flash pattern to indicate motion detection
      flashAlert(2, 100);
      
      lastMotionTime = currentTime;
    }
  }
  
  lastMotionState = motionState;
}

/**
 * Flash LED pattern (used for motion alerts)
 */
void flashAlert(int flashes, int duration) {
  for (int i = 0; i < flashes; i++) {
    digitalWrite(RED_LED_PIN, HIGH);
    delay(duration);
    digitalWrite(RED_LED_PIN, LOW);
    delay(duration);
  }
}

/**
 * Read sensor data and send to host
 */
void readAndSendSensorData() {
  float temperature = readTemperature();
  float humidity = readHumidity();
  
  // Send sensor data in CSV format
  Serial.print("[SENSOR] temp=");
  Serial.print(temperature);
  Serial.print(",humidity=");
  Serial.println(humidity);
}

/**
 * Read temperature from analog sensor
 * Maps 0-1023 to 0-50°C range
 */
float readTemperature() {
  int rawValue = analogRead(TEMP_SENSOR_PIN);
  float voltage = (rawValue / 1023.0) * 5.0;
  float temperature = voltage * 10.0; // Simple linear mapping
  return temperature;
}

/**
 * Read humidity from analog sensor
 * Maps 0-1023 to 0-100% range
 */
float readHumidity() {
  int rawValue = analogRead(HUMIDITY_PIN);
  float humidity = (rawValue / 1023.0) * 100.0;
  return humidity;
}

/**
 * Process incoming serial commands from the host
 */
void processSerialData() {
  while (Serial.available() > 0) {
    char incomingChar = Serial.read();
    
    if (incomingChar == '\n') {
      handleCommand(serialBuffer);
      serialBuffer = "";
    } else if (incomingChar != '\r') { // Ignore carriage return
      serialBuffer += incomingChar;
    }
  }
}

/**
 * Handle commands from the host
 * 
 * Command formats:
 * - "C85"           -> Set compliance level to 85%
 * - "DETECT:..."   -> EPI detection data
 */
void handleCommand(String command) {
  // === COMPLIANCE LEVEL COMMAND ===
  if (command.startsWith("C")) {
    int complianceLevel = command.substring(1).toInt();
    Serial.print("[CMD] Received compliance level: ");
    Serial.println(complianceLevel);
    setSystemStatus(complianceLevel, false);
  }
  
  // === DETECTION DATA COMMAND ===
  else if (command.startsWith("DETECT:")) {
    handleDetectionData(command);
  }
  
  // === UNKNOWN COMMAND ===
  else if (command.length() > 0) {
    Serial.print("[WARNING] Unknown command: ");
    Serial.println(command);
  }
}

/**
 * Handle incoming detection data from the host
 * Format: "DETECT:helmet=1,vest=0,glasses=1,confidence=92"
 */
void handleDetectionData(String command) {
  // Parse detection data
  bool helmet = extractValue(command, "helmet=") == 1;
  bool vest = extractValue(command, "vest=") == 1;
  bool glasses = extractValue(command, "glasses=") == 1;
  int confidence = extractValue(command, "confidence=");
  
  // Update detection state
  currentDetection.helmet_detected = helmet;
  currentDetection.vest_detected = vest;
  currentDetection.glasses_detected = glasses;
  currentDetection.confidence = confidence;
  currentDetection.lastUpdate = millis();
  
  // Log detection
  Serial.print("[DETECT] Helmet:");
  Serial.print(helmet ? "✓" : "✗");
  Serial.print(" Vest:");
  Serial.print(vest ? "✓" : "✗");
  Serial.print(" Glasses:");
  Serial.print(glasses ? "✓" : "✗");
  Serial.print(" Confidence:");
  Serial.print(confidence);
  Serial.println("%");
  
  // Calculate compliance and update LEDs
  int compliance = calculateCompliance(helmet, vest, glasses, confidence);
  setSystemStatus(compliance, false);
}

/**
 * Extract numeric value from command string
 * Example: extractValue("confidence=92", "confidence=") returns 92
 */
int extractValue(String str, String key) {
  int startIndex = str.indexOf(key);
  if (startIndex == -1) return 0;
  
  startIndex += key.length();
  int endIndex = str.indexOf(",", startIndex);
  if (endIndex == -1) endIndex = str.length();
  
  String valueStr = str.substring(startIndex, endIndex);
  return valueStr.toInt();
}

/**
 * Calculate compliance score based on EPI detection
 * 
 * Scoring:
 * - Helmet: 33% of score
 * - Vest: 33% of score
 * - Glasses: 34% of score
 * - Confidence multiplier applied
 */
int calculateCompliance(bool helmet, bool vest, bool glasses, int confidence) {
  // Base score: 33 points per EPI detected
  int score = 0;
  if (helmet) score += 33;
  if (vest) score += 33;
  if (glasses) score += 34;
  
  // Apply confidence multiplier (0-100%)
  score = (score * confidence) / 100;
  
  return constrain(score, 0, 100);
}

/**
 * Set system status and control LEDs/buzzer
 * 
 * Status levels:
 * - ≥ 80%: Safe (green LED, no buzzer)
 * - 60-79%: Warning (red LED, no buzzer)
 * - < 60%: Danger (red LED + buzzer)
 */
void setSystemStatus(int level, bool startup) {
  level = constrain(level, 0, 100);
  
  // Startup sequence
  if (startup) {
    // Green pulse for startup
    digitalWrite(GREEN_LED_PIN, HIGH);
    delay(300);
    digitalWrite(GREEN_LED_PIN, LOW);
    return;
  }
  
  // Safety status
  if (level >= HIGH_COMPLIANCE_THRESHOLD) {
    // ✅ SAFE - Green LED active
    digitalWrite(GREEN_LED_PIN, HIGH);
    digitalWrite(RED_LED_PIN, LOW);
    noTone(BUZZER_PIN);
    
    Serial.print("[STATUS] ✅ SAFE (Compliance: ");
    Serial.print(level);
    Serial.println("%)");
  } 
  // Warning status
  else if (level >= MEDIUM_COMPLIANCE_THRESHOLD) {
    // ⚠️ WARNING - Red LED, no sound
    digitalWrite(GREEN_LED_PIN, LOW);
    digitalWrite(RED_LED_PIN, HIGH);
    noTone(BUZZER_PIN);
    
    Serial.print("[STATUS] ⚠️ WARNING (Compliance: ");
    Serial.print(level);
    Serial.println("%)");
  } 
  // Danger status
  else {
    // 🚨 DANGER - Red LED + beeping buzzer
    digitalWrite(GREEN_LED_PIN, LOW);
    digitalWrite(RED_LED_PIN, HIGH);
    
    // Beeping pattern: 1500Hz for 500ms, pause 300ms
    tone(BUZZER_PIN, 1500, 500);
    
    Serial.print("[STATUS] 🚨 DANGER (Compliance: ");
    Serial.print(level);
    Serial.println("%)");
  }
}
