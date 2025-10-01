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
