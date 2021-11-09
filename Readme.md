# Inhaltsverzeichnis





[TOC]





# 1 Allgemeine Daten





| Abmessungen              | 3,00m x 1,25m |
| ------------------------ | ------------- |
| Anzahl LED               | 14400         |
| Anzahl LED-Streifen      | 192           |
| Anzahl LED / Streifen    | 75            |
| Anzahl Teensy4           | 2             |
| Anzahl Channel           | 16            |
| Anzahl Channel / Teensy  | 8             |
| Anzahl LED / Channel     | 900           |
| Anzahl Raspberry Pi      | 1             |
| Anzahl Netzteile         | 12            |
| Leistung / Netzteil      | 350W          |
| Stromstärke / Netzteile  | 70A           |
| Ausgabespannung Netzteil | 5V            |
| Anschluss Leistung       | circa 4200W   |
|                          |               |
|                          |               |



(Bild gesamt)





# 2 Hardware

## 2.1 Stromversorgung

### 2.1.1 Relais-Netzteil

![img](https://lh4.googleusercontent.com/hmO1Aso4R9J6UwY6ocMb_xBabUQ7OHdV8xS_04T-KhUgXZS0XQbydubJco_wPyhZYbKMAOiI_yLZz6SNXSU8Cj_qkdkMwxdR81HLliwT5HzGxIrnJVKGonSXdyNsilc_EV1V37k_)Über das Relais wird die Phase des Stromanschlusses verzögert an die Netzteile geleitet und startet diese nacheinander. Dadurch wird die auf einmal auftretende Strombedarfs-Spitze geglättet.

Die Null-Phase wie die Erdung wird direkt an die Netzteile angeschlossen.

### 2.1.2 Netzteil LED-Streifen

![img](https://lh4.googleusercontent.com/hmO1Aso4R9J6UwY6ocMb_xBabUQ7OHdV8xS_04T-KhUgXZS0XQbydubJco_wPyhZYbKMAOiI_yLZz6SNXSU8Cj_qkdkMwxdR81HLliwT5HzGxIrnJVKGonSXdyNsilc_EV1V37k_)

Aus jedem der 12 Netzteile, werden vier Kabel (zwei Paare bestehend aus Plus- und Minuspolung) zur Stromversorgung abgeführt. Diese werden in einer Schraubverteilungsschiene auf jeweils acht LED-Streifen aufgeteilt.

Durch diesen Aufbau werden insgesamt 48 Kabel (zusammengefasst in 24 Doppelkabel) in 24 Verteilerblöcke aufgeteilt.



(Bild Verteilerblock)



Alle Anschlüsse werden durch Schraub-Klemm verbindungen gebildet.



(Bilder der Anschlüsse- Netzgerät wie Verteilerblock)





### 2.1.3 Raspberry Pi Stromzufuhr



Die Stromzufuhr für den Raspberry Pi erfolgt gesondert. Dadurch kann dieser immer an bleiben und über seine GPIO Pins die bereits erwähnten Relais schalten.



### 2.1.4 Teensy4



(Schema)

![img](https://lh4.googleusercontent.com/0axk4GieoA4J7XJdmdlkXIRMR-CZfsgF7c2TKuhGNn3nY2wpJqgHXJV148RHZl_QcMvyFP6bAaNin0NtUNNydEl8SiCVtNMcW1YkGNuFMRdB_ymFUyOk_7m_LB69nmPz0PbTOxTL)



Die beiden Mikrocontroller werden an einem der Netzteile angeschlossen. Zusätzlich zur Stromzufuhr an einem Netzteil, wird deren Erdung über die gesamte Anzahl der Netzgeräte verteilt. Nur dadurch wird ein Störungsfreies Bild gewährleistet.

## 2.2 Datenleitungen



### 2.2.1 LED-Streifen zu Teensy



![img](https://lh4.googleusercontent.com/0axk4GieoA4J7XJdmdlkXIRMR-CZfsgF7c2TKuhGNn3nY2wpJqgHXJV148RHZl_QcMvyFP6bAaNin0NtUNNydEl8SiCVtNMcW1YkGNuFMRdB_ymFUyOk_7m_LB69nmPz0PbTOxTL)



Jeder der Teensies besitzt acht Channels, die über ein PWM-Signal die Farbcodierung an die LED Streifen übermitteln. Durch insgesamt 16 Channel werden 900LEDs, über 12Streifen verteilt, an einen Channel angeschlossen. alle acht channels des Teensy verlaufen in einem Kabel und werden nach und nach an die Fassade abgeleitet. Der Anschluss am Teensy selbst, wird über Ethernet-Stecker gebildet, die in einem Adapterboard auf die Pins treffen.



(Bild/schema Ethernet stecker)



### 2.2.2 Teensy synchronisation



Um die Daten der beiden Teensy aufeinander abzustimmen, werden diese über den synchronisations Pin verbunden.



### 2.2.3 Teensy zu Raspberry Pi



Die Daten des Raspberry Pi werden über eine Serielle USB Schnittstelle weitergegeben



### 2.2.4 Raspberry Pi Relais



![img](https://lh4.googleusercontent.com/0axk4GieoA4J7XJdmdlkXIRMR-CZfsgF7c2TKuhGNn3nY2wpJqgHXJV148RHZl_QcMvyFP6bAaNin0NtUNNydEl8SiCVtNMcW1YkGNuFMRdB_ymFUyOk_7m_LB69nmPz0PbTOxTL)



Für jedes der 12 Relais wird ein Signal auf einen Pin des Raspberry Pi verbunden.

Die dazu verwendeten Pins sind:



(Bild mit PIN highlight)



# 3 Software

Die Software besteht aus drei Hauptbestandteilen: Der Code auf den Mikrocontrollern, der die LEDs ansteuert, die API, die die Videos verwaltet und in das LED-Format konvertiert und ein unabhängiges Webinterface, das die Anfragen an die API stellt. Der Einfachheit geschuldet wird das Webinterface und die API auf dem Raspberry zusammen in respektiven Containern ausgeführt. Die API wird auf den Unterordner “/api” geproxied.



Teensy4 Microcontoller <--> FastAPI + Movie2Serial <--> Webinterface 

## 3.1 Teensy4: DisplayVideo

Das VideoDisplay-Programm des Mikrocontrollers basiert auf dem Code von PaulStoffgren (https://github.com/PaulStoffregen/OctoWS2811/blob/master/examples/VideoDisplay_Teensy4/VideoDisplay_Teensy4.ino). Hier wurde von uns der Code hinsichtlich der Kompatibilität mit dem Teensy4 verbessert (Pull-Request pending).

Das Programm erhält den Teil des aktuellen Frame des Videos per SerialUSB Verbindung und schickt PWM Signale an den jeweiligen Channel der LED-Streifen. Desweiteren gibt es einen Main, der per Sync-Signal die Framerate des anderen Controllers, der Agent, steuert.

Die Rolle der jeweiligen Controller wird über ein Signal vom Raspberry PI festgelegt.

## 3.2 Raspberry Pi 4: API

Der wohl Komplexeste Teil der Programmierung ist die API. Sie kümmert sich um die Verwaltung der Film- und Bilddateien, bestimmt die Reihenfolge der Anzeige und konvertiert die Filme und Bilder in das für den Teensy verständliche serielle Format um.

Für diese Aufgaben sind mehrere Subprozesse verantwortlich:

FastAPI Request Handler <--> Queue Worker Thread <--> movie2serial Konvertierung

Die API ist in einer Kombination von Python 3 und Processing Java 3 geschrieben und setzt verschiedene Programme und Libraries voraus (siehe *3.2.4 Docker Container*).

### 3.2.1 FastAPI Request Handler (main.py)

Die Hauptfunktionen der API werden über FastAPI URLs gesteuert. Vor dem Starten von FastAPI werden via GPIO die Relais, mit kurzer Verzögerung, nach und nach eingeschaltet. Danach wird der queueWorker.py importiert und damit der WorkerThread gestartet, der die Queue asynchron zur API abarbeitet.

Jede Ausführung der Funktionen ist zeitlich begrenzt (ca. 30 pro Minute), um eine Überbelastung der API zu vermeiden.

#### FastAPI URLs:

##### /upload/

Über diese Funktion werden POST-Request verarbeitet, die einen Datei-Upload starten.

Inputs:

- in_file: Datei als Bytestream
- length: Anzeigedauer für Bilder als integer (optional//nur für Bilder relevant)
- recurring: Wenn Datei täglich angezeigt werden soll als Boolean (optional)
- time: Uhrzeit der Anzeige als Time (optional)
- password: Login-Passwort aus der Umgebungsvariable

##### /queue/

Diese Funktion gibt Informationen über die aktuelle Queue als json zurück.

##### /delQueue/

Diese Funktion löscht die angegebene Datei aus der Queue.

Inputs:

- movName: Name der zu löschenden Datei
- password: Login-Passwort aus der Umgebungsvariable

##### /backup/

Diese Funktion gibt eine ZIP-Datei zurück, die alle hochgeladenen Dateien enthält. Um Speicherplatz zu sparen, werden auch alle Dateien gelöscht, die nicht mehr in Benutzung sind.

Inputs:

- password: Login-Passwort aus der Umgebungsvariable

##### /power/

Diese Funktion stoppt/startet den aktuellen workerThread und schaltet alle Relais aus bzw. ein.

Inputs:

- password: Login-Passwort aus der Umgebungsvariable

### 3.2.2 Queue Worker Thread (queueWorker.py)

Neben des Haupthreads, der die Queue nach und nach abarbeitet und jedes Video der Reihe nach vom movie2serial-Programm abspielen lässt, befinden sich in dieser Python-Datei auch Funktionen, die die Basis der Interaktion von der API mit der Queue bilden.

#### Funktionen:

##### class MovieObj

Konstruiert ein Objekt mit allen nötigen Informationen über ein Medium, das abgespielt werden soll.

Eigenschaften:

- .filePath: absoluter Pfad zur Mediendatei als String
- .dTime: Zeit der Anzeige als Unix-Timestamp (optional, default = aktuelle Zeit)
- .imgLength: Länge der Anzeige bei Bildern als Integer (optional, default = None, nur applikabel bei Bildern)
- .recurrent: Ob das Medium täglich angezeigt werden soll als Boolean (optional, default = False)

Funktionen:

- getDict(): gibt das Objekt als Dictionnary zurück

##### stopWorker()

Setzt die globale Variable is_running auf False und wartet (time blocking) bis die aktuelle Iteration des workerThreads abgelaufen ist.

##### startWorker()

Erstellt und startet einen neuen workerThread.

##### putQueue(movPath, length=None)

Setzt ein Medium zur nächstmöglichen Ausführung in die Queue.

Inputs:

- movPath: absoluter Pfad zur Mediendatei als String
- length: Länge der Anzeige bei Bildern als Integer (optional, nur applikabel bei Bildern)

##### putDB(filePath, dTime, imgLength, recurrent)

Erstellt einen Datenbankeintrag zur späteren oder wiederholten Ausführung eines Mediums.

Inputs:

- filePath: absoluter Pfad zur Mediendatei als String
- dTime: Zeitpunkt der nächsten Ausführung
- imgLength: Länge der Anzeige eines Bildes (optional, nur applikabel bei Bildern)
- recurrent: Ob das Medium täglich angezeigt werden soll als Boolean (optional, default = False)

##### getQueueInfo()

Gibt Informationen über Medien in der aktuellen Queue und der Datenbank als *movieObj*-s zurück.

##### delDB(filepath)

Löscht die angegebene Datei aus der Datenbank.

Inputs:

- filepath: absoluter Pfad zur Mediendatei als String

##### cleanFiles()

Löscht alle Dateien, die sich weder in der Queue, noch in der Datenbank befinden.

##### _randomMovie()

Gibt ein MovieObj aus dem Ordner stdMovies zurück. Dies dient als Lückenfüller, wenn keine Medien in der Queue sind.

##### _workQueue(mQueue)

Haupt-Worker-Thread. In dieser Funktion wird die gegebene Queue abgearbeitet und angezeigt. Ist die Queue leer, wird ein zufälliges Video aus dem stdMovies-Ordner gezeigt. Die worker-loop wird beendet, indem die globale Variable is_running auf False gesetzt wird.

Die Funktionsweise des Threads wird im folgenden Diagramm verdeutlicht:

![img](https://lh6.googleusercontent.com/5dph6vrYPkwz_HMgra9-FRAEBaVfBZ1Dbbu-sSVh3Tc9TFQzZQp2221DmgmRQRuKyqpQp-TLdq8ylb45JNWYFSXuEkeYv3ouqcNTBtdQpfalSe92j38YvwOn3VVNRsvY9fJFK9ju)

### 3.2.3 movie2serial (Java/Processing)

Dieses Programm wandelt eine Mediendatei in das Serielle Format um und überträgt es an die Teensies. 

Der Quellcode des movie2serial-Programms basiert auf dem Code von PaulStoffgren (https://github.com/PaulStoffregen/OctoWS2811/blob/master/extras/VideoDisplay/Processing/movie2serial.pde).

Das Programm wurde grundlegend modifiziert, um erstens auch Bilder konvertieren zu können und zweitens einen Aufruf aus dem Python-Programm, mit Übergabe der notwendigen Informationen, zu ermöglichen.

Der Versuch das Processing-Programm in Python umzuschreiben ist an der geringen Geschwindigkeit der pySerial-Library gescheitert.



Das auf ARM64 kompilierte movie2serial Java Programm wird aus dem Python Script als subprocess aufgerufen. Dabei werden folgende Befehl-Arguments angehängt:

- $1: absoluter Pfad zur Mediendatei als String
- $2: zuvor in Python berechnete Framerate des Videos als Float (nicht möglich in Processing)
- $3: der Pfad der Serial Ports aus der Umgebungsvariable als String (kommagetrennt)
- $4: (optional, nur bei Bildern) Länge der Anzeige des Bildes als Integer

Der subprocess Befehl mit den jeweiligen Variablen lautet:

  “[pfad-zu]/movie2serial $1 $2 $3 $4”



Das Programm fragt zunächst die Anzeigedaten von den Teensies ab, um so das Bild gegebenenfalls in das jeweilige Format zu beschneiden



### 3.2.4 Docker Container (balena)

## 3.3 Webinterface





# 4 Anhang

## 4.2.2 movie2serial Code:

```java
/*  OctoWS2811 movie2serial.pde - Transmit video data to 1 or more
      Teensy 3.0 boards running OctoWS2811 VideoDisplay.ino
    http://www.pjrc.com/teensy/td_libs_OctoWS2811.html
    Copyright (c) 2018 Paul Stoffregen, PJRC.COM, LLC

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
*/

// Linux systems (including Raspberry Pi) require 49-teensy.rules in
// /etc/udev/rules.d/, and gstreamer compatible with Processing's
// video library.

// To configure this program, edit the following sections:
//
//  1: change myMovie to open a video file of your choice    ;-)
//
//  2: edit the serialConfigure() lines in setup() for your
//     serial device names (Mac, Linux) or COM ports (Windows)
//
//  3: if your LED strips have unusual color configuration,
//     edit colorWiring().  Nearly all strips have GRB wiring,
//     so normally you can leave this as-is.
//
//  4: if playing 50 or 60 Hz progressive video (or faster),
//     edit framerate in movieEvent().

import processing.video.*;
import processing.serial.*;
import java.awt.Rectangle;

Movie myMovie;
PImage myImage;

float gamma = 1.7;

int numPorts=0;  // the number of serial ports in use
int maxPorts=24; // maximum number of serial ports

Serial[] ledSerial = new Serial[maxPorts];     // each port's actual Serial port
Rectangle[] ledArea = new Rectangle[maxPorts]; // the area of the movie each port gets, in % (0-100)
boolean[] ledLayout = new boolean[maxPorts];   // layout of rows, true = even is left->right
PImage[] ledImage = new PImage[maxPorts];      // image sent to each port
int[] gammatable = new int[256];
int errorCount=0;
float framerate=0;

int imgTime = 0;

void settings() {
  //size(0, 0);  // create the window
}

void setup() {
  String[] inputPorts = split(args[2], ',');
  for (int i=0; i < inputPorts.length;i++) {
    println("Configure S-Port " + inputPorts[i]);
    serialConfigure(inputPorts[i]);
  }
  if (errorCount > 0) System.exit(74);
  for (int i=0; i < 256; i++) {
    gammatable[i] = (int)(pow((float)i / 255.0, gamma) * 255.0 + 0.5);
  }
  if (args.length == 3){
    myMovie = new Movie(this, args[0]);
    myMovie.play();  // start the movie :-)
  } else if (args.length == 4){
    myImage = loadImage(args[0]);
  }
  
}


// movieEvent runs for each new frame of movie data
void movieEvent(Movie m) {
  //println("movieEvent");
  // read the movie's next frame
  m.read();

  framerate = float(args[1]);

  for (int i=0; i < numPorts; i++) {
    // copy a portion of the movie's image to the LED image
    int xoffset = percentage(m.width, ledArea[i].x);
    int yoffset = percentage(m.height, ledArea[i].y);
    int xwidth =  percentage(m.width, ledArea[i].width);
    int yheight = percentage(m.height, ledArea[i].height);
    ledImage[i].copy(m, xoffset, yoffset, xwidth, yheight,
                     0, 0, ledImage[i].width, ledImage[i].height);
    // convert the LED image to raw data
    byte[] ledData =  new byte[(ledImage[i].width * ledImage[i].height * 3) + 3];
    image2data(ledImage[i], ledData, ledLayout[i]);
    if (i == 0) {
      ledData[0] = '*';  // first Teensy is the frame sync master
      int usec = (int)((1000000.0 / framerate) * 0.75);
      ledData[1] = (byte)(usec);   // request the frame sync pulse
      ledData[2] = (byte)(usec >> 8); // at 75% of the frame time
    } else {
      ledData[0] = '%';  // others sync to the master board
      ledData[1] = 0;
      ledData[2] = 0;
    }
    // send the raw data to the LEDs  :-)
    ledSerial[i].write(ledData);
  }
}

// imageEvent runs once then sleeps for the time the image is displayed
void imageEvent(PImage m) {
  //println("movieEvent");

  for (int i=0; i < numPorts; i++) {
    // copy a portion of the image to the LED image
    int xoffset = percentage(m.width, ledArea[i].x);
    int yoffset = percentage(m.height, ledArea[i].y);
    int xwidth =  percentage(m.width, ledArea[i].width);
    int yheight = percentage(m.height, ledArea[i].height);
    ledImage[i].copy(m, xoffset, yoffset, xwidth, yheight,
                     0, 0, ledImage[i].width, ledImage[i].height);
    // convert the LED image to raw data
    byte[] ledData =  new byte[(ledImage[i].width * ledImage[i].height * 3) + 3];
    image2data(ledImage[i], ledData, ledLayout[i]);
    ledData[0] = '*';  // on image every board = masterboard (no framesync required)
    ledData[1] = 0;
    ledData[2] = 0;
    // send the raw data to the LEDs  :-)
    ledSerial[i].write(ledData);
  }
}

// image2data converts an image to OctoWS2811's raw data format.
// The number of vertical pixels in the image must be a multiple
// of 8.  The data array must be the proper size for the image.
void image2data(PImage image, byte[] data, boolean layout) {
  int offset = 3;
  int x, y, xbegin, xend, xinc, mask;
  int linesPerPin = image.height / 8;
  int pixel[] = new int[8];

  for (y = linesPerPin-1; y >= 0; y--) {
    if ((y & 1) == (layout ? 0 : 1)) {
      // even numbered rows are left to right
      xbegin = 0;
      xend = image.width;
      xinc = 1;
    } else {
      // odd numbered rows are right to left
      xbegin = image.width - 1;
      xend = -1;
      xinc = -1;
    }
    for (x = xbegin; x != xend; x += xinc) {
      for (int i=0; i < 8; i++) {
        // fetch 8 pixels from the image, 1 for each pin
        pixel[i] = image.pixels[x + (y + linesPerPin * i) * image.width];
        pixel[i] = colorWiring(pixel[i]);
      }
      // convert 8 pixels to 24 bytes
      for (mask = 0x800000; mask != 0; mask >>= 1) {
        byte b = 0;
        for (int i=0; i < 8; i++) {
          if ((pixel[i] & mask) != 0) b |= (1 << i);
        }
        data[offset++] = b;
      }
    }
  }
}

// translate the 24 bit color from RGB to the actual
// order used by the LED wiring.  GRB is the most common.
int colorWiring(int c) {
  int red = (c & 0xFF0000) >> 16;
  int green = (c & 0x00FF00) >> 8;
  int blue = (c & 0x0000FF);
  red = gammatable[red];
  green = gammatable[green];
  blue = gammatable[blue];
  return (green << 16) | (red << 8) | (blue); // GRB - most common wiring
}

// ask a Teensy board for its LED configuration, and set up the info for it.
void serialConfigure(String portName) {
  if (numPorts >= maxPorts) {
    println("too many serial ports, please increase maxPorts");
    errorCount++;
    return;
  }
  try {
    ledSerial[numPorts] = new Serial(this, portName);
    if (ledSerial[numPorts] == null) throw new NullPointerException();
    ledSerial[numPorts].write('?');
  } catch (Throwable e) {
    println("Serial port " + portName + " does not exist or is non-functional");
    errorCount++;
    return;
  }
  delay(50);
  String line = ledSerial[numPorts].readStringUntil(10);
  if (line == null) {
    println("Serial port " + portName + " is not responding.");
    println("Is it really a Teensy 3.0 running VideoDisplay?");
    errorCount++;
    return;
  }
  String param[] = line.split(",");
  if (param.length != 12) {
    println("Error: port " + portName + " did not respond to LED config query");
    errorCount++;
    return;
  }
  // only store the info and increase numPorts if Teensy responds properly
  ledImage[numPorts] = new PImage(Integer.parseInt(param[0]), Integer.parseInt(param[1]), RGB);
  ledArea[numPorts] = new Rectangle(Integer.parseInt(param[5]), Integer.parseInt(param[6]),
                     Integer.parseInt(param[7]), Integer.parseInt(param[8]));
  ledLayout[numPorts] = false;
  numPorts++;
}

void draw() {
  if (args.length == 3){
    if (myMovie.duration() == myMovie.time()){
      System.exit(0); //exit when movie is played
    }
  } else if (args.length == 4){
    if (imgTime == 0){
      imageEvent(myImage);
      imgTime = millis();
    } else if (millis() > imgTime + int(args[3]) * 1000){
      System.exit(0);
    }
  }
  
}

// scale a number by a percentage, from 0 to 100
int percentage(int num, int percent) {
  double mult = percentageFloat(percent);
  double output = num * mult;
  return (int)output;
}

// scale a number by the inverse of a percentage, from 0 to 100
int percentageInverse(int num, int percent) {
  double div = percentageFloat(percent);
  double output = num / div;
  return (int)output;
}

// convert an integer from 0 to 100 to a float percentage
// from 0.0 to 1.0.  Special cases for 1/3, 1/6, 1/7, etc
// are handled automatically to fix integer rounding.
double percentageFloat(int percent) {
  if (percent == 33) return 1.0 / 3.0;
  if (percent == 17) return 1.0 / 6.0;
  if (percent == 14) return 1.0 / 7.0;
  if (percent == 13) return 1.0 / 8.0;
  if (percent == 11) return 1.0 / 9.0;
  if (percent ==  9) return 1.0 / 11.0;
  if (percent ==  8) return 1.0 / 12.0;
  return (double)percent / 100.0;
}
```