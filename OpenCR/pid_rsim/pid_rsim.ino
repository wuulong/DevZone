/*
 * OpenCR PID real simulator
 * features:
 *    a tool for tunning PID parameter
 * Usage:

 * Default output:Setpoint, Output
 * Default transfer function
 *    Amplifier , 2 times
 * LICENSE: MIT
 * Author: WuLung Hsu, wuulong@gmail.com
 *  doc: https://paper.dropbox.com/doc/FBTUG-FarmHarvestBot-PID--AZqCRYp2UOWjxVZmARyJQiDfAg-LXwJwDEhTrftgGmRetVrM#:uid=334945626962486621734538&h2=PID-%E6%B8%AC%E8%A9%A6%E8%88%87%E6%A8%A1%E6%93%AC%E8%88%87%E9%A9%97%E8%AD%89%E7%9A%84%E5%B0%8F%E5%B7%A5%E5%85%B7
 */

#include <PID_v1.h>

//Define Variables we'll be connecting to
double Setpoint, POutput, Err, Output; 

//double aggKp=4, aggKi=0.2, aggKd=1;
//double consKp=1, consKi=0.05, consKd=0.25;
double Kp=0.4, Ki=0.30, Kd=0.0;
double set_user=100.0;

//Specify the links and initial tuning parameters
PID myPID(&Output, &POutput, &Setpoint, Kp, Ki, Kd, DIRECT);

unsigned long tick_cur=0, tick_target=0, tick_report=0;

void target_proc(unsigned long tick)
{
  if(tick - tick_target > 20000){
    if(Setpoint==0) Setpoint=set_user;
    else Setpoint =0;

    tick_target = tick;
  }
}

void error_proc(unsigned long tick)
{
  Err = abs(Setpoint-Output); //distance away from setpoint , useless. for debug purpose
}

void plant_proc(unsigned long tick)
{
  Output = POutput * 2;
}

void report_proc(unsigned long tick)
{
  if(tick - tick_report > 100){
    Serial.print(Setpoint);
    Serial.print(",");
    Serial.print(Output);
    /*Serial.print(",");
    Serial.print(Err);
    Serial.print(",");
    Serial.print(POutput);
    */Serial.print("\n");
    
    tick_report = tick;
  }
}
void setup()
{
  Setpoint=set_user;
  //initialize the variables we're linked to
  Err = 0;

  //turn the PID on
  myPID.SetMode(AUTOMATIC);

  Serial.begin(115200);
}

void loop()
{
  tick_cur = millis();
  target_proc(tick_cur);
  error_proc(tick_cur);
  
  myPID.Compute();
  //analogWrite(3,POutput);
  
  plant_proc(tick_cur);
  report_proc(tick_cur);
}
