/*
* 
* pin 7 ---> Tester 1 Pass (Pin is an input pin that will go LOW when tester 1 cycle passes)
* pin 6 ---> Tester 1 Cycle End (Pin is an input pin that will go LOW when tester 1 cycle ends)
* 
* pin 5 ---> Tester 2 Pass (Pin is an input pin that will go LOW when tester 2 cycle passes)
* pin 4 ---> Tester 2 Cycle End (Pin is an input pin that will go LOW when tester 2 cycle ends)
* 
* pin 2 ---> Tester 1 Start (HIGH signal starts tester 1, This pin needs to be set HIGH for at least 0.020 seconds to activate tester)
* pin 3 ---> Tester 2 Start (HIGH signal starts tester 2, This pin needs to be set HIGH for at least 0.020 seconds to activate tester)
* 
* pin 9 ---> Welder Home Switch (This pin is the signal wire from a limit switch and will go HIGH when the welder is in the home position and LOW when the welder is welding)
* pin 8 ---> Welder Start (This pin is normally set LOW and a HIGH signal starts the welder, This pin needs to be set HIGH for at least 0.700 seconds to activate welder)
* 
* ASCII digit 1 ---> BYTE value of 49 (this is what the Raspi will send over the serial comm to start tester 1)
* ASCII digit 2 ---> BYTE value of 50 (this is what the Raspi will send over the serial comm to start tester 2)
* ASCII Capital 'W' ---> BYTE value of 87 (this is what the Raspi will send over the serial comm to start the welder)
* 
*/

//can be LOW (0) for welder home, or HIGH (1) for welder active
int WELDER_STATE = 0;

//welder
const int welder_start = 8;
const int welder_home = 9;

//solo unit 1 (leak decay)
const int solo_1_end = 6;
const int solo_1_pass = 7;
const int solo_1_start = 2;
int SOLO_1_READY = 0; // is HIGH (1) if the system is ready for a new part and LOW (0) while testing
int SOLO_1_STATE = 0; // holds a PASS (1) or FAIL (0) value

//solo unit 2 (leak decay)
const int solo_2_end = 4;
const int solo_2_pass = 5;
const int solo_2_start = 3;
int SOLO_2_READY = 0; // is HIGH (1) if the system is ready for a new part and LOW (0) while testing
int SOLO_2_STATE = 0; // holds a PASS (1) or FAIL (0) value

//alarm
bool alarm_on = false;
const int alarm_pin = 13;

void setup() {
  /*
   * We don't need crazy high baud rates because we will never be trying to time stuff to within 1/10,000th of a second 
   * and so 9600 will be fine and will reduce the chances of transmission errors
   */
  Serial.begin(9600);
  
  pinMode(solo_1_start, OUTPUT);
  pinMode(solo_2_start, OUTPUT);
  pinMode(welder_start, OUTPUT);

  pinMode(solo_1_end, INPUT);
  pinMode(solo_1_pass, INPUT);
  
  pinMode(solo_2_end, INPUT);
  pinMode(solo_2_pass, INPUT);

  pinMode(welder_home, INPUT);

  int SOLO_1_READY = 1; 
  int SOLO_2_READY = 1; 
//  Serial.println("initializing...");
//  delay(5000);
//  Serial.println("System Ready");
//  Serial.println(digitalRead(solo_1_pass));
//  Serial.println(digitalRead(solo_2_pass));
//  Serial.println(digitalRead(solo_1_end));
//  Serial.println(digitalRead(solo_2_end));
} //end of void setup{}

void loop() {

  //check the welder state
  if(digitalRead(welder_home) == HIGH && WELDER_STATE == 1){
    Serial.println("Welder Home");
    WELDER_STATE = 0;
    delay(20);
  }
  if(digitalRead(welder_home) == LOW && WELDER_STATE == 0){
    Serial.println("Welder Active");
    WELDER_STATE = 1;
    delay(20);
  }

  //check solo tester 1
  if( SOLO_1_READY == 0 && digitalRead(solo_1_end) == LOW){
    if(digitalRead(solo_1_pass) == HIGH)
      Serial.println("1 Fail");
    else if(digitalRead(solo_1_pass) == LOW)
      Serial.println("1 Pass");
    SOLO_1_READY = 1;
  }
  else if( SOLO_1_READY == 1 && digitalRead(solo_1_end) == HIGH){
    SOLO_1_READY = 0;
  }

  //check solo tester 2
  if( SOLO_2_READY == 0 && digitalRead(solo_2_end) == LOW){
    if(digitalRead(solo_2_pass) == HIGH)
      Serial.println("2 Fail");
    else if(digitalRead(solo_2_pass) == LOW)
      Serial.println("2 Pass");
    SOLO_2_READY = 1;
  }
  else if( SOLO_2_READY == 1 && digitalRead(solo_2_end) == HIGH){
    SOLO_2_READY = 0;
  }
  
  //check the serial com
  if (Serial.available() > 0) {
    // read the incoming byte:
    byte incomingByte = Serial.read();

    //if the control computer sent 'W' (byte value of 87) then start the welder
    if(incomingByte == 87){
      digitalWrite(welder_start, HIGH);
      Serial.println("Welder Active");
      WELDER_STATE = 1;
      delay(1000);
      digitalWrite(welder_start, LOW);
    }

    //if the control computer sent 'A' (byte value of 65) then start/stop the alarm
    if(incomingByte == 65){
      if(alarm_on){
        digitalWrite(alarm_pin, LOW);
        alarm_on = false;
      }
      else{
        digitalWrite(alarm_pin, HIGH);
        alarm_on = true;
      }
    }

    //if the control computer sent '1' (byte value of 49) then start tester 1
    else if(incomingByte == 49){
      digitalWrite(solo_1_start, HIGH);
      Serial.println("Started Tester 1");
      delay(20);
      digitalWrite(solo_1_start, LOW);
      //SOLO_1_READY = 0;
    }

    //if the control computer sent '2' (byte value of 50) then start tester 2
    else if(incomingByte == 50){
      digitalWrite(solo_2_start, HIGH);
      Serial.println("Started Tester 2");
      delay(20);
      digitalWrite(solo_2_start, LOW);
      //SOLO_2_READY = 0;
    }
  } //end of serial.available{}
} //end of void loop{}
