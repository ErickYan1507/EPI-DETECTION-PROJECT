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
// Automatic board pin selection (UNO / MEGA2560)
#if defined(ARDUINO_AVR_MEGA2560)
const char* BOARD_NAME = "MEGA2560";
const int PIR_PIN = 2;            // PIR motion sensor input
const int RED_LED_PIN = 5;       // Alert LED (danger) - Rouge
const int YELLOW_LED_PIN = 3;    // Warning LED (warning) - Jaune
const int GREEN_LED_PIN = 4;     // Safe LED (compliant) - Vert
const int BUZZER_PIN = 9;         // Audio alarm - Buzzer
#elif defined(ARDUINO_AVR_UNO)
const char* BOARD_NAME = "UNO";
const int PIR_PIN = 2;            // PIR motion sensor input
const int RED_LED_PIN = 5;        // Alert LED (danger) - Rouge
const int YELLOW_LED_PIN = 3;     // Warning LED (warning) - Jaune
const int GREEN_LED_PIN = 4;      // Safe LED (compliant) - Vert
const int BUZZER_PIN = 9;         // Audio alarm - Buzzer
#else
const char* BOARD_NAME = "GENERIC";
const int PIR_PIN = 2;            // Safe fallback mapping
const int RED_LED_PIN = 5;
const int YELLOW_LED_PIN = 3;
const int GREEN_LED_PIN = 4;
const int BUZZER_PIN = 9;
#endif

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

// LED Persistence State - pour maintenir les LEDs au dernier état de conformité détecté
int lastDetectionComplianceLevel = -1;  // -1 = pas de détection initiale
unsigned long lastImageDetectionTime = 0;  // Timestamp de la dernière détection d'image
const unsigned long DETECTION_TIMEOUT = 30000;  // 30 secondes avant réinitialisation

// EPI Detection state - utiliser les COMPTAGES (pas les booléens)
struct DetectionState {
  int total_persons;    // Nombre total de personne détectées
  int with_helmet;      // Nombre avec casque
  int with_vest;        // Nombre avec gilet
  int with_glasses;     // Nombre avec lunettes
  int with_boots;       // Nombre avec bottes
  unsigned long lastUpdate;
} currentDetection = {0, 0, 0, 0, 0, 0};

// LED State Tracking - pour éviter le scintillement du à des updates continues
int currentLEDState = -1;  // -1=unknown, 0=off, 1=green, 2=yellow, 3=red
bool currentBuzzerActive = false;

void setup() {
  // Configure pins
  pinMode(PIR_PIN, INPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(YELLOW_LED_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(TEMP_SENSOR_PIN, INPUT);
  pinMode(HUMIDITY_PIN, INPUT);

  // Start serial at 9600 baud (standard for Arduino)
  Serial.begin(9600);
  serialBuffer.reserve(128);

  // Initialize system - all systems green
  setSystemStatus(100, true);
  
  Serial.println("[STARTUP] EPI Detection Arduino Controller v2.2");
  Serial.println("[INFO] System ready - waiting for commands");
  Serial.print("[INFO] Board: ");
  Serial.println(BOARD_NAME);
  Serial.print("[INFO] Pin mapping: PIR=");
  Serial.print(PIR_PIN);
  Serial.print(", Red=");
  Serial.print(RED_LED_PIN);
  Serial.print(", Yellow=");
  Serial.print(YELLOW_LED_PIN);
  Serial.print(", Green=");
  Serial.print(GREEN_LED_PIN);
  Serial.print(", Buzzer=");
  Serial.println(BUZZER_PIN);
  delay(500);
}

void loop() {
  // === MOTION DETECTION ===
  checkMotion();

  // === SERIAL COMMUNICATION ===
  processSerialData();

  // === CHECK DETECTION TIMEOUT ===
  // Si aucune détection d'image reçue depuis DETECTION_TIMEOUT, réinitialiser l'état
  if (lastDetectionComplianceLevel != -1) {
    if (millis() - lastImageDetectionTime > DETECTION_TIMEOUT) {
      Serial.println("[STATUS] ⏱️ Detection timeout - Resetting LED state");
      lastDetectionComplianceLevel = -1;  // Réinitialiser
    }
  }

  // === UPDATE LEDS CONTINUOUSLY (IMPORTANT!) ===
  // Maintenir continuellement les LEDs à l'état de conformité détecté
  updateLEDsContinuously();

  // === SENSOR UPDATE ===
  if (millis() - lastSensorUpdate >= SENSOR_UPDATE_INTERVAL) {
    readAndSendSensorData();
    lastSensorUpdate = millis();
  }

  delay(50); // Small delay to prevent overwhelming the loop
}

/**
 * Check for motion events with debouncing
 * Note: Motion alerts are suppressed when image detection is active
 */
// void checkMotion() {
//   // Ne pas interférer avec les LEDs si une détection d'image est active et valide
//   if (lastDetectionComplianceLevel != -1) {
//     // Skip motion detection alerts while image detection is active
//     return;
//   }
  
//   int motionState = digitalRead(PIR_PIN);
  
//   if (motionState == HIGH && lastMotionState == LOW) {
//     unsigned long currentTime = millis();
    
//     if (currentTime - lastMotionTime > MOTION_DEBOUNCE_TIME) {
//       Serial.println("[MOTION] Motion detected!");
      
//       // Flash pattern to indicate motion detection
//       flashAlert(2, 100);
      
//       lastMotionTime = currentTime;
//     }
//   }
  
//   lastMotionState = motionState;
// }

/**
 * Flash LED pattern for motion alerts
 */
void flashAlert(int flashes, int duration) {
  for (int i = 0; i < flashes; i++) {
    // Flash red LED and beep buzzer
    digitalWrite(RED_LED_PIN, HIGH);
    tone(BUZZER_PIN, 1000, duration);
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
 * - "C85"           -> Set compliance level to 85% (PERSIST until next detection)
 * - "DETECT:..."   -> EPI detection data
 */
void handleCommand(String command) {
  // === COMPLIANCE LEVEL COMMAND ===
  if (command.startsWith("C")) {
    int complianceLevel = command.substring(1).toInt();
    Serial.print("[CMD] Image detection - Compliance level: ");
    Serial.print(complianceLevel);
    Serial.println("% (LEDs will persist until next detection)");
    
    // Afficher l'ancienne valeur pour déterminer si ça change
    Serial.print("[CMD-DEBUG] Old level: ");
    Serial.print(lastDetectionComplianceLevel);
    Serial.print(" -> New level: ");
    Serial.println(complianceLevel);
    
    // Mettre à jour l'état persistant
    lastDetectionComplianceLevel = complianceLevel;
    lastImageDetectionTime = millis();
    
    // Mettre à jour les LEDs
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
 * NEW FORMAT: "DETECT:person=5,helmet=3,vest=4,glasses=2,boots=1"
 * 
 * Arduino calcule lui-même la conformité avec la logique du système Python:
 * - 0% si aucune personne
 * - 100% si tous les EPI détectés (helmet, vest, glasses, boots)
 * - 90% si 1-2 EPI manquent
 * - 60% si 3 EPI manquent
 * - 10% si 4 EPI manquent
 */
void handleDetectionData(String command) {
  // NOUVEAU FORMAT: "DETECT:person=5,helmet=3,vest=4,glasses=2,boots=1"
  Serial.print("[DETECT-RAW] Full command received: '");
  Serial.print(command);
  Serial.println("'");
  
  // Parse detection data - NEW FORMAT with counts
  int total_persons = extractValue(command, "person=");
  int with_helmet = extractValue(command, "helmet=");
  int with_vest = extractValue(command, "vest=");
  int with_glasses = extractValue(command, "glasses=");
  int with_boots = extractValue(command, "boots=");
  
  Serial.print("[DETECT-PARSE] Raw parsed values: person=");
  Serial.print(total_persons);
  Serial.print(", helmet=");
  Serial.print(with_helmet);
  Serial.print(", vest=");
  Serial.print(with_vest);
  Serial.print(", glasses=");
  Serial.print(with_glasses);
  Serial.print(", boots=");
  Serial.println(with_boots);
  
  // Check if parsing failed
  if (total_persons == 0 && with_helmet == 0 && with_vest == 0 && with_glasses == 0 && with_boots == 0) {
    Serial.println("[DETECT-ERROR] ❌ Failed to parse any values! Command format issue?");
    return;
  }
  
  // Update detection state
  currentDetection.total_persons = total_persons;
  currentDetection.with_helmet = with_helmet;
  currentDetection.with_vest = with_vest;
  currentDetection.with_glasses = with_glasses;
  currentDetection.with_boots = with_boots;
  currentDetection.lastUpdate = millis();
  
  // Log detection
  Serial.print("[DETECT] Image detection - Persons:");
  Serial.print(total_persons);
  Serial.print(", Helmet:");
  Serial.print(with_helmet);
  Serial.print(", Vest:");
  Serial.print(with_vest);
  Serial.print(", Glasses:");
  Serial.print(with_glasses);
  Serial.print(", Boots:");
  Serial.println(with_boots);
  
  // CALCULATE COMPLIANCE LOCALLY (same logic as Python)
  int complianceLevel = calculateCompliance(total_persons, with_helmet, with_vest, with_glasses, with_boots);
  
  Serial.print("[COMPLIANCE] Calculated: ");
  Serial.print(complianceLevel);
  Serial.println("%");
  
  // Update LED state immediately with calculated compliance
  lastDetectionComplianceLevel = complianceLevel;
  lastImageDetectionTime = millis();
  
  // Update LEDs now (will be called in loop anyway, but update immediately for responsiveness)
  setSystemStatus(complianceLevel, false);
}

/**
 * Calculate compliance score using the same logic as Python
 * - 0% if no persons
 * - 100% if all EPI detected
 * - 90% if 1-2 EPI missing
 * - 60% if 3 EPI missing
 * - 10% if 4 EPI missing
 */
int calculateCompliance(int total_persons, int with_helmet, int with_vest, int with_glasses, int with_boots) {
  // DEBUG: Log input parameters
  Serial.print("[CALC-DEBUG] Inputs: persons=");
  Serial.print(total_persons);
  Serial.print(", helmet=");
  Serial.print(with_helmet);
  Serial.print(", vest=");
  Serial.print(with_vest);
  Serial.print(", glasses=");
  Serial.print(with_glasses);
  Serial.print(", boots=");
  Serial.println(with_boots);
  
  // If no persons detected, return 0%
  if (total_persons == 0) {
    Serial.println("[CALC-DEBUG] ❌ No persons detected -> returning 0%");
    return 0;
  }
  
  // Count how many EPI classes have at least one detection
  int detected_epi = 0;
  if (with_helmet > 0) detected_epi++;
  if (with_vest > 0) detected_epi++;
  if (with_glasses > 0) detected_epi++;
  if (with_boots > 0) detected_epi++;
  
  // Calculate missing EPI classes
  int missing_epi = 4 - detected_epi;
  
  Serial.print("[CALC-DEBUG] Detected EPI: ");
  Serial.print(detected_epi);
  Serial.print(" / 4, Missing: ");
  Serial.println(missing_epi);
  
  // Apply scoring rules
  int result;
  if (missing_epi == 0) {
    result = 100;  // All EPI detected
    Serial.println("[CALC-DEBUG] All EPI present -> 100%");
  } else if (missing_epi <= 2) {
    result = 90;   // 1-2 missing
    Serial.print("[CALC-DEBUG] ");
    Serial.print(missing_epi);
    Serial.println(" EPI missing -> 90%");
  } else if (missing_epi == 3) {
    result = 60;   // 3 missing
    Serial.println("[CALC-DEBUG] 3 EPI missing -> 60%");
  } else {
    result = 10;   // 4 missing (no EPI)
    Serial.println("[CALC-DEBUG] 4 EPI missing (no EPI) -> 10%");
  }
  
  return result;
  
  // Apply scoring rules
  if (missing_epi == 0) {
    return 100;  // All EPI detected
  } else if (missing_epi <= 2) {
    return 90;   // 1-2 missing
  } else if (missing_epi == 3) {
    return 60;   // 3 missing
  } else {
    return 10;   // 4 missing (no EPI)
  }
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
 * Update LEDs continuously based on last detection compliance level
 * This function must be called every loop to maintain LED state
 * IMPORTANT: This prevents LEDs from resetting when motion is detected
 */
void updateLEDsContinuously() {
  // Si pas de détection d'image, ne rien faire (garder l'état des capteurs IR)
  if (lastDetectionComplianceLevel == -1) {
    return;  // Laisser l'état normal (pas de forçage)
  }
  
  // Déterminer quel état LED on devrait avoir
  int level = lastDetectionComplianceLevel;
  int targetLEDState;
  
  if (level >= HIGH_COMPLIANCE_THRESHOLD) {
    targetLEDState = 1;  // GREEN
  } 
  else if (level >= MEDIUM_COMPLIANCE_THRESHOLD) {
    targetLEDState = 2;  // YELLOW
  } 
  else {
    targetLEDState = 3;  // RED
  }
  
  // DEBUG: Afficher l'état cible
  static int lastLoggedState = -1;
  if (lastLoggedState != targetLEDState) {
    Serial.print("[LED-DEBUG] Level=");
    Serial.print(level);
    Serial.print("%, Target=");
    Serial.print(targetLEDState);
    Serial.print(", Current=");
    Serial.println(currentLEDState);
    lastLoggedState = targetLEDState;
  }
  
  // NE METTRE À JOUR QUE SI L'ÉTAT CHANGE
  if (currentLEDState != targetLEDState) {
    Serial.print("[LED-CHANGE] ");
    Serial.print(currentLEDState);
    Serial.print(" -> ");
    Serial.println(targetLEDState);
    
    // Éteindre toutes les LEDs
    digitalWrite(GREEN_LED_PIN, LOW);
    digitalWrite(YELLOW_LED_PIN, LOW);
    digitalWrite(RED_LED_PIN, LOW);
    
    // Allumer la LED correcte
    if (targetLEDState == 1) {
      digitalWrite(GREEN_LED_PIN, HIGH);
    } 
    else if (targetLEDState == 2) {
      digitalWrite(YELLOW_LED_PIN, HIGH);
    } 
    else if (targetLEDState == 3) {
      digitalWrite(RED_LED_PIN, HIGH);
    }
    
    currentLEDState = targetLEDState;
  }
  
  // Gérer le buzzer de manière similaire (ne pas le toggler constamment)
  bool shouldBuzzer = (lastDetectionComplianceLevel < MEDIUM_COMPLIANCE_THRESHOLD);
  
  if (shouldBuzzer && !currentBuzzerActive) {
    // Démarrer le buzzer
    Serial.println("[BUZZER] ON");
    tone(BUZZER_PIN, 1500);
    currentBuzzerActive = true;
  } 
  else if (!shouldBuzzer && currentBuzzerActive) {
    // Arrêter le buzzer
    Serial.println("[BUZZER] OFF");
    noTone(BUZZER_PIN);
    currentBuzzerActive = false;
  }
}

/**
 * Set system status and control LEDs/buzzer
 * 
 * Status levels:
 * - ≥ 80%: Safe (GREEN LED only, no buzzer)
 * - 60-79%: Warning (YELLOW LED, no buzzer)
 * - < 60%: Danger (RED LED + buzzer)
 * 
 * NOTE: LEDs persist in this state until the next image detection update
 */
void setSystemStatus(int level, bool startup) {
  level = constrain(level, 0, 100);
  
  // Startup sequence - all LEDs pulse
  if (startup) {
    // Sequence: Green -> Yellow -> Red
    digitalWrite(GREEN_LED_PIN, HIGH);
    delay(200);
    digitalWrite(GREEN_LED_PIN, LOW);
    digitalWrite(YELLOW_LED_PIN, HIGH);
    delay(200);
    digitalWrite(YELLOW_LED_PIN, LOW);
    digitalWrite(RED_LED_PIN, HIGH);
    delay(200);
    digitalWrite(RED_LED_PIN, LOW);
    currentLEDState = -1;  // Reinit state tracker after startup
    return;
  }
  
  // Turn off all LEDs first
  digitalWrite(GREEN_LED_PIN, LOW);
  digitalWrite(YELLOW_LED_PIN, LOW);
  digitalWrite(RED_LED_PIN, LOW);
  noTone(BUZZER_PIN);
  currentBuzzerActive = false;
  
  String persistenceStatus = (lastDetectionComplianceLevel == level) ? " [PERSISTENT]" : "";
  
  // Determine new LED state
  int newLEDState;
  
  // Safety status - GREEN LED
  if (level >= HIGH_COMPLIANCE_THRESHOLD) {
    // ✅ SAFE - Green LED active
    digitalWrite(GREEN_LED_PIN, HIGH);
    newLEDState = 1;
    
    Serial.print("[STATUS] ✅ SAFE (Compliance: ");
    Serial.print(level);
    Serial.print("%) - LED: VERT");
    Serial.println(persistenceStatus);
  } 
  // Warning status - YELLOW LED
  else if (level >= MEDIUM_COMPLIANCE_THRESHOLD) {
    // ⚠️ WARNING - Yellow LED, no sound
    digitalWrite(YELLOW_LED_PIN, HIGH);
    newLEDState = 2;
    
    Serial.print("[STATUS] ⚠️ WARNING (Compliance: ");
    Serial.print(level);
    Serial.print("%) - LED: JAUNE");
    Serial.println(persistenceStatus);
  } 
  // Danger status - RED LED + buzzer
  else {
    // 🚨 DANGER - Red LED + beeping buzzer
    digitalWrite(RED_LED_PIN, HIGH);
    newLEDState = 3;
    tone(BUZZER_PIN, 1500, 500);
    currentBuzzerActive = true;
    
    Serial.print("[STATUS] 🚨 DANGER (Compliance: ");
    Serial.print(level);
    Serial.print("%) - LED: ROUGE + BUZZER");
    Serial.println(persistenceStatus);
  }
  
  // Update LED state tracker
  currentLEDState = newLEDState;
}
