# CardiacMonitoring
arduino+python 心电图识别软件

配件 Arduino或者任意单片机 AD8232 放大电路 医疗电极贴片 导线若干 可选树莓派作为服务端带个充电宝 便携

arduino 代码

执行 main.py 会启动一个ui
服务端在SocketModel里面 具体启动参数 看代码

`void setup() {
  Serial.begin(9600);
  pinMode(11, INPUT);
  pinMode(10, INPUT);
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
    delay(10);
}`
