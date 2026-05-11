# BOOTSTRAP_MULTI_EQUIPO.md

## Proposito

Guia para que multiples equipos o miembros puedan clonar, rehidratar y validar el orquestador local `C:\Agente` en distintas maquinas, con rutas locales distintas, sin versionar configuracion personal ni secretos.

---

## 1. Clonar o rehidratar

```powershell
# Clonar desde GitHub (reemplazar <repo-url> por la URL real)
git clone <repo-url> <AGENTE_ROOT>
cd <AGENTE_ROOT>
```

`<AGENTE_ROOT>` es la ruta local donde se ubica el repositorio en cada maquina. Ejemplos:

- `C:\Agente`
- `D:\dev\agente-local-orchestrator`
- `C:\Users\alice\projects\orquestador`

Todas las rutas en este documento usan `<AGENTE_ROOT>` como placeholder. Cada equipo debe reemplazarlo por su ruta real.

---

## 2. Prerrequisitos instalables

| Herramienta | Version minima | Notas |
|---|---|---|
| Git | 2.30+ | `git --version` |
| Python | 3.10+ | `python --version` |
| VS Code | 1.85+ | `code --version` |
| Continue | ultima estable | Extension VS Code |
| OpenCode CLI | segun docs oficiales | `opencode.cmd --version` |

No se incluyen valores de secrets, tokens ni variables de entorno en esta guia. Cada equipo debe configurar sus propios valores en `.env` local (no versionado).

---

## 3. Configurar Continue MCP

> **Nota:** La configuracion exacta depende de la version instalada de Continue. Este es un procedimiento best-effort.

### 3.1 Referencias

- `mcp_server/README.md` — documentacion tecnica del servidor MCP
- `docs/protocols/MCP_CONTINUE_INTEGRATION_PROTOCOL.md` — protocolo de integracion

### 3.2 Comando del servidor

El servidor MCP se ejecuta con:

```powershell
python <AGENTE_ROOT>\mcp_server\server.py
```

Agregar esta entrada en la configuracion de Continue (`.continue/config.json` o la UI de configuracion segun la version):

```json
{
  "experimental": {
    "mcpServers": {
      "agente-local-orchestrator": {
        "command": "python",
        "args": ["<AGENTE_ROOT>\\mcp_server\\server.py"]
      }
    }
  }
}
```

Reemplazar `<AGENTE_ROOT>` por la ruta local real.

> **Importante:** No versionar `.continue/config.json` ni ninguna configuracion personal de Continue. Cada miembro del equipo debe configurarlo localmente.

---

## 4. Validar la instalacion

Ejecutar en orden:

### 4.1 Portabilidad

```powershell
cd <AGENTE_ROOT>
python .\scripts\check_portability.py --output json
```

### 4.2 Estado operativo

```powershell
python .\mcp_server\tools.py --self-test
```

### 4.3 Validacion stdio del servidor MCP

```powershell
python .\mcp_server\test_mcp_stdio.py
```

### 4.4 Checks locales rapidos

```powershell
python .\scripts\run_local_checks.py --mode quick
```

### 4.5 Checks locales completos

```powershell
python .\scripts\run_local_checks.py --mode full --include-git-status
```

---

## 5. Manejo de rutas locales distintas

Cada maquina puede tener el repositorio en una ruta distinta.

Reglas:

1. **Usar placeholders en documentacion compartida:** `<AGENTE_ROOT>` en lugar de rutas absolutas.
2. **No hardcodear rutas absolutas** en scripts de validacion o configuracion.
3. **Los scripts del orquestador** (en `scripts/`) intentan detectar la raiz del repositorio automaticamente. Si fallan, usar `--root` flag:

```powershell
python .\scripts\check_portability.py --output json --root <AGENTE_ROOT>
```

4. **Configuracion de Continue MCP:** cada miembro debe ajustar la ruta en su configuracion local.

---

## 6. Manejo de registries por maquina

El archivo `PROJECT_REGISTRY.md` centraliza los proyectos del orquestador, pero **no debe versionarse** contenido generado localmente por maquina.

Para registros locales por maquina:

1. Crear un archivo fuera del repositorio:

   ```powershell
   # En PowerShell
   $HOME\project_registry_local.md
   
   # O en TEMP
   $env:TEMP\project_registry_local.md
   ```

2. Usar el flag `--registry-path` en los scripts que lo soporten:

   ```powershell
   python .\scripts\some_script.py --registry-path "$HOME\project_registry_local.md"
   ```

3. **No versionar** estos archivos locales. Agregar la ruta elegida a `.gitignore` del usuario si fuera necesario.

---

## 7. Que nunca versionar

Los siguientes archivos y directorios **no deben** incluirse en commits:

| Elemento | Motivo |
|---|---|
| `.env` / `.env.*` | Secrets, tokens, credenciales |
| `.continue/config.json` y `.continue/` personal | Config IDE local, API keys de modelos |
| `.vscode/settings.json` personal | Preferencias de editor por maquina |
| `opencode.json` / `opencode.config.example.json` | Config local de OpenCode |
| `docs/agent_runs/**` | Evidencia operacional generada por ejecuciones |
| `docs/agent_queue/**` | Handoffs en cola (temporales) |
| `raw_outputs/**` | Salidas crudas de modelos |

Si se incluye alguno por error, usar `git rm --cached` y agregar a `.gitignore`.

---

## 8. Resumen de comandos utiles

```powershell
# Clonar
git clone <repo-url> <AGENTE_ROOT>

# Validar portabilidad
python .\scripts\check_portability.py --output json

# Test de portabilidad
python .\scripts\test_check_portability.py

# Validar servidor MCP
python .\mcp_server\tools.py --self-test
python .\mcp_server\test_mcp_stdio.py

# Checks locales
python .\scripts\run_local_checks.py --mode quick
python .\scripts\run_local_checks.py --mode full --include-git-status

# Ver estado de git
git status
git diff --name-only
```
