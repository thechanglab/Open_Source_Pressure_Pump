// Define the command variables
char cmd = "";
String cmdline = "";
String cmd1 = "";
int cmdvalve;
String cmd2 = "";

// Define the valve variables for the control loop
# define VALVE 4 // Number of valves
double SetPoint[VALVE] = {0, 0, 0, 0}; // Setpoints set to zero at start
double MeasuredPoint[VALVE];
int wait = 1; // Predefined wait value

int outlets[] = {2, 4, 6, 8}; // Digitial pins for the S_out valves
int inlets[] = {3, 5, 7, 9}; // Digitial pins for the S_in valves
int sensors[] = {A0, A1, A2, A3}; // Analog pins for the sensors

// AnalogWrite range for the solenoid valves
int minin[] = {0, 0, 0, 0};
int minout[] = {0, 0, 0, 0};
int maxin[] = {255, 255, 255, 255};
int maxout[] = {255, 255, 255, 255};

// Initial AnalogWrite Values and how much to change them per loop
int DCin[]  = {0, 0, 0, 0};
int DCout[] = {0, 0, 0, 0};
int increment = 1;
int decrement = -1;

// Measurement variables to transform voltages to pressure values
int aread;
double voltage;
int Pmin = 0;
int Pmax = 15;
int Vs = 5;
double P_up;
unsigned long t;

// Output Variables
String Output;
String Number;
String MeaPnt;
String StPnt;
String elapsedtime;

// Setup loop
void setup() {
  Serial.begin(9600); // Preset Baudrate

  // Set the pins for the valves
  for (int i = 0; i < VALVE; i++) {
    pinMode(inlets[i],OUTPUT);
    pinMode(outlets[i],OUTPUT);
  }

  // Set the pins for the sensors
  for (int i = 0; i < VALVE; i++) {
    analogWrite(inlets[i],minin[i]);
    analogWrite(outlets[i],minout[i]);
  }

  // Wait for 10ms and then send the "Ready" message
  delay(wait*10);
  Serial.println("Ready");
}

void loop() {
  
  // Grab Set Points when a mesaage is sent
  // Input format is a string "N,SP"
  if (Serial.available() > 0) {
    cmd = Serial.read();
    cmdline += (String)cmd;

    // Convert to command lines
    if (cmd == '\n') {
      int N = cmdline.length();
      // Valve Number
      cmd1 = cmdline.substring(0,1);
      // Set Point
      cmd2 = cmdline.substring(2,N);
      // Change the set point array based on the input
      cmdvalve = cmd1.toInt();
      SetPoint[cmdvalve] =  cmd2.toDouble();
      // Clear the incoming message
      cmdline = "";
    }
  }

  // Control loop
  for (int i = 0; i < 1; i++) {

    // If setpoint is 0, then full valve shut off
    if (SetPoint[i] <= 0) {
      analogWrite(outlets[i],255);
      analogWrite(inlets[i],0);
    }
    else {
      // Calculate measured pressures
      aread = (analogRead(sensors[i]));
      voltage = aread*(5.0/1023.0);
      MeasuredPoint[i] = (voltage-0.1*Vs)*(Pmax - Pmin)/(0.8*Vs) + Pmin;
  
      t = millis();
      
      // ON/OFF control
      // Inlet Control
      if (MeasuredPoint[i] < SetPoint[i]) {
        DCin[i] = updateDC(DCin[i], increment, minin[i], maxin[i]);
        DCout[i] = updateDC(DCout[i], decrement, minout[i], maxout[i]);
        analogWrite(inlets[i],DCin[i]);
        analogWrite(outlets[i],DCout[i]);
      }
      // Outlet Control
      else if (MeasuredPoint[i] > SetPoint[i]) {
        DCin[i] = updateDC(DCin[i], decrement, minin[i], maxin[i]);
        DCout[i] = updateDC(DCout[i], increment, minout[i], maxout[i]);
        analogWrite(inlets[i],DCin[i]);
        analogWrite(outlets[i],DCout[i]);
      }
      else {
        // No change
        analogWrite(inlets[i],DCin[i]);
        analogWrite(outlets[i],DCout[i]);
      }
    }

    // Send the updated values over the serial port if a valves setpoint is not zero
    if (SetPoint[i] != 0) {
      Number = String(i);
      StPnt = String(SetPoint[i],3);
      MeaPnt = String(MeasuredPoint[i],3);
      elapsedtime = String(t);
      // Output is N,SP,MP,time,DCin,DCout
      Output = Number + "," + StPnt + "," + MeaPnt + "," + elapsedtime + "," + String(DCin[i]) + "," + String(DCout[i]);
      Serial.println(Output);
    }

    delay(wait);
  }
  delay(wait);
}

// Function to update the DC of each valve and keep it in the range
int updateDC (int DC, int k, int minimum, int maximum) {
  // DC is the duty cycle indexed from the array
  // k is the increment or decrement
  // minimum and maximum are the indexed values from their arrays
  DC = DC + k;
  if (DC > maximum) {
    DC = maximum;
  }
  else if (DC < minimum) {
    DC = minimum;
  }
  else {
    DC = DC;
  }
  return DC;
}
