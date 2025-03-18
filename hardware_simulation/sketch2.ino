#include <Wire.h>

int cm = 0;

long readUltrasonicDistance(int triggerPin, int echoPin)
{
  pinMode(triggerPin, OUTPUT);  
  digitalWrite(triggerPin, LOW);
  delayMicroseconds(2);
  digitalWrite(triggerPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(triggerPin, LOW);
  pinMode(echoPin, INPUT);
  return pulseIn(echoPin, HIGH);
}

int flag(int tp, int ep)
{
  cm = 0.01723 * readUltrasonicDistance(tp,ep);
  if(cm<200)
  return (HIGH);
  else
  return (LOW);
}

void transmission(int f, int d)
{
  Wire.beginTransmission(d); 
  Wire.write(f);           
  Wire.endTransmission();
}  

void setup()
{
  Wire.begin();
  Serial.begin(9600);
}

void loop()
{    
  int a=0, b=0, c=0, d=0;
  while (flag(7,7)==LOW && flag(9,9)==LOW && flag(11,11)==LOW && flag(13,13)==LOW)
  {
    Serial.println(1);
    transmission(50,4);
    transmission(50,6);
  }

  //Any One Intersection is Conjested
  
  while (flag(7,7)==HIGH && flag(9,9)==LOW && flag(11,11)==LOW && flag(13,13)==LOW)
  {
    if (flag(6,6)==HIGH)
    { 
      Serial.println(78);
      transmission(2,6);
      transmission(2,4);
    }
    else
    {
      Serial.println(2);
      transmission(10,4);
      transmission(10,6);
    }
  }
  
  while (flag(7,7)==LOW && flag(9,9)==HIGH && flag(11,11)==LOW && flag(13,13)==LOW)
  {
    if (flag(8,8)==HIGH)
    {
      Serial.println(79);
      transmission(4,6);
      transmission(4,4);
    }
    else
    {
      Serial.println(3);
      transmission(15,4);
      transmission(15,6);
    } 
  }
  
  while (flag(7,7)==LOW && flag(9,9)==LOW && flag(11,11)==HIGH && flag(13,13)==LOW)
  {
    if (flag(10,10)==HIGH)
    {
      Serial.println(80);
      transmission(6,6);
      transmission(6,4);
    }
    else
    {
      Serial.println(4);
      transmission(20,4);
      transmission(20,6);
    } 
  }
 
  while (flag(7,7)==LOW && flag(9,9)==LOW && flag(11,11)==LOW && flag(13,13)==HIGH)
  {
    if (flag(12,12)==HIGH)
    {
      Serial.print(82);
      transmission(8,6);
      transmission(8,4);
    }
    else
    {
      Serial.println(5);
      transmission(25,4);
      transmission(25,6);
    } 
  }

  //Any Two Intersection is Conjested
  
  while (flag(7,7)==HIGH && flag(9,9)==HIGH && flag(11,11)==LOW && flag(13,13)==LOW)
  {
    a=flag(6,6);
    b=flag(8,8);
    if (a==HIGH && b==HIGH)
    {
      Serial.println(6);
      transmission(100,4);
      transmission(100,6);
    }
    if (a==HIGH && b==LOW)
    {
      Serial.println(7);
      transmission(102,4);
      transmission(102,6);
    }
    if (a==LOW && b==HIGH)
    {
      Serial.println(8);
      transmission(104,4);
      transmission(104,6);
    }
    if (a==LOW && b==LOW)
    {
      Serial.println(9);
      transmission(106,4);
      transmission(106,6);
    }
  }
  
  while (flag(7,7)==HIGH && flag(9,9)==LOW && flag(11,11)==HIGH && flag(13,13)==LOW)
  {
    a=flag(6,6);
    c=flag(10,10);
    if (a==HIGH && c==HIGH)
    {
      Serial.println(10);
      transmission(108,4);
      transmission(108,6);
    }
    if (a==HIGH && c==LOW)
    {
      Serial.println(11);
      transmission(110,4);
      transmission(110,6);
    }
    if (a==LOW && c==HIGH)
    {
      Serial.println(12);
      transmission(112,4);
      transmission(112,6);
    }
    if (a==LOW && c==LOW)
    {
      Serial.println(13);
      transmission(114,4);
      transmission(114,6);
    }
  }
  
  while (flag(7,7)==HIGH && flag(9,9)==LOW && flag(11,11)==LOW && flag(13,13)==HIGH)
  {
    a=flag(6,6);
    d=flag(12,12);
    if (a==HIGH && d==HIGH)
    {
      Serial.println(14);
      transmission(116,4);
      transmission(116,6);
    }
    if (a==HIGH && d==LOW)
    {
      Serial.println(15);
      transmission(118,4);
      transmission(118,6);
    }
    if (a==LOW && d==HIGH)
    {
      Serial.println(16);
      transmission(120,4);
      transmission(120,6);
    }
    if (a==LOW && d==LOW)
    {
      Serial.println(17);
      transmission(122,4);
      transmission(122,6);
    }
  }

  while (flag(7,7)==LOW && flag(9,9)==HIGH && flag(11,11)==LOW && flag(13,13)==HIGH)
  {
    b=flag(8,8);
    d=flag(12,12);
    if (b==HIGH && d==HIGH)
    {
      Serial.println(18);
      transmission(62,4);
      transmission(62,6);
    }
    if (b==HIGH && d==LOW)
    {
      Serial.println(19);
      transmission(64,4);
      transmission(64,6);
    }
    if (b==LOW && d==HIGH)
    {
      Serial.println(20);
      transmission(66,4);
      transmission(66,6);
    }
    if (b==LOW && d==LOW)
    {
      Serial.println(21);
      transmission(68,4);
      transmission(68,6);
    }
  }
  while (flag(7,7)==LOW && flag(9,9)==LOW && flag(11,11)==HIGH && flag(13,13)==HIGH)
  {
    c=flag(10,10);
    d=flag(12,12);
    if (c==HIGH && d==HIGH)
    {
      Serial.println(22);
      transmission(70,4);
      transmission(70,6);
    }
    if (c==HIGH && d==LOW)
    {
      Serial.println(23);
      transmission(72,4);
      transmission(72,6);
    }
    if (c==LOW && d==HIGH)
    {
      Serial.println(24);
      transmission(74,4);
      transmission(74,6);
    }
    if (c==LOW && d==LOW)
    {
      Serial.println(25);
      transmission(76,4);
      transmission(76,6);
    }
  }
  while (flag(7,7)==LOW && flag(9,9)==HIGH && flag(11,11)==HIGH && flag(13,13)==LOW)
  {
    b=flag(8,8);
    c=flag(10,10);
    if (b==HIGH && c==HIGH)
    {
      Serial.println(26);
      transmission(86,4);
      transmission(86,6);
    }
    if (b==HIGH && c==LOW)
    {
      Serial.println(27);
      transmission(88,4);
      transmission(88,6);
    }
    if (b==LOW && c==HIGH)
    {
      Serial.println(28);
      transmission(90,4);
      transmission(90,6);
    }
    if (b==LOW && c==LOW)
    {
      Serial.println(29);
      transmission(92,4);
      transmission(92,6);
    }
  }
  
  //Any Three Intersection is Conjested

  while (flag(7,7)==HIGH && flag(9,9)==HIGH && flag(11,11)==HIGH && flag(13,13)==LOW)
  {
    a=flag(6,6);
    b=flag(8,8);
    c=flag(10,10);  
    if (a==LOW && b==LOW && c==LOW)
    {
      Serial.println(30);
      transmission(124,4);
      transmission(124,6);
    }
    if (a==HIGH && b==LOW && c==LOW)
    {
      Serial.println(31);
      transmission(126,4);
      transmission(126,6);
    }
    if (a==LOW && b==HIGH && c==LOW)
    {
      Serial.println(32);
      transmission(128,4);
      transmission(128,6);
    }
    if (a==LOW && b==LOW && c==HIGH)
    {
      Serial.println(33);
      transmission(130,4);
      transmission(130,6);
    }
    if (a==HIGH && b==HIGH && c==LOW)
    {
      Serial.println(34);
      transmission(132,4);
      transmission(132,6);
    }
    if (a==LOW && b==HIGH && c==HIGH)
    {
      Serial.println(35);
      transmission(134,4);
      transmission(134,6);
    }
    if (a==HIGH && b==LOW && c==HIGH)
    {
      Serial.println(36);
      transmission(136,4);
      transmission(136,6);
    }
    if (a==HIGH && b==HIGH && c==HIGH)
    {
      Serial.println(37);
      transmission(78,4);
      transmission(78,6);
    }
  }
  
  while (flag(7,7)==HIGH && flag(9,9)==HIGH && flag(11,11)==LOW && flag(13,13)==HIGH)
  {
    a=flag(6,6);
    b=flag(8,8);
    d=flag(12,12);
    if (a==LOW && b==LOW && d==LOW)
    {
      Serial.println(38);
      transmission(138,4);
      transmission(138,6);
    }
    if (a==HIGH && b==LOW && d==LOW)
    {
      Serial.println(39);
      transmission(140,4);
      transmission(140,6);
    }
    if (a==LOW && b==HIGH && d==LOW)
    {
      Serial.println(40);
      transmission(142,4);
      transmission(142,6);
    }
    if (a==LOW && b==LOW && d==HIGH)
    {
      Serial.println(41);
      transmission(144,4);
      transmission(144,6);
    }
    if (a==HIGH && b==HIGH && d==LOW)
    {
      Serial.println(42);
      transmission(146,4);
      transmission(146,6);
    }
    if (a==LOW && b==HIGH && d==HIGH)
    {
      Serial.println(43);
      transmission(148,4);
      transmission(148,6);
    }
    if (a==HIGH && b==LOW && d==HIGH)
    {
      Serial.println(44);
      transmission(150,4);
      transmission(150,6);
    }
    if (a==HIGH && b==HIGH && d==HIGH)
    {
      Serial.println(45);
      transmission(80,4);
      transmission(80,6);
    }
  }
  
  while (flag(7,7)==HIGH && flag(9,9)==LOW && flag(11,11)==HIGH && flag(13,13)==HIGH)
  {
    a=flag(6,6);
    c=flag(10,10);
    d=flag(12,12);
    if (a==LOW && c==LOW && d==LOW)
    {
      Serial.println(46);
      transmission(152,4);
      transmission(152,6);
    }
    if (a==HIGH && c==LOW && d==LOW)
    {
      Serial.println(47);
      transmission(154,4);
      transmission(154,6);
    }
    if (a==LOW && c==HIGH && d==LOW)
    {
      Serial.println(48);
      transmission(156,4);
      transmission(156,6);
    }
    if (a==LOW && c==LOW && d==HIGH)
    {
      Serial.println(49);
      transmission(158,4);
      transmission(158,6);
    }
    if (a==HIGH && c==HIGH && d==LOW)
    {
      Serial.println(50);
      transmission(160,4);
      transmission(160,6);
    }
    if (a==LOW && c==HIGH && d==HIGH)
    {
      Serial.println(51);
      transmission(162,4);
      transmission(162,6);
    }
    if (a==HIGH && c==LOW && d==HIGH)
    {
      Serial.println(52);
      transmission(164,4);
      transmission(164,6);
    }
    if (a==HIGH && c==HIGH && d==HIGH)
    {
      Serial.println(53);
      transmission(82,4);
      transmission(82,6);
    }
  }
  while (flag(7,7)==LOW && flag(9,9)==HIGH && flag(11,11)==HIGH && flag(13,13)==HIGH)
  {
    b=flag(8,8);
    c=flag(10,10);
    d=flag(12,12);
    if (b==LOW && c==LOW && d==LOW)
    {
      Serial.println(54);
      transmission(168,4);
      transmission(168,6);
    }
    if (b==HIGH && c==LOW && d==LOW)
    {
      Serial.println(55);
      transmission(170,4);
      transmission(170,6);
    }
    if (b==LOW && c==HIGH && d==LOW)
    {
      Serial.println(56);
      transmission(172,4);
      transmission(172,6);
    }
    if (b==LOW && c==LOW && d==HIGH)
    {
      Serial.println(57);
      transmission(174,4);
      transmission(174,6);
    }
    if (b==HIGH && c==HIGH && d==LOW)
    {
      Serial.println(58);
      transmission(176,4);
      transmission(176,6);
    }
    if (b==LOW && c==HIGH && d==HIGH)
    {
      Serial.println(59);
      transmission(178,4);
      transmission(178,6);
    }
    if (b==HIGH && c==LOW && d==HIGH)
    {
      Serial.println(60);
      transmission(180,4);
      transmission(180,6);
    }
    if (b==HIGH && c==HIGH && d==HIGH)
    {
      Serial.println(61);
      transmission(84,4);
      transmission(84,6);
    }
  }

  //All Four Intersection is Conjested

  while (flag(7,7)==HIGH && flag(9,9)==HIGH && flag(11,11)==HIGH && flag(13,13)==HIGH)
  {
    a=flag(6,6);
    b=flag(8,8);
    c=flag(10,10);
    d=flag(12,12);
    if (a==LOW && b==LOW && c==LOW && d==LOW)
    {
      Serial.println(62);
      transmission(200,4);
      transmission(200,6);
    } 
    if (a==LOW && b==LOW && c==LOW && d==HIGH)
    {
      Serial.println(63);
      transmission(202,4);
      transmission(202,6);
    }
    if (a==LOW && b==LOW && c==HIGH && d==LOW)
    {
      Serial.println(64);
      transmission(204,4);
      transmission(204,6);
    }
    if (a==LOW && b==HIGH && c==LOW && d==LOW)
    {
      Serial.println(65);
      transmission(206,4);
      transmission(206,6);
    }
    if (a==HIGH && b==LOW && c==LOW && d==LOW)
    {
      Serial.println(66);
      transmission(208,4);
      transmission(208,6);
    }
    if (a==LOW && b==LOW && c==HIGH && d==HIGH)
    {
      Serial.println(67);
      transmission(210,4);
      transmission(210,6);
    }
    if (a==LOW && b==HIGH && c==HIGH && d==LOW)
    {
      Serial.println(68);
      transmission(212,4);
      transmission(212,6);
    }
    if (a==HIGH && b==HIGH && c==LOW && d==LOW)
    {
      Serial.println(69);
      transmission(214,4);
      transmission(214,6);
    }
    if (a==LOW && b==HIGH && c==LOW && d==HIGH)
    {
      Serial.println(70);
      transmission(216,4);
      transmission(216,6);
    }
    if (a==HIGH && b==LOW && c==LOW && d==HIGH)
    {
      Serial.println(71);
      transmission(218,4);
      transmission(218,6);
    }
    if (a==HIGH && b==LOW && c==HIGH && d==LOW)
    {
      Serial.println(72);
      transmission(220,4);
      transmission(220,6);
    }
    if (a==HIGH && b==HIGH && c==HIGH && d==LOW)
    {
      Serial.println(73);
      transmission(52,4);
      transmission(52,6);
    }
    if (a==HIGH && b==HIGH && c==LOW && d==HIGH)
    {
      Serial.println(74);
      transmission(54,4);
      transmission(54,6);
    }
    if (a==HIGH && b==LOW && c==HIGH && d==HIGH)
    {
      Serial.println(75);
      transmission(56,4);
      transmission(56,6);
    }
    if (a==LOW && b==HIGH && c==HIGH && d==HIGH)
    {
      Serial.println(76);
      transmission(58,4);
      transmission(58,6);
    }
    if (a==HIGH && b==HIGH && c==HIGH && d==HIGH)
    {
      Serial.println(77);
      transmission(60,4);
      transmission(60,6);
    }
  }
  delay(100);
}