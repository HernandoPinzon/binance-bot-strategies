# Uso de `tmux` para ejecutar el bot de trading en AWS

## 1️⃣ Instalar `tmux` (si no lo tienes)
```bash
sudo apt update && sudo apt install tmux -y
sudo pacman -S tmux
```

## 2️⃣ Iniciar una nueva sesión de `tmux` y correr el bot
```bash
tmux new -s bot
```
Dentro de `tmux`, ejecuta tu bot:
```bash
python3 /ruta/a/tu/bot.py >> /ruta/a/logs/bot.log 2>&1
```

## 3️⃣ Salir de `tmux` sin detener el bot
Presiona:

- `Ctrl + B`, luego suelta y presiona `D`

Tu bot seguirá corriendo en segundo plano.

## 4️⃣ Volver a la sesión del bot
Cuando vuelvas a conectarte por SSH, reanuda la sesión con:

```bash
tmux attach -t bot
```

Si tienes varias sesiones y no recuerdas el nombre:
```bash
tmux ls
```
Luego, para reanudar una sesión específica:
```bash
tmux attach -t nombre_de_sesion
```

## 5️⃣ Ver logs en tiempo real (opcional)
Si solo quieres ver los logs sin entrar a `tmux`:
```bash
tail -f /ruta/a/logs/bot.log
```

## 6️⃣ Matar la sesión del bot (cuando quieras detenerlo)
```bash
tmux kill-session -t bot
```

Con esto, tu bot seguirá corriendo aunque cierres la terminal SSH, y podrás volver a verlo cuando quieras. 🚀

---

# Diferencias entre `tmux` y `systemd`

### Comparación clave

| Característica        | `tmux`                                         | `systemd`                                    |
|----------------------|--------------------------------|--------------------------------|
| **Persistencia**      | Se mantiene solo mientras la sesión de `tmux` existe. | Se reinicia automáticamente si falla o se reinicia el sistema. |
| **Autoinicio**        | No, debes iniciar la sesión manualmente. | Sí, puede iniciarse al arrancar la máquina. |
| **Monitoreo**         | Manual (debes entrar a `tmux` para ver qué pasa). | Automático (`systemctl status bot.service`). |
| **Facilidad de uso**  | Simple para ejecutar procesos interactivos. | Mejor para procesos en segundo plano. |
| **Logs**             | Debes redirigir la salida a un archivo manualmente. | Guarda los logs automáticamente con `journalctl`. |

### Diferencias de rendimiento
- `tmux` y `systemd` apenas consumen recursos por sí solos.
- La diferencia principal es que **`systemd` maneja mejor fallos y reinicios**, mientras que `tmux` es más interactivo.
- `tmux` es útil si quieres **ver la ejecución del bot en vivo**, como si lo hubieras minimizado.
- `systemd` es mejor si necesitas que el bot **se inicie automáticamente y se recupere tras fallos o reinicios**.

### 📌 **Conclusión**
Si solo quieres mantener el bot corriendo y poder verlo en vivo cuando te conectes, **`tmux` es suficiente**.  
Si quieres algo más robusto que se ejecute al reiniciar y se recupere solo, **usa `systemd`**.  

🚀 **Mejor solución**: **Usar ambos**. Puedes iniciar el bot con `systemd` y luego usar `tmux` para inspeccionarlo cuando lo necesites.
