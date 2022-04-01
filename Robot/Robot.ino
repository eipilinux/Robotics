int homepos = 1;

void setup() {
  Serial.begin(9600);
  /*
   * pin 7 ---> Tester 1 Pass
   * pin 6 ---> Tester 
   * pin 5 ---> Tester 
   * pin 4 ---> Tester 
   * pin 3 ---> Tester 
   * pin 2 ---> Tester 
   * pin 9 ---> Welder Home Button
   * pin 8 ---> Welder Start (HIGH signal starts welder, This pin needs to be set HIGH for at least 0.500 seconds to activate welder)
   */
}

// the loop function runs over and over again forever
void loop() {
  if(digitalRead(8) == HIGH && homepos == 0){
    Serial.println("Home");
    homepos = 1;
    delay(20);
  }
  if(digitalRead(8) == LOW && homepos == 1){
    homepos = 0;
    delay(20);
  }

//new section
  if(digitalRead(3) == LOW && estop == 1){
    Serial.println("estop");
    estop = 0;
    delay(20);
  }
  if(digitalRead(3) == HIGH && estop == 0){
    Serial.println("resume");
    estop = 1;
    delay(20);
  }
//
 
  if (Serial.available() > 0) {
    // read the incoming byte:
    byte incomingByte = Serial.read();
    if(incomingByte == 49){
      digitalWrite(7, HIGH);
      //Serial.println("Received");
      delay(1000);
      digitalWrite(7, LOW);
    }
  }
}






//data transfer variables
int incomingByte = 0; // for incoming serial data

//solo unit 1 (leak decay)
const int solo_1_end = 10;
const int solo_1_fail = 12;
const int solo_1_pass = 11;
const int solo_1_start = 2;
int SOLO_1_READY; // is HIGH if the system is ready for a new part and LOW while testing
int SOLO_1_STATE; // holds a PASS or FAIL value

//solo unit 2 (leak decay)
const int solo_2_end = A4;
const int solo_2_fail = A2;
const int solo_2_pass = A3;
const int solo_2_start = 3;
int SOLO_2_READY = 0; // is HIGH if the system is ready for a new part and LOW while testing
int SOLO_2_STATE = 0; // holds a PASS or FAIL value

const int table_home = A5;
int TABLE_STATE;



void setup() {
  // initialize the solo test start pins as outputs:
  pinMode(solo_1_start, OUTPUT);
  pinMode(solo_2_start, OUTPUT);
  pinMode(solo_3_start, OUTPUT);
  
  // initialize the solo tester pins as input:
  pinMode(solo_1_end, INPUT);
  pinMode(solo_1_fail, INPUT);
  pinMode(solo_1_pass, INPUT);
  //solo 2
  pinMode(solo_2_end, INPUT);
  pinMode(solo_2_fail, INPUT);
  pinMode(solo_2_pass, INPUT);
  //solo 3
  pinMode(solo_3_end, INPUT);
  pinMode(solo_3_fail, INPUT);
  pinMode(solo_3_pass, INPUT);
  //table home
  pinMode(table_home, INPUT);

  // opens serial port, sets data rate to 9600 bps
  Serial.begin(9600); 

  //do the initail check of the input pins for solo 1
  if(digitalRead(solo_1_fail) == HIGH){
    SOLO_1_STATE = 0;
    Serial.println("Fail");
  }
  else if(digitalRead(solo_1_pass) == HIGH){
    SOLO_1_STATE = 1;
    Serial.println("Pass");
  }
  if(digitalRead(solo_1_end) == HIGH){
    SOLO_1_READY = 1;
    //Serial.println("1 is ready");
  }
  else{
    SOLO_1_READY = 0;
    //Serial.println("1 is active");
  }

  //do the initail check of the input pins for solo 2
  if(digitalRead(solo_2_fail) == HIGH){
    SOLO_2_STATE = 0;
    Serial.println("Fail");
  }
  else if(digitalRead(solo_2_pass) == HIGH){
    SOLO_2_STATE = 1;
    Serial.println("Pass");
  }
  if(digitalRead(solo_2_end) == HIGH){
    SOLO_2_READY = 1;
    //Serial.println("2 is ready");
  }
  else{
    SOLO_2_READY = 0;
    //Serial.println("2 is active");
  }

  //do the initail check of the input pins for solo 3
  if(digitalRead(solo_3_fail) == HIGH){
    SOLO_3_STATE = 0;
    Serial.println("Fail");
  }
  else if(digitalRead(solo_3_pass) == HIGH){
    SOLO_3_STATE = 1;
    Serial.println("Pass");
  }
  if(digitalRead(solo_3_end) == HIGH){
    SOLO_3_READY = 1;
    //Serial.println("3 is ready");
  }
  else{
    SOLO_3_READY = 0;
    //Serial.println("3 is active");
  }

  //do the initial check of table position
  if(digitalRead(table_home) == HIGH){
    TABLE_STATE = 1;
    Serial.println("Table Home");
  }
  else{
    TABLE_STATE = 0;
    Serial.println("Table Moving");
  }

  //end of setup()
}

void loop() {
  //check the input pins for solo tester 1
  if( SOLO_1_READY == 0 && digitalRead(solo_1_end) == HIGH){
      if(digitalRead(solo_1_fail) == HIGH || digitalRead(solo_1_pass) == LOW)
        Serial.println("1 Fail");
      else if(digitalRead(solo_1_pass) == HIGH)
        Serial.println("1 Pass");
      //Serial.println("1 is ready");
      SOLO_1_READY = 1;
  }
  else if( SOLO_1_READY == 1 && digitalRead(solo_1_end) == LOW){
    //Serial.println("1 is active");
    SOLO_1_READY = 0;
  }

  //
  //
  //
  
  //check the input pins for solo tester 2
  if( SOLO_2_READY == 0 && digitalRead(solo_2_end) == HIGH){
      if(digitalRead(solo_2_fail) == HIGH || digitalRead(solo_2_pass) == LOW)
        Serial.println("2 Fail");
      else if(digitalRead(solo_2_pass) == HIGH)
        Serial.println("2 Pass");
      //Serial.println("2 is ready");
      SOLO_2_READY = 1;
  }
  else if( SOLO_2_READY == 1 && digitalRead(solo_2_end) == LOW){
    //Serial.println("2 is active");
    SOLO_2_READY = 0;
  }

  //
  //
  //
  
  //check the input pins for solo tester 3
  if( SOLO_3_READY == 0 && digitalRead(solo_3_end) == HIGH){
      if(digitalRead(solo_3_fail) == HIGH || digitalRead(solo_3_pass) == LOW)
        Serial.println("3 Fail");
      else if(digitalRead(solo_3_pass) == HIGH)
        Serial.println("3 Pass");
      //Serial.println("3 is ready");
      SOLO_3_READY = 1;
  }
  else if( SOLO_3_READY == 1 && digitalRead(solo_3_end) == LOW){
    //Serial.println("3 is active");
    SOLO_3_READY = 0;
  }

  //check the table position
  if(TABLE_STATE == 0 && digitalRead(table_home) == HIGH){
    TABLE_STATE = 1;
    Serial.println("Table Home");
  }
  else if(TABLE_STATE == 1 && digitalRead(table_home) == LOW){
    TABLE_STATE = 0;
    Serial.println("Table Moving");
  }

  //deal with incoming commands
  if (Serial.available() > 0) {
    // read the incoming byte:
    incomingByte = Serial.read();

    //start tester 1
    if(incomingByte == 49){
      digitalWrite(solo_1_start, HIGH);
      //Serial.println("Received");
      delay(20);
      digitalWrite(solo_1_start, LOW);
    }

    //start tester 2
    if(incomingByte == 50){
      digitalWrite(solo_2_start, HIGH);
      //Serial.println("Received");
      delay(20);
      digitalWrite(solo_2_start, LOW);
    }

    //start tester 3
    if(incomingByte == 51){
      digitalWrite(solo_3_start, HIGH);
      //Serial.println("Received");
      delay(20);
      digitalWrite(solo_3_start, LOW);
    }
  }
  
  delay(1);
}
