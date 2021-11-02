/*
  Blink

  Turns an LED on for one second, then off for one second, repeatedly.

  Most Arduinos have an on-board LED you can control. On the UNO, MEGA and ZERO
  it is attached to digital pin 13, on MKR1000 on pin 6. LED_BUILTIN is set to
  the correct LED pin independent of which board is used.
  If you want to know what pin the on-board LED is connected to on your Arduino
  model, check the Technical Specs of your board at:
  https://www.arduino.cc/en/Main/Products

  modified 8 May 2014
  by Scott Fitzgerald
  modified 2 Sep 2016
  by Arturo Guadalupi
  modified 8 Sep 2016
  by Colby Newman

  This example code is in the public domain.

  http://www.arduino.cc/en/Tutorial/Blink
*/
int homepos = 1;
int estop = 1; //normally open for some reason

// the setup function runs once when you press reset or power the board
void setup() {
  Serial.begin(9600);
  pinMode(7, OUTPUT);
  pinMode(8, INPUT);
  pinMode(3, INPUT);
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
