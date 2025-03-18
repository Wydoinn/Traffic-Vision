#include <Wire.h>

void setup()
{
  pinMode(5, OUTPUT);
  pinMode(12, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(6, OUTPUT);
  Wire.begin(6);                
  Wire.onReceive(receiveEvent); 
  Serial.begin(9600);          
}

void loop()
{
  delay(100);
 
}


void receiveEvent(int howMany)
{
  int x = Wire.read();    
  if (x==50)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G 
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G 
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G 
  }
  if (x==2)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G 
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G 
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R 
  }
  if (x==10)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G 
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G 
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y 
  } 
  if (x==4)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G 
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G 
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R 
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G
  }
  if (x==15)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G 
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G 
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y 
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G
  }
   if (x==6)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G 
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G 
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G 
  }
  if (x==20)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G 
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G 
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G 
  } 
  if (x==8)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G 
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G 
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G 
  }
  if (x==25)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G 
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y 
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G 
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G 
  } 
  
  // Any Two is Conjested
  
  if (x==100)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G 
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G 
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R 
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R 
  } 
  if (x==102)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G 
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G 
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y 
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R 
  }
  if (x==104)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G 
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G 
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R 
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y 
  }
  if (x==106)
  {
   digitalWrite(5, LOW);    
   digitalWrite(12, HIGH);   //G 
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G 
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y 
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y 
  }   
  if (x==108)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R 
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G 
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G 
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R 
  }
  if (x==110)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y 
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G 
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G 
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R
  }   
  if (x==112)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R 
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G 
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G 
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y 
  }  
  if (x==114)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y 
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G 
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G 
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y 
  }   
  if (x==116)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G 
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R 
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G 
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R
  } 
  if (x==118)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G 
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y 
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G 
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R
  } 
  if (x==120)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G 
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y
  }
  if (x==122)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y
  }
  if (x==62)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G
  }
  if (x==64)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G
  }
  if (x==66)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G
  } 
  if (x==68)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G
  }   
  if (x==70)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G
  }   
  if (x==72)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G
  }   
  if (x==74)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G
  } 
  if (x==76)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G
  } 
  if (x==86)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G
  }
  if (x==88)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G
  }
  if (x==90)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G
  }
  if (x==92)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G
  }
  
  // Any Three Conjested
  
  if (x==124)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y
  } 
  if (x==126)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R
  }   
  if (x==128)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y
  } 
  if (x==130)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y
  } 
  if (x==132)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R
  } 
  if (x==134)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y
  }   
  if (x==136)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R
  }
  if (x==78)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, LOW); 
   digitalWrite(10, HIGH);   //G
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R
  }
  if (x==138)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y
  }
  if (x==140)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R
  }
  if (x==142)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y
  }
  if (x==144)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y
  }
  if (x==146)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R
  }
  if (x==148)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y
  }
  if (x==150)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R
  }
  if (x==80)
  {
   digitalWrite(5, LOW); 
   digitalWrite(12, HIGH);   //G
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R
  }
  if (x==152)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y
  }
  if (x==154)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R
  }
  if (x==156)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y
  }
  if (x==158)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y
  }
  if (x==160)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R
  }
  if (x==162)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y
  }
  if (x==164)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R
  }
  if (x==82)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, LOW);  
   digitalWrite(8, HIGH);    //G
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R
  }
  if (x==168)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G
  }
  if (x==170)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G
  }
  if (x==172)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G
  }
  if (x==174)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G
  }
  if (x==176)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G
  }
  if (x==178)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G
  }
  if (x==180)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G
  }
  if (x==84)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, LOW); 
   digitalWrite(6, HIGH);    //G
  }
  
  //All Four Intersection is Conjested
  
  if (x==200)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y
  }
  if (x==202)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y
  }
  if (x==204)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y
  }
  if (x==206)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y
  }
  if (x==208)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R
  }
  if (x==210)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y
  }
  if (x==212)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y
  }
  if (x==214)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R
  }
  if (x==216)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y
  }
  if (x==218)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R
  }
  if (x==220)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, HIGH);  
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //R
  }
  if (x==52)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, HIGH); 
   digitalWrite(10, HIGH);   //Y
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R
  }
  if (x==54)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, HIGH);   //Y
   digitalWrite(11, HIGH);
   digitalWrite(10, LOW);    //R
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R
  }
  if (x==56)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, HIGH);   
   digitalWrite(8, HIGH);    //Y
   digitalWrite(7, HIGH);  
   digitalWrite(6, LOW);     //R
  }
  if (x==58)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, HIGH); 
   digitalWrite(6, HIGH);    //Y
  }
  if (x==60)
  {
   digitalWrite(5, HIGH); 
   digitalWrite(12, LOW);    //R
   digitalWrite(11, HIGH); 
   digitalWrite(10, LOW);    //R
   digitalWrite(9, HIGH);  
   digitalWrite(8, LOW);     //R
   digitalWrite(7, HIGH); 
   digitalWrite(6, LOW);     //R
  }
}