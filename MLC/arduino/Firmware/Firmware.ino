
#define DEBUG 1

#ifdef DEBUG
#define LOG(x,y) Serial.print(x); Serial.println(y);
#endif

// defines ahorran ROM... aunque nos sobra de eso XD -- Verificar que los const vayan a la rom!
const uint8_t ANALOG_PRECISION_CMD  = 0x01;
const uint8_t ADD_ANALOG_INPUT_CMD  = 0x02;
const uint8_t ADD_ANALOG_OUTPUT_CMD = 0x03;
const uint8_t SET_PIN_MODE_CMD      = 0x04;
const uint8_t SET_REPORT_MODE_CMD   = 0x05;
const uint8_t ACTUATE_CMD           = 0xF0;

// Commands executor caller -- one vector position == one command
void (*executor[255])(const char*);

void not_implemented(const char* data)
{
  //nothing to do...
  return;
}

typedef enum ReportModes {average, bulk, rt};

/** ---------------------------------------------------------- **/
/** GLOBAL CONFIG **/

uint8_t REPORT_READ_COUNT = 0;
uint8_t REPORT_READ_DELAY = 0;
ReportModes REPORT_MODE = average;
uint8_t INPUT_PORTS[129]; // Port count in first position

/** ---------------------------------------------------------- **/

const char* ACK = "\xFF\x00";

/**
   ANALOG_PRECISION: 0x01 0x01 [BITS]
*/
void set_analog_precision(const char* data)
{
  int i = byte(data[2]);
  // Tal vez conviene separar estas funciones ya que hay boards con resoluciones distintas...
  // Igual, así funciona bien con el due (y con todos, ya que no hay problema en superar el máximo de la resolución)
  analogWriteResolution(i);
  analogReadResolution(i);

  LOG("Resolution changed to: ", i);
}

/**
   PIN_MODE: 0x04 0x02 [PIN] [MODE]
*/
void set_pin_mode(const char* data)
{
  pinMode(data[2], data[3]);
  LOG("Changed pin mode on pin ", data[2]);
  LOG("Mode set to ", data[3]);
}

/**
   REPORT_MODE: 0x05 0x03 [MODE] [READ_COUNT] [READ_DELAY]
*/
void set_report_mode(const char* data)
{
  REPORT_MODE = (ReportModes)(data[2]);
  REPORT_READ_COUNT = byte(data[3]);
  REPORT_READ_DELAY = byte(data[4]);
  LOG("Report mode changed on port ", byte(data[3]));
}

/**
   ANALOG_INPUT: 0x02 0x01 [PORT]
*/
void set_analog_input(const char* data)
{
  INPUT_PORTS[0] += 1;
  INPUT_PORTS[INPUT_PORTS[0]] = byte(data[2]);
  LOG("New analog input: ", byte(data[2]));
}

/**
 * ANALOG_OUTPUT: 0x03 0x01 [PORT]
 */
void set_analog_output(const char* data)
{
  // No se si vale la pena guardar registro de pines de salida...
}

/**
 * ACTUATE: 0xF0 [PIN_COUNT] [PIN_A] [VALUE_PIN_A] ... [PIN_N] [VALUE_PIN_N]
 */
void actuate(const char* data)
{
  int offset = 0;
  int byte_count = byte(data[1]); // Un byte puede llegar a limitar la cantidad de salidas... creo

  // ACTUATION ZONE
  while (offset > byte_count)
  {
    //Se aplica la acción a cada puerto indicado
    int port = byte(data[2 + offset]);

    //Detects an analog port
    if ( port >= A0 )
    {
      int value = (data[3 + offset] << 8) + data[4 + offset];
      analogWrite(port, value);
      offset += 3;

      LOG("Analog pin written", port);
    } else
    {
      int value = data[3 + offset] > 0 ? HIGH : LOW; // Creo que da igual si pongo el entero directamente
      digitalWrite(port, value);
      offset += 2;

      LOG("Digital pin written ", port);
    }
  }

  delayMicroseconds(REPORT_READ_DELAY); // FIXME: Usamos variable de 8 bits cuando la precisión de esta función llega a 16 bits.

  char response[130];
  response[0] = '\xF1';
  byte len = 1;  // Inicia en 1 para evitar pisar el id de comando
  for (int i = 1; i <= byte(INPUT_PORTS[0]); i++)
  {
    if ( INPUT_PORTS[i] >= A0 )
    {
      int data = analogRead(INPUT_PORTS[i]);
      response[len + 1] = byte((data & 0xFF00) >> 8); // Se guarda el msb en el buffer
      response[len + 2] = byte(data & 0xFF);        // Se guarda el lsb en el buffer

      len += 2; // Cada lectura de un recurso analógico ocupa dos bytes. FIXME: se puede optimizar con bajas resoluciones
      LOG("Analog pin read: ", INPUT_PORTS[i]);
    } else
    {
      int data = digitalRead(INPUT_PORTS[i]);
      response[len + 1] = byte(data);

      len += 1;
      LOG("Digital pin read: ", INPUT_PORTS[i]);
    }
  }

  response[1] = len - 1;
  SerialUSB.write(response, len + 2); // 2 bytes extras por el id de comando y la longitud
}

void setup() {
  SerialUSB.begin(115200);
  
  #ifdef DEBUG
  Serial.begin(57600);
  #endif
  
  for (int i = 0; i < 255; i++)
  {
    executor[i] = &not_implemented;
  }

  INPUT_PORTS[0] = 0;

  /**  Commands Callbacks  **/
  executor[ANALOG_PRECISION_CMD]  = &set_analog_precision;
  executor[ADD_ANALOG_INPUT_CMD]  = &set_analog_input;
  executor[ADD_ANALOG_OUTPUT_CMD] = &set_analog_output;
  executor[SET_PIN_MODE_CMD]      = &set_pin_mode;
  executor[SET_REPORT_MODE_CMD]   = &set_report_mode;
  executor[ACTUATE_CMD]           = &actuate;

  executor[ANALOG_PRECISION_CMD]("\x01\x01\x12");
  executor[ADD_ANALOG_INPUT_CMD]("\x02\x01\x37"); // Configura a A1 como lectura
  executor[ADD_ANALOG_INPUT_CMD]("\x02\x01\x38"); // Configura a A2 como lectura
  executor[SET_PIN_MODE_CMD]("\x04\x02\x12\x01");
  executor[SET_PIN_MODE_CMD]("\x04\x02\x55\x00");

}

void loop() {
  LOG("Escribiendo...", " ");
  executor[ACTUATE_CMD]("\xF0\x01\x12\x01");

  if (SerialUSB.available() > 0)
  {
    char input[64]; // Esto se reserva en el stack, tal vez hacerlo global consume menos recursos...

    while (SerialUSB.available() > 0)
    {
      SerialUSB.readBytes(input, SerialUSB.available());
    }

    executor[input[0]](input); // Does the callback for the command
  }

  delay(5000);
}
