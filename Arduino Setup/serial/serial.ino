#include <Mouse.h>

void setup() {
  Mouse.begin();
  Serial.begin(115200);
  Serial.setTimeout(1);
}

String split(String data, char separator, int index) {
  int found = 0;
  int strIndex[] = { 0, -1 };
  int maxIndex = data.length() - 1;
  for (int i = 0; i <= maxIndex && found <= index; i++) {
    if (data.charAt(i) == separator || i == maxIndex) {
      found++;
      strIndex[0] = strIndex[1] + 1;
      strIndex[1] = (i == maxIndex) ? i + 1 : i;
    }
  }
  return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}

void loop() {
  if (Serial.available() > 0) {
    String rawdata = Serial.readString();
    String _x = split(rawdata, ',', 0);
    String _y = split(rawdata, ',', 1);
    String _m = split(rawdata, ',', 2);
    if ((_x.length() > 0) && (_y.length() > 0) && (_m.length() > 0)) {
      int x = _x.toInt();
      int y = _y.toInt();
      int m = _m.toInt();
      Mouse.move(x, y);
      if (m == 1) {
        Mouse.press(MOUSE_LEFT);
        Mouse.release(MOUSE_LEFT);
      }
    }
  }
}
