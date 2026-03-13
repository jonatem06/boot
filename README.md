# Alpaca Trading Bot con Estrategia de Dividendos y Gestión de Riesgo

Este es un bot de trading automatizado escrito en Python que utiliza la API de Alpaca. El bot incluye análisis técnico, gestión de riesgo avanzada y una estrategia específica para la reinversión de beneficios en acciones de dividendos.

## Características

1.  **Módulo de Análisis (Inteligencia)**:
    *   Cálculo de indicadores técnicos como SMA (Media Móvil Simple) y RSI (Índice de Fuerza Relativa).
    *   Manejo de DataFrames multi-índice para múltiples activos.
    *   Ganchos (placeholders) para análisis de sentimiento mediante IA y flujo de órdenes.
2.  **Módulo de Ejecución Táctica**:
    *   Envío rápido de órdenes de mercado y límite.
    *   Optimizado para minimizar el slippage.
3.  **Módulo de Gestión de Riesgo (Equity Guardian)**:
    *   **Control de Drawdown**: Detiene las operaciones si la caída de la cuenta supera un porcentaje definido.
    *   **Stop-Loss Automático**: Protege cada posición contra pérdidas excesivas.
    *   **Dimensionamiento de Posiciones**: Limita la inversión por acción (máximo 10%) para mantener la diversidad de la cartera. Soporta la compra de **acciones fraccionadas**.
4.  **Estrategia de Dividendos**:
    *   Cuando el bot acumula un beneficio neto específico ($1000), compra automáticamente una acción de dividendos.
    *   **Mantenimiento de Liquidez**: Solo compra acciones de dividendos si queda suficiente capital (50% de equity) para seguir operando con otras acciones.
    *   **Hold Target**: Las acciones de dividendos no se venden hasta que generen al menos un 50% de ganancia.
5.  **Memoria y Persistencia**:
    *   Logueo detallado en una base de datos SQLite (`trade`).
    *   Registra: Saldo antes/después, costo, símbolo, porcentaje, tipo de movimiento (BUY/SELL) y beneficio.
    *   Recupera el estado de las posiciones y el beneficio acumulado al reiniciarse.

## Estructura del Proyecto

*   `bot/config.py`: Configuración global y manejo de variables de entorno.
*   `bot/broker.py`: Integración con la API de Alpaca (balance, posiciones).
*   `bot/analysis.py`: Lógica de indicadores y generación de señales.
*   `bot/execution.py`: Gestión de órdenes de compra y venta.
*   `bot/risk_management.py`: Equity Guardian (drawdown, stop-loss, sizing).
*   `bot/strategy.py`: Orquestación de la estrategia principal y dividendos.
*   `bot/logger.py`: Persistencia en base de datos SQLAlchemy/SQLite.
*   `bot/main.py`: Punto de entrada del bot.

## Requisitos Previos

*   Python 3.10+
*   Cuenta en Alpaca (Paper o Live).

## Instalación

1. Clonar el repositorio.
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Crear un archivo `.env` en la raíz del proyecto con el siguiente formato:
   ```env
   TRADING_MODE=PAPER  # O 'LIVE'

   ALPACA_PAPER_API_KEY=tu_key_aqui
   ALPACA_PAPER_SECRET_KEY=tu_secret_aqui

   ALPACA_LIVE_API_KEY=tu_key_aqui
   ALPACA_LIVE_SECRET_KEY=tu_secret_aqui
   ```

## Uso

Para iniciar el bot:
```bash
python bot/main.py
```

Para ejecutar los tests de lógica:
```bash
export PYTHONPATH=$PYTHONPATH:.
python3 -m unittest discover tests
```

## Configuración de Estrategia

Puedes ajustar los parámetros de riesgo y estrategia en `bot/config.py`:
*   `MAX_POSITION_PERCENT`: Porcentaje máximo de la cartera por acción.
*   `MAX_DRAWDOWN_PERCENT`: Caída máxima permitida antes de detener el bot.
*   `ALLOW_FRACTIONAL_SHARES`: Permite comprar fracciones de acciones (ej. 0.5 acciones).
*   `DIVIDEND_REINVEST_THRESHOLD`: Beneficio necesario para comprar una acción de dividendos.
*   `DIVIDEND_HOLD_PROFIT_TARGET`: Objetivo de ganancia (1.5 = 50%) para vender acciones de dividendos.
