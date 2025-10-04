# Diagrama de Conexiones del Hardware

Este documento detalla las conexiones eléctricas entre el Arduino Uno, el driver L298N y el motor Pololu 37D con encoder, después de la simplificación del código para eliminar el control de dirección.

### 1. Alimentación Principal (Externa)

| Componente Origen | Pin/Terminal Origen | Componente Destino | Pin/Terminal Destino | Nota                               |
|-------------------|---------------------|--------------------|----------------------|------------------------------------|
| Fuente Externa    | Positivo (+)        | L298N              | VCC / +12V           | Usar el voltaje requerido por el motor |
| Fuente Externa    | Negativo (-)        | L298N              | GND                  |                                    |

### 2. Lógica de Control (Arduino y L298N)

| Componente Origen | Pin/Terminal Origen | Componente Destino | Pin/Terminal Destino | Propósito                          |
|-------------------|---------------------|--------------------|----------------------|------------------------------------|
| Arduino Uno       | GND                 | L298N              | GND                  | **Crítico:** Tierra común entre ambos      |
| Arduino Uno       | Pin 11 (PWM `~`)    | L298N              | ENA                  | Control de Velocidad del motor     |
| L298N             | 5V                  | L298N              | IN1                  | Fija la dirección (estado HIGH)    |
| L298N             | GND                 | L298N              | IN2                  | Fija la dirección (estado LOW)     |

### 3. Salida de Potencia al Motor

| Componente Origen | Cable Origen | Componente Destino | Pin/Terminal Destino |
|-------------------|--------------|--------------------|----------------------|
| Motor Pololu 37D  | Rojo (+)     | L298N              | OUT1                 |
| Motor Pololu 37D  | Negro (-)    | L298N              | OUT2                 |

### 4. Conexión del Encoder (Motor a Arduino)

| Componente Origen | Cable Origen      | Componente Destino | Pin/Terminal Destino | Propósito                          |
|-------------------|-------------------|--------------------|----------------------|------------------------------------|
| Motor Pololu 37D  | Amarillo (Canal A)| Arduino Uno        | Pin 2                | Lectura de RPM (Pin de Interrupción) |
| Motor Pololu 37D  | Azul (VCC)        | Arduino Uno        | 5V                   | Alimentación para el encoder       |
| Motor Pololu 37D  | Verde (GND)       | Arduino Uno        | GND                  | Tierra para el encoder             |
| Motor Pololu 37D  | Blanco (Canal B)  | -                  | -                    | No se utiliza en esta configuración|

### 5. Conexión del Servomotor de Clasificación

El servomotor se utiliza para desviar los objetos clasificados a diferentes contenedores.

| Componente Origen | Pin/Terminal Origen | Componente Destino | Pin/Terminal Destino | Propósito                          |
|-------------------|---------------------|--------------------|----------------------|------------------------------------|
| Servomotor        | Cable de Señal (Naranja/Amarillo) | Arduino Uno        | Pin 10 (PWM `~`)     | Control de posición del servo      |
| Servomotor        | Cable de VCC (Rojo) | Arduino Uno        | 5V                   | Alimentación para el servo         |
| Servomotor        | Cable de GND (Marrón/Negro) | Arduino Uno        | GND                  | Tierra para el servo               |

#### Códigos de Posición del Servo

El firmware del Arduino responde a códigos numéricos enviados desde la aplicación de Python para mover el servo a posiciones predefinidas. Estas posiciones corresponden a las diferentes categorías de clasificación.

| Código | Posición (Ángulo) | Categoría (Forma) | Categoría (Color) | Categoría (Tamaño) |
|--------|-------------------|-------------------|-------------------|--------------------|
| `0`    | 30°               | Triángulo         | Rojo              | Pequeño            |
| `1`    | 90°               | Cuadrado          | Amarillo          | Mediano            |
| `2`    | 150°              | Círculo           | Verde             | Grande             |
| `9`    | 0°                | Desconocido       | Desconocido       | Desconocido        |

**Nota:** El código `9` (Desconocido) es manejado por el caso `default` en el firmware y corresponde a la posición de reposo o inicial. Los valores de los ángulos son aproximados y deben ser calibrados físicamente para un rendimiento óptimo.

### 6. Conexión del Sensor IR de Obstáculos

El sensor infrarrojo se utiliza para detectar la presencia de objetos en la banda transportadora y activar el proceso de clasificación por visión computacional.

| Componente Origen | Pin/Terminal Origen | Componente Destino | Pin/Terminal Destino | Propósito                          |
|-------------------|---------------------|--------------------|----------------------|------------------------------------|
| Sensor IR         | VCC                 | Arduino Uno        | 5V                   | Alimentación del sensor            |
| Sensor IR         | GND                 | Arduino Uno        | GND                  | Tierra del sensor                  |
| Sensor IR         | OUT (Señal)         | Arduino Uno        | Pin 7                | Señal digital de detección         |

#### Configuración del Sensor IR

- **Pin configurado:** Pin 7 (Digital)
- **Modo:** `INPUT_PULLUP` (utiliza la resistencia pull-up interna del Arduino)
- **Lógica de detección:** 
  - `LOW` (0V) = Objeto detectado (sensor activado)
  - `HIGH` (5V) = No hay objeto (sensor inactivo)
- **Trigger:** El sistema usa detección por "rising edge" - la clasificación se inicia cuando el sensor pasa de no detectar a detectar un objeto

#### Funcionamiento

1. El sensor IR emite continuamente un haz infrarrojo
2. Cuando un objeto interrumpe el haz, la salida del sensor cambia a `LOW`
3. El Arduino detecta este cambio y notifica a la aplicación Python
4. La aplicación Python inicia el proceso de clasificación por visión computacional
5. Una vez clasificado, el servo mueve el objeto al contenedor correspondiente

**Nota Técnica:** El sensor utiliza lógica invertida (LOW = objeto presente) debido a la configuración típica de los sensores IR de obstáculos. La resistencia pull-up interna mantiene la señal en HIGH cuando no hay objetos presentes.