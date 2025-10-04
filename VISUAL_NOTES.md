# Visual improvements (UI)

Recent UI updates improve readability and controls:

- Dark theme refined with softened contrast and card-style panels.
- Larger, higher-contrast icons (32x32) and outline primary buttons so icons stand out.
- Stop button shows an icon-only control with a tooltip to avoid icon/color clash.
- Servo debug is available as a dockable panel via the toolbar (Tools → Servo Debug).
- RPM graph now shows a subtle grid and larger labels for readability.
- A smoothing control (Smoothing spinner) was added to adjust graph smoothing in real time.

How to test these changes:

1. Start the app: `python main.py`
2. Toggle Tools → Servo Debug to open the dockable servo panel.
3. Use the Smoothing spinner to change the graph smoothing window.
4. Observe the LED indicator: it pulses when the obstacle sensor state is ON.

