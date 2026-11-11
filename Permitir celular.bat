@echo off
REM Doble clic una sola vez para que el celular pueda entrar al asistente (pide permiso de administrador).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0permitir_celular.ps1"
