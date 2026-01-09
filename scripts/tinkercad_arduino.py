// Simulation Arduino pour TinkerCad

int pirSensor = 2;      // Capteur de mouvement (entrée digitale)
int redLED = 3;         // LED Rouge pour danger
int greenLED = 4;       // LED Verte pour sécurité
int buzzer = 5;         // Buzzer pour alerte
int complianceLevel = 0; // Niveau de conformité (0-100)

void setup() {
  Serial.begin(9600);
  pinMode(pirSensor, INPUT);
  pinMode(redLED, OUTPUT);
  pinMode(greenLED, OUTPUT);
  pinMode(buzzer, OUTPUT);
  
  Serial.println("Système de détection EPI - Simulation TinkerCad");
  Serial.println("==============================================");
}

void loop() {
  // Simuler la détection de mouvement
  int motionDetected = digitalRead(pirSensor);
  
  if (motionDetected == HIGH) {
    Serial.println("Mouvement détecté! Vérification des EPI...");
    
    // Simulation de la détection EPI
    complianceLevel = random(0, 101); // Simulation aléatoire
    
    if (complianceLevel >= 80) {
      // Conformité OK
      digitalWrite(greenLED, HIGH);
      digitalWrite(redLED, LOW);
      noTone(buzzer);
      Serial.print("Conformité: ");
      Serial.print(complianceLevel);
      Serial.println("% - ZONE SÉCURISÉE");
    } 
    else if (complianceLevel >= 50) {
      // Avertissement
      digitalWrite(greenLED, LOW);
      digitalWrite(redLED, HIGH);
      tone(buzzer, 1000, 500);
      Serial.print("Conformité: ");
      Serial.print(complianceLevel);
      Serial.println("% - ATTENTION!");
    } 
    else {
      // Danger
      digitalWrite(greenLED, LOW);
      digitalWrite(redLED, HIGH);
      tone(buzzer, 2000, 1000);
      Serial.print("Conformité: ");
      Serial.print(complianceLevel);
      Serial.println("% - DANGER! EPI Manquants");
    }
    
    // Envoyer les données à l'API (simulation)
    sendToAPI(complianceLevel);
    
    delay(3000); // Attendre 3 secondes
  } 
  else {
    digitalWrite(greenLED, LOW);
    digitalWrite(redLED, LOW);
    noTone(buzzer);
  }
  
  delay(1000); // Vérifier chaque seconde
}

void sendToAPI(int compliance) {
  // Simulation d'envoi à l'API Flask
  Serial.print("Envoi des données à l'API: compliance=");
  Serial.println(compliance);
  
  // Format JSON simulé
  Serial.print("{");
  Serial.print("\"sensor_id\": \"tinkercad_01\",");
  Serial.print("\"compliance\": ");
  Serial.print(compliance);
  Serial.print(",");
  Serial.print("\"timestamp\": \"");
  Serial.print(millis());
  Serial.println("\"}");
}