const int solo_end = 5;
const int solo_fail = 6;
const int solo_pass = 7;
const int solo_start = 8;
const int alarm = 4;

int SOLO_READY; // is HIGH if the system is ready for a new part and LOW while testing
int SOLO_STATE; // holds a PASS or FAIL value
 
// Pin to connect to your conductive sensor 
// (paperclip, conductive paint/fabric/thread, wire)
int capSensePin = 2;

// This is how high the sensor needs to read in order
//  to trigger a touch.  You'll find this number
//  by trial and error, or you could take readings at 
//  the start of the program to dynamically calculate this.
// If this is not sensitive enough, try a resistor with more ohms.
int touchedCutoff = 90;

void setup(){
  Serial.begin(9600);

  pinMode(solo_start, OUTPUT);
  pinMode(alarm, OUTPUT);
  pinMode(solo_end, INPUT);
  pinMode(solo_fail, INPUT);
  pinMode(solo_pass, INPUT);
 

    //do the initail check of the input pins for solo tester
  if(digitalRead(solo_fail) == LOW){
    SOLO_STATE = 0;
    digitalWrite(alarm, HIGH);
    delay(500);
    digitalWrite(alarm, LOW);
  }
  else if(digitalRead(solo_pass) == LOW){
    SOLO_STATE = 1;
    Serial.println("Pass");
  }
  if(digitalRead(solo_end) == LOW){
    SOLO_READY = 1;
    Serial.println("ready");
  }
  else{
    SOLO_READY = 0;
    Serial.println("active");
  }
}

void loop(){
  //Serial.print("Capacitive Sensor reads: ");
  //Serial.println(readCapacitivePin(capSensePin));
  //Serial.println(digitalRead(solo_end));
  //Serial.println(digitalRead(solo_pass));
  //Serial.println(digitalRead(solo_fail));
  delay(100);
  if( SOLO_READY == 0 && digitalRead(solo_end) == LOW){
      if(digitalRead(solo_fail) == LOW || digitalRead(solo_pass) == HIGH){
        Serial.println("Fail");
        digitalWrite(alarm, HIGH);
        delay(500);
        digitalWrite(alarm, LOW);
      }
      else if(digitalRead(solo_pass) == LOW)
        Serial.println("Pass");
      Serial.println("ready");
      SOLO_READY = 1;
  }
  else if( SOLO_READY == 1 && digitalRead(solo_end) == HIGH){
    Serial.println("active");
    SOLO_READY = 0;
  }
    
  if (readCapacitivePin(capSensePin) > touchedCutoff && SOLO_READY == 1) {
    digitalWrite(solo_start, HIGH);
    delay(50);
    digitalWrite(solo_start, LOW);
    Serial.print("Capacitive Sensor reads: ");
    Serial.println(readCapacitivePin(capSensePin));
  }
  
  
  //else {
    //digitalWrite(LEDPin, LOW);
  //}
  
  // Every 500 ms, print the value of the capacitive sensor
  //if ( (millis() % 500) == 0){
    //Serial.print("Capacitive Sensor reads: ");
    //Serial.println(readCapacitivePin(capSensePin));
  //}
  //delay(20);
}

// readCapacitivePin
//  Input: Arduino pin number
//  Output: A number, from 0 to 17 expressing
//          how much capacitance is on the pin
//  When you touch the pin, or whatever you have
//  attached to it, the number will get higher
//  In order for this to work now,
// The pin should have a resistor pulling
//  it up to +5v.
uint8_t readCapacitivePin(int pinToMeasure){
  // This is how you declare a variable which
  //  will hold the PORT, PIN, and DDR registers
  //  on an AVR
  volatile uint8_t* port;
  volatile uint8_t* ddr;
  volatile uint8_t* pin;
  // Here we translate the input pin number from
  //  Arduino pin number to the AVR PORT, PIN, DDR,
  //  and which bit of those registers we care about.
  byte bitmask;
  if ((pinToMeasure >= 0) && (pinToMeasure <= 7)){
    port = &PORTD;
    ddr = &DDRD;
    bitmask = 1 << pinToMeasure;
    pin = &PIND;
  }
  if ((pinToMeasure > 7) && (pinToMeasure <= 13)){
    port = &PORTB;
    ddr = &DDRB;
    bitmask = 1 << (pinToMeasure - 8);
    pin = &PINB;
  }
  if ((pinToMeasure > 13) && (pinToMeasure <= 19)){
    port = &PORTC;
    ddr = &DDRC;
    bitmask = 1 << (pinToMeasure - 13);
    pin = &PINC;
  }
  // Discharge the pin first by setting it low and output
  *port &= ~(bitmask);
  *ddr  |= bitmask;
  delay(1);
  // Make the pin an input WITHOUT the internal pull-up on
  *ddr &= ~(bitmask);
  // Now see how long the pin to get pulled up
  int cycles = 16000;
  for(int i = 0; i < cycles; i++){
    if (*pin & bitmask){
      cycles = i;
      break;
    }
  }
  // Discharge the pin again by setting it low and output
  //  It's important to leave the pins low if you want to 
  //  be able to touch more than 1 sensor at a time - if
  //  the sensor is left pulled high, when you touch
  //  two sensors, your body will transfer the charge between
  //  sensors.
  *port &= ~(bitmask);
  *ddr  |= bitmask;
  
  return cycles;
}
