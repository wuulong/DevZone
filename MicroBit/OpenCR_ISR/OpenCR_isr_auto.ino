

/*
 * OpenCR ISR performance test sample
 * features:
 *  use user-defined waveform to test controller ISR performance
 *  
 * test case: micro:bit
 * Usage:
 *    FS - microbit(P0) - EXTI_0( 0: Arduino PIN 2,   EXTI_0)
 *    PASS - microbit(P1) - EXTI_1( 0: Arduino PIN 3,   EXTI_1)
 *    INT - microbit(P2) - EXTI_2( 0: Arduino PIN 4,   EXTI_2)
 * Default output:
 *  sprintf(str_buf,"%i %i %i %lu", state,isr_cnt, loop_cnt,debug_cnt);
 * LICENSE: MIT
 * Author: WuLung Hsu, wuulong@gmail.com
 *  doc: https://paper.dropbox.com/doc/FBTUG-FarmHarvestBot-OpenCR--AXheYDmXaKg~v7I1J1WYgFB7Ag-KKIOxeWkjnEwHyJZ51GUU#:uid=329885975022421369607500&h2=%E5%AF%A6%E9%A9%97-1.4---%E6%B8%AC%E8%A9%A6-Max-ISR-rate
 */
#define EXTI_0          2
#define EXTI_1          3
#define EXTI_2          4
#define TARGET_CNT     1000
unsigned long isr_cnt = 0;
int state=0; // 0: end/init, 1: start
unsigned long debug_cnt = 0;
unsigned long time_prev=0;
unsigned long loop_cnt=0;

void setup(){
  Serial.begin(115200);

  pinMode(EXTI_1, OUTPUT);
  pinMode(EXTI_0, INPUT_PULLDOWN);
  pinMode(EXTI_2, INPUT_PULLDOWN);

  /*It can be choose as CHANGE, RISING or FALLING*/
  attachInterrupt(0, change_EXIT_0, CHANGE);
  attachInterrupt(2, rising_EXIT_2, RISING);

  time_prev = micros();
  
}

void change_EXIT_0(void){
  //Serial.println("EXIT_Interrupt! 0");
  state = digitalRead(EXTI_0);
  if(state==1){
    isr_cnt = 0;
    loop_cnt = 0;
    digitalWrite(EXTI_1,0);
  }else{
    if(isr_cnt==TARGET_CNT){
      // if((loop_cnt % 2) == 0) #random output result for testing purpose
      digitalWrite(EXTI_1,1);  
      
    }else{
      digitalWrite(EXTI_1,0);
    }
  }

}

void rising_EXIT_2(void){
  long i=0;
  char str2[32];
  if(state >0){
    isr_cnt ++;
  }

  for(i=0;i<100;i++){
    debug_cnt++;
  }
  
}

void loop(){
  char str_buf[32];
  if(state==1){
    loop_cnt ++;
  }
  long time_now = micros();
  
  if(time_now - time_prev > 1000000){
    time_prev = time_now;
    sprintf(str_buf,"%i %i %i %lu", state,isr_cnt, loop_cnt,debug_cnt);
    Serial.println(str_buf);     
  }
}
