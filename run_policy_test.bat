@echo off
setlocal enabledelayedexpansion

:: Configurazione
set TARGET_IP=192.168.200.10
set ROUTER_IP=192.168.200.254
set ROUTER_API=http://%ROUTER_IP%:5000
set NUM_SCANS=3
set PORTS_PER_SCAN=15
set MONITOR_DURATION=300

echo === TEST POLICY DI SICUREZZA ZERO TRUST ===
echo Target IP: %TARGET_IP%
echo Router API: %ROUTER_API%

:: Verifica che il router sia in esecuzione
echo.
echo Verifica connettività router...
curl -s "%ROUTER_API%/health" > nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ Router raggiungibile
) else (
    echo ✗ Router non raggiungibile. Verificare che il container sia in esecuzione
    exit /b 1
)

:: Recupera stato iniziale degli IP bloccati
echo.
echo Recupero stato iniziale...
for /f "tokens=*" %%a in ('curl -s "%ROUTER_API%/blocked-ips" ^| findstr "count"') do set BLOCKED_INFO=%%a
echo %BLOCKED_INFO%

:: Verifica se l'IP target è già bloccato
curl -s "%ROUTER_API%/blocked-ips" | findstr "%TARGET_IP%" > nul
if %ERRORLEVEL% EQU 0 (
    echo ⚠ Il target IP %TARGET_IP% risulta già bloccato, sbloccandolo per il test...
    curl -s -X POST -H "Content-Type: application/json" -d "{\"ip\":\"%TARGET_IP%\",\"action\":\"unblock\"}" "%ROUTER_API%/enforce" > nul
)

:: Verifica che il server Splunk sia in esecuzione
echo.
echo Verifica Splunk...
docker exec splunk ps aux | findstr "splunkd" > nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ Splunk è in esecuzione
) else (
    echo ✗ Splunk non sembra essere in esecuzione. Verificare il container 'splunk'
    exit /b 1
)

:: Verifica che Squid sia configurato correttamente nel router
echo.
echo Verifica Squid...
docker exec router ps aux | findstr "squid" > nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ Squid è in esecuzione
) else (
    echo ✗ Squid non sembra essere in esecuzione. Verificare il container 'router'
    exit /b 1
)

:: Verifica che Snort sia configurato correttamente nel router
echo.
echo Verifica Snort...
docker exec router ps aux | findstr "snort" > nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ Snort è in esecuzione
) else (
    echo ✗ Snort non sembra essere in esecuzione. Verificare il container 'router'
    exit /b 1
)

:: Avvia il monitoraggio in background
echo.
echo Avvio monitoraggio policy...
start /b docker exec router python3 /router/api/monitor_policy.py -t "%TARGET_IP%" -d "%MONITOR_DURATION%"

:: Attendi un momento per assicurarti che il monitoraggio sia avviato
timeout /t 3 > nul

:: Genera eventi di port scanning
echo.
echo Generazione eventi port scanning verso %TARGET_IP%...
echo Esecuzione di %NUM_SCANS% batch di %PORTS_PER_SCAN% connessioni ciascuno

:: Esegui da un container client per essere nella stessa rete
docker exec client-internal python3 -c "import socket; import time; import random; def scan_port(ip, port, timeout=0.5): s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(timeout); try: s.connect((ip, port)); s.close(); return True; except: s.close(); return False; target = '%TARGET_IP%'; num_scans = %NUM_SCANS%; ports_per_scan = %PORTS_PER_SCAN%; print(f'Avvio scansione: {num_scans} batch con {ports_per_scan} porte per batch'); for batch in range(num_scans): print(f'Batch {batch+1}/{num_scans}'); for i in range(ports_per_scan): port = random.randint(1, 65535); result = 'aperta' if scan_port(target, port) else 'chiusa'; print(f'Scansione porta {port}: {result}'); time.sleep(0.2); if batch < num_scans - 1: print('Pausa tra i batch...'); time.sleep(5); print('Scansione completata');"

:: Attendi che il monitoraggio completi
echo.
echo Eventi generati. Monitoraggio in corso...
echo Il monitoraggio terminerà automaticamente tra %MONITOR_DURATION% secondi
echo Puoi controllare i log di Splunk e del router per verificare l'elaborazione degli eventi

:: Suggerimenti
echo.
echo Suggerimenti per verificare il funzionamento:
echo 1. Verifica i log Snort: docker exec router cat /var/log/snort/alert
echo 2. Verifica punteggi di fiducia: curl %ROUTER_API%/trust-scores
echo 3. Verifica IP bloccati: curl %ROUTER_API%/blocked-ips
echo 4. Accedi a Splunk Web: http://localhost:8000

:: Attesa per il completamento del monitoraggio
timeout /t %MONITOR_DURATION% > nul

:: Verifica finale
echo.
echo Verifica finale dello stato...
for /f "tokens=*" %%a in ('curl -s "%ROUTER_API%/blocked-ips" ^| findstr "count"') do set FINAL_BLOCKED=%%a

curl -s "%ROUTER_API%/blocked-ips" | findstr "%TARGET_IP%" > nul
set TARGET_BLOCKED=%ERRORLEVEL%

echo === RISULTATI FINALI ===
echo %BLOCKED_INFO%
echo %FINAL_BLOCKED%

if %TARGET_BLOCKED% EQU 0 (
    echo ✓ TEST SUPERATO: L'IP target %TARGET_IP% è stato bloccato!
    
    :: Ottieni i dettagli dal sistema di fiducia
    echo Dettagli punteggio di fiducia:
    curl -s "%ROUTER_API%/trust-scores" | findstr /C:"%TARGET_IP%" /C:"current_score" /C:"block_reason"
) else (
    echo ✗ TEST FALLITO: L'IP target %TARGET_IP% NON è stato bloccato
    echo Possibili motivi:
    echo 1. Gli eventi generati non sono stati sufficienti per attivare la policy
    echo 2. Splunk non ha elaborato gli alert in tempo
    echo 3. Il webhook non è stato configurato correttamente
    echo 4. La policy non è stata implementata correttamente
    
    echo.
    echo Controlla i log per maggiori dettagli:
    echo - Router logs: docker exec router cat /var/log/router/policy_enforcer.log
    echo - Splunk saved searches: Splunk Web -^> Settings -^> Searches, reports, and alerts
    echo - Snort alerts: docker exec router cat /var/log/snort/alert
)

echo.
echo Test completato!