# CardiacMonitoring
arduino+python 心电图识别软件

配件 Arduino或者任意单片机 AD8232 放大电路 医疗电极贴片 导线若干 可选树莓派作为服务端带个充电宝 便携

arduino 代码
`
void setup() {
  // initialize the serial communication:
  Serial.begin(9600);
  pinMode(11, INPUT); // Setup for leads off detection LO +
  pinMode(10, INPUT); // Setup for leads off detection LO -
}

void loop() {
  if ((digitalRead(10) == 1) || (digitalRead(11) == 1)) {
    Serial.println(-100);
  }
  else {
    // send the value of analog input 0:
    int dat = analogRead(A0);
    Serial.println(dat);
  }
  //Wait for a bit to keep serial data from saturating
    delay(10);
}
`
