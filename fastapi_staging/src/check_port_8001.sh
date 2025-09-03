[0;1;31m●[0m fastapi.service - SMC Tracker FastAPI Backend
   Loaded: loaded (/etc/systemd/system/fastapi.service; enabled; vendor preset: disabled)
   Active: [0;1;31mfailed[0m (Result: exit-code) since Fri 2025-08-22 12:03:05 PKT; 8min ago
  Process: 1277713 ExecStart=/opt/smc_v2/env/bin/uvicorn apps.fastapi_app:app --host 0.0.0.0 --port 8001 --workers 4 [0;1;31m(code=exited, status=1/FAILURE)[0m
 Main PID: 1277713 (code=exited, status=1/FAILURE)

Aug 22 12:03:05 smcv2.eoc.gov.pk systemd[1]: fastapi.service: Service RestartSec=100ms expired, scheduling restart.
Aug 22 12:03:05 smcv2.eoc.gov.pk systemd[1]: fastapi.service: Scheduled restart job, restart counter is at 5.
Aug 22 12:03:05 smcv2.eoc.gov.pk systemd[1]: Stopped SMC Tracker FastAPI Backend.
Aug 22 12:03:05 smcv2.eoc.gov.pk systemd[1]: [0;1;39m[0;1;31m[0;1;39mfastapi.service: Start request repeated too quickly.[0m
Aug 22 12:03:05 smcv2.eoc.gov.pk systemd[1]: [0;1;39m[0;1;31m[0;1;39mfastapi.service: Failed with result 'exit-code'.[0m
Aug 22 12:03:05 smcv2.eoc.gov.pk systemd[1]: [0;1;31m[0;1;39m[0;1;31mFailed to start SMC Tracker FastAPI Backend.[0m
