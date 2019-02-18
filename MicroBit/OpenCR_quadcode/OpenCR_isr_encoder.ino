/*
 * OpenCR motor decoder by ISR
 * features:
 *  
 *  
 * test case: micro:bit
 * Usage:
 *    A - microbit(P0) - EXTI_0( 0: Arduino PIN 2,   EXTI_0)
 *    B - microbit(P1) - EXTI_1( 0: Arduino PIN 3,   EXTI_1)
 *    Clear - microbit(P2) - EXTI_2( 0: Arduino PIN 4,   EXTI_2)
 *    Arduino PIN 4 + Ground -> reset counter
 * Default output:
 *  isr0_cnt,isr1_cnt,encoder0Pos
 * LICENSE: MIT
 * Author: WuLung Hsu, wuulong@gmail.com
 *  doc: https://paper.dropbox.com/doc/MbitBot--AXygciMpkj~Tsk6AdFTEKGtsAg-DG5SSj5zQhBv1CoAgDtAG#:uid=925566654150854768396062&h2=Encoder-tool  
 */


long isr0_cnt = 0;
long isr1_cnt = 0;
volatile long encoder0Pos = 0;
#define encoder0PinA  2
#define encoder0PinB  3
#define clearPinC  4
void setup(){
  Serial.begin(115200);

  pinMode(9, OUTPUT);

  pinMode(encoder0PinA, INPUT_PULLDOWN);
  pinMode(encoder0PinB, INPUT_PULLDOWN);
  pinMode(clearPinC, INPUT_PULLDOWN);


  /*It can be choose as CHANGE, RISING or FALLING*/
  attachInterrupt(0, doEncoderA, CHANGE);
  attachInterrupt(1, doEncoderB, CHANGE);
  attachInterrupt(2, doClear, RISING);
  
}

void doClear(void){
  isr0_cnt=0;
  isr1_cnt=0;
  encoder0Pos=0;
}

void doEncoderA(void){
  //Serial.print("0");
  isr0_cnt ++;
  
  // look for a low-to-high on channel A
  if (digitalRead(encoder0PinA) == HIGH) {

    // check channel B to see which way encoder is turning
    if (digitalRead(encoder0PinB) == LOW) {
      encoder0Pos = encoder0Pos + 1;         // CW
    }
    else {
      encoder0Pos = encoder0Pos - 1;         // CCW
    }
    
  }

  else   // must be a high-to-low edge on channel A
  {
    // check channel B to see which way encoder is turning
    if (digitalRead(encoder0PinB) == HIGH) {
      encoder0Pos = encoder0Pos + 1;          // CW
    }
    else {
      encoder0Pos = encoder0Pos - 1;          // CCW
    }
  }
}

void doEncoderB(void){
  isr1_cnt ++;
  
  // look for a low-to-high on channel B
  if (digitalRead(encoder0PinB) == HIGH) {

    // check channel A to see which way encoder is turning
    if (digitalRead(encoder0PinA) == HIGH) {
      encoder0Pos = encoder0Pos + 1;         // CW
    }
    else {
      encoder0Pos = encoder0Pos - 1;         // CCW
    }
  }

  // Look for a high-to-low on channel B

  else {
    // check channel B to see which way encoder is turning
    if (digitalRead(encoder0PinA) == LOW) {
      encoder0Pos = encoder0Pos + 1;          // CW
    }
    else {
      encoder0Pos = encoder0Pos - 1;          // CCW
    }
  }
  
}

void loop(){
  Serial.println("");
  Serial.print(isr0_cnt);
  Serial.print(" ");
  Serial.print(isr1_cnt);
  Serial.print(" ");
  Serial.print(encoder0Pos);
  delay(1000);
}
