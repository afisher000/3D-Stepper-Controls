//int z_step = 6; // arduino pin
//int z_dir = 7; // arduino pin

// Define variables
String input;
float steps;
int step_pins[] = {5, 3, 7}; //pins to control steps of x, y, z motors
int dir_pins[] = {4, 2, 6}; //pins to control direction of x, y, z motors
int motor; //0=x motor, 1=y motor, 2=z motor
int dir; // Determined from sign of steps

// Define functions
void parseInput();
void moveStepper();
void clearSerial();

// Runs once at start
void setup() {
  // Open serial connection
  Serial.begin(9600);

  // Set pins 2-7 to OUTPUT mode and low voltage
  for(int pin = 2; pin<8; pin++){
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
  }

  clearSerial();
}

// Looped function
void loop() {
  // Read when serial data available
  if (Serial.available()>0){
    input = Serial.readString();
    parseInput();
    moveStepper();
  }
}

void parseInput(){
  int input_length = input.length()+1;
  char input_array[input_length];
  input.toCharArray(input_array, input_length);
  
  char* token = strtok(input_array, " ,"); //Read motor number (0-2)
  motor = atoi(token);
  //Serial.println("Read motor");
  //Serial.println(motor);

  token = strtok(NULL, " ,"); //Read number of steps
  steps = atof(token);
  //Serial.println("Read steps");
  //Serial.println(steps); 
  
  // Clear any remaining data from serial
  clearSerial();
}


void clearSerial() {
  while (Serial.available()>0){
    Serial.read();
  }
}

void moveStepper(){

  // Set direction
  if (steps<0){
    digitalWrite(dir_pins[motor], LOW);
  }
  else {
    digitalWrite(dir_pins[motor], HIGH);
  }
  
  //Serial.println("Moving");
  for (long x = 0; x<abs(steps); x++){
    digitalWrite(step_pins[motor], HIGH);
    delay(1);
    digitalWrite(step_pins[motor], LOW);
    delay(1);
  }

  Serial.print("success\n");
}
