#include <Wire.h>

int z;

void setup()
{
  pinMode(5,OUTPUT);
  pinMode(12,OUTPUT);
  pinMode(11,OUTPUT);
  pinMode(10,OUTPUT);
  pinMode(9,OUTPUT);
  pinMode(8,OUTPUT);
  pinMode(7,OUTPUT);
  pinMode(6,OUTPUT);
  Wire.begin(4);                
  Wire.onReceive(receiveEvent); 
  Serial.begin(9600);
  delay(500);
}

void receiveEvent(int howMany)
{
  int x = Wire.read(); 
  z=x; 
}

void loop()
{
  int a, b, c, d;
  int i, j, k, l;
  digitalWrite(9, LOW);
  digitalWrite(8, HIGH);   //G
  digitalWrite(5, HIGH);
  digitalWrite(12, LOW);   //R 
  digitalWrite(11, HIGH);
  digitalWrite(10, LOW);   //R
  digitalWrite(7, HIGH);
  digitalWrite(6, LOW);    //R
  Serial.println();
  if ( z==50 || z==4 || z==15 || z==6 || z==20 || z==8 || z==25 || z==62 || z==64 || z==66 || z==68 || z==70 || z==72 || z==74 || z==76 || z==88 || z==90 || z==168 || z==170 || z==172 || z==174 || z==176 || z==178 || z==180 || z==84)  
  {
    a=5;
  }
  else if ( z==10 || z==104 || z==106 || z==112 || z==120 || z==122 || z==124 || z==128 || z==130 || z==134 || z==138 || z==142 || z==144 || z==148 || z==152 || z==156 || z==158 || z==162 || z==200 || z==202 || z==204 || z==206 || z==210 || z==216 || z==58)
  {
    a=10;
  }
  else
  {
    a=15;
  }
  for (i=0;i<a;++i)
  {
    Serial.print(a-i);
    Serial.print(" ");
    delay(100);
  }
  digitalWrite(9, HIGH);
  digitalWrite(8, HIGH);   //Y
  delay(100);
  digitalWrite(9, HIGH);
  digitalWrite(8, LOW);    //R
  digitalWrite(5, LOW);
  digitalWrite(12, HIGH);  //G 
  Serial.println();
  if ( z==50 || z==2 || z==10 || z==6 || z==20 || z==8 || z==25 || z==108 || z==110 || z==112 || z==114 || z==116 || z==118 || z==120 || z==122 || z==70 || z==72 || z==74 || z==76 || z==152 || z==154 || z==156 || z==158 || z==160 || z==162 || z==164 || z==82)
  {
    b=5;
  }
  else if ( z==15 || z==102 || z==106 || z==66 || z==68 || z==90 || z==92 || z==124 || z==126 || z==130 || z==136 || z==138 || z==140 || z==144 || z==150 || z==168 || z==172 || z==174 || z==178 || z==200 || z==202 || z==204 || z==208 || z==210 || z==218 || z==220 || z==56)
  {
    b=10;
  }
  else
  {
    b=15;
  }
  for (j=0;j<b;++j)
  {
    Serial.print(b-j);
    Serial.print(" ");
    delay(100);
  }
  digitalWrite(5, HIGH);
  digitalWrite(12, HIGH);  //Y 
  delay(100);
  digitalWrite(5, HIGH);
  digitalWrite(12, LOW);   //R 
  digitalWrite(11, LOW);
  digitalWrite(10, HIGH);  //G      
  Serial.println();
  if( z==50 || z==2 || z==10 || z==4 || z==15 || z==6 || z==20 || z==100 || z==102 || z==104 || z==106 || z==108 || z==110 || z==112 || z==114 || z==86 || z==88 || z==90 || z==92 || z==124 || z==126 || z==128 || z==130 || z==132 || z==134 || z==136 || z==78)
  {
    c=5;
  }
  else if( z==25 || z==118 || z==122 || z==64 || z==68 || z==72 || z==76 || z==138 || z==140 || z==142 || z==146 || z==152 || z==154 || z==156 || z==160 || z==168 || z==170 || z==172 || z==176 || z==200 || z==204 || z==206 || z==208 || z==212 || z==214 || z==220 || z==52)
  {
    c=10;
  }
  else
  {  
    c=15;
  }
  for (k=0;k<c;++k)
  {
    Serial.print(c-k);
    Serial.print(" ");
    delay(100);
  }
  digitalWrite(11, HIGH);
  digitalWrite(10, HIGH);  //Y 
  delay(100);
  digitalWrite(11, HIGH);
  digitalWrite(10, LOW);   //R
  digitalWrite(7, LOW);
  digitalWrite(6, HIGH);   //G      
  Serial.println();
  if( z==50 || z==2 || z==10 || z==4 || z==15 || z==8 || z==25 || z==100 || z==102 || z==104 || z==106 || z==116 || z==118 || z==120 || z==122 || z==62 || z==64 || z==66 || z==68 || z==138 || z==140 || z==142 || z==144 || z==146 || z==148 || z==150 || z==80)
  {
    d=5;
  }
  else if( z==20 || z==110 || z==114 || z==74 || z==76 || z==88 || z==92 || z==124 || z==126 || z==128 || z==132 || z==152 || z==154 || z==158 || z==164 || z==168 || z==170 || z==174 || z==180 || z==200 || z==202 || z==206 || z==208 || z==214 || z==216 || z==218 || z==54)
  {
    d=10;
  }
  else
  {
    d=15;
  }
  for (l=0;l<d;++l)
  { 
    Serial.print(d-l);
    Serial.print(" ");
    delay(100);
  }
  digitalWrite(7, HIGH);
  digitalWrite(6, HIGH);   //Y      
  delay(100);  
  Serial.println();    
}