/*
 * Script Arduino pour la simulation TinkerCad
 * Détection d'EPI avec capteurs virtuels
 */

// Définir les pins
const int IR_ENTRANCE_PIN = 2;    // Capteur IR d'entrée
const int IR_EXIT_PIN = 3;        // Capteur IR de sortie
const int LED_GREEN_PIN = 4;      // LED verte (conforme)
const int LED_RED_PIN = 5;        // LED rouge (non conforme)
const int BUZZER_PIN = 6;         // Buzzer d'alerte
const int BUTTON_PIN = 7;         // Bouton de test

// Variables d'état
int workersInArea = 0;
bool systemActive = true;
unsigned long lastDetectionTime = 0;
const unsigned long ALERT_DURATION = 5000; // 5 secondes

// Structure pour stocker l'état des travailleurs
struct Worker {
  int id;
  bool helmet;
  bool vest;
  bool glasses;
  bool compliant;
  unsigned long entryTime;
};

Worker workers[10]; // Maximum 10 travailleurs
int workerCount = 0;

void setup() {
  // Initialiser la communication série
  Serial.begin(9600);
  Serial.println("🚀 Système de détection EPI - Arduino");
  Serial.println("=====================================");
  
  // Configurer les pins
  pinMode(IR_ENTRANCE_PIN, INPUT);
  pinMode(IR_EXIT_PIN, INPUT);
  pinMode(LED_GREEN_PIN, OUTPUT);
  pinMode(LED_RED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  
  // Initialiser les LED
  digitalWrite(LED_GREEN_PIN, LOW);
  digitalWrite(LED_RED_PIN, LOW);
  noTone(BUZZER_PIN);
  
  // Message de démarrage
  Serial.println("✅ Système initialisé");
  Serial.println("📡 En attente de détections...");
  Serial.println();
}

void loop() {
  // Vérifier les capteurs IR
  checkIRSensors();
  
  // Vérifier le bouton de test
  if (digitalRead(BUTTON_PIN) == LOW) {
    testSystem();
    delay(500); // Anti-rebond
  }
  
  // Vérifier l'état de conformité
  checkCompliance();
  
  // Envoyer les données périodiquement
  static unsigned long lastSendTime = 0;
  if (millis() - lastSendTime > 1000) { // Toutes les secondes
    sendStatusData();
    lastSendTime = millis();
  }
  
  // Gestion des alertes prolongées
  manageAlerts();
  
  delay(100); // Petit délai pour stabilité
}

void checkIRSensors() {
  static bool lastEntranceState = LOW;
  static bool lastExitState = LOW;
  
  bool currentEntranceState = digitalRead(IR_ENTRANCE_PIN);
  bool currentExitState = digitalRead(IR_EXIT_PIN);
  
  // Détection d'entrée (front montant)
  if (currentEntranceState == HIGH && lastEntranceState == LOW) {
    workerEnters();
    lastDetectionTime = millis();
  }
  
  // Détection de sortie (front montant)
  if (currentExitState == HIGH && lastExitState == LOW) {
    workerExits();
    lastDetectionTime = millis();
  }
  
  lastEntranceState = currentEntranceState;
  lastExitState = currentExitState;
}

void workerEnters() {
  if (workerCount < 10) {
    // Créer un nouveau travailleur
    workers[workerCount].id = workerCount + 1;
    
    // Simuler aléatoirement le port des EPI
    workers[workerCount].helmet = random(0, 100) > 25;  // 75% de chance
    workers[workerCount].vest = random(0, 100) > 50;    // 50% de chance
    workers[workerCount].glasses = random(0, 100) > 75; // 25% de chance
    
    // Vérifier la conformité
    workers[workerCount].compliant = 
      workers[workerCount].helmet && 
      workers[workerCount].vest && 
      workers[workerCount].glasses;
    
    workers[workerCount].entryTime = millis();
    workerCount++;
    workersInArea++;
    
    Serial.print("👷 Travailleur #");
    Serial.print(workers[workerCount-1].id);
    Serial.println(" entré dans la zone");
    Serial.print("   Casque: ");
    Serial.println(workers[workerCount-1].helmet ? "✅ OUI" : "❌ NON");
    Serial.print("   Gilet: ");
    Serial.println(workers[workerCount-1].vest ? "✅ OUI" : "❌ NON");
    Serial.print("   Lunettes: ");
    Serial.println(workers[workerCount-1].glasses ? "✅ OUI" : "❌ NON");
    Serial.print("   Conforme: ");
    Serial.println(workers[workerCount-1].compliant ? "✅ OUI" : "❌ NON");
    Serial.println();
  }
}

void workerExits() {
  if (workerCount > 0) {
    // Retirer le dernier travailleur
    Serial.print("👋 Travailleur #");
    Serial.print(workers[workerCount-1].id);
    Serial.println(" sorti de la zone");
    
    // Calculer le temps passé
    unsigned long timeSpent = (millis() - workers[workerCount-1].entryTime) / 1000;
    Serial.print("   Temps passé: ");
    Serial.print(timeSpent);
    Serial.println(" secondes");
    Serial.println();
    
    workerCount--;
    workersInArea--;
  }
}

void checkCompliance() {
  // Calculer le taux de conformité
  int compliantCount = 0;
  
  for (int i = 0; i < workerCount; i++) {
    if (workers[i].compliant) {
      compliantCount++;
    }
  }
  
  int complianceRate = workerCount > 0 ? (compliantCount * 100) / workerCount : 100;
  
  // Contrôler les LED en fonction du taux de conformité
  if (workerCount == 0) {
    // Aucun travailleur: LEDs éteintes
    digitalWrite(LED_GREEN_PIN, LOW);
    digitalWrite(LED_RED_PIN, LOW);
    noTone(BUZZER_PIN);
  } else if (complianceRate >= 50) {
    // 50% ou plus de conformité: LED verte
    digitalWrite(LED_GREEN_PIN, HIGH);
    digitalWrite(LED_RED_PIN, LOW);
    noTone(BUZZER_PIN);
  } else {
    // Moins de 50% de conformité: LED rouge
    digitalWrite(LED_GREEN_PIN, LOW);
    digitalWrite(LED_RED_PIN, HIGH);
    
    // Activer le buzzer pour les non-conformités
    if (millis() % 1000 < 500) { // Bip bip
      tone(BUZZER_PIN, 1000);
    } else {
      noTone(BUZZER_PIN);
    }
  }
}

void sendStatusData() {
  // Calculer les statistiques
  int compliantCount = 0;
  int helmetCount = 0;
  int vestCount = 0;
  int glassesCount = 0;
  
  for (int i = 0; i < workerCount; i++) {
    if (workers[i].compliant) compliantCount++;
    if (workers[i].helmet) helmetCount++;
    if (workers[i].vest) vestCount++;
    if (workers[i].glasses) glassesCount++;
  }
  
  int complianceRate = workerCount > 0 ? (compliantCount * 100) / workerCount : 100;
  
  // Envoyer les données au format JSON
  Serial.print("{");
  Serial.print("\"workers\": ");
  Serial.print(workerCount);
  Serial.print(", \"compliant\": ");
  Serial.print(compliantCount);
  Serial.print(", \"compliance_rate\": ");
  Serial.print(complianceRate);
  Serial.print(", \"helmets\": ");
  Serial.print(helmetCount);
  Serial.print(", \"vests\": ");
  Serial.print(vestCount);
  Serial.print(", \"glasses\": ");
  Serial.print(glassesCount);
  Serial.print(", \"timestamp\": ");
  Serial.print(millis());
  Serial.print(", \"system_active\": ");
  Serial.print(systemActive ? "true" : "false");
  Serial.println("}");
}

void testSystem() {
  Serial.println("🔧 TEST DU SYSTÈME EN COURS...");
  
  // Test des LED
  Serial.println("💡 Test des LED...");
  digitalWrite(LED_GREEN_PIN, HIGH);
  delay(500);
  digitalWrite(LED_GREEN_PIN, LOW);
  digitalWrite(LED_RED_PIN, HIGH);
  delay(500);
  digitalWrite(LED_RED_PIN, LOW);
  
  // Test du buzzer
  Serial.println("🔊 Test du buzzer...");
  for (int i = 0; i < 3; i++) {
    tone(BUZZER_PIN, 1000 + i * 500, 200);
    delay(300);
  }
  noTone(BUZZER_PIN);
  
  // Simulation de travailleurs
  Serial.println("👷 Simulation de travailleurs...");
  workerEnters();
  delay(1000);
  workerExits();
  
  Serial.println("✅ Test terminé");
  Serial.println();
}

void manageAlerts() {
  // Désactiver le système si aucune détection depuis longtemps
  if (workersInArea == 0 && millis() - lastDetectionTime > 300000) { // 5 minutes
    if (systemActive) {
      systemActive = false;
      Serial.println("💤 Système en veille");
      
      // Éteindre tout
      digitalWrite(LED_GREEN_PIN, LOW);
      digitalWrite(LED_RED_PIN, LOW);
      noTone(BUZZER_PIN);
    }
  } else {
    if (!systemActive) {
      systemActive = true;
      Serial.println("🔄 Système réactivé");
    }
  }
}
